import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { chromium } from "playwright";

function ts() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  return (
    d.getFullYear() +
    pad(d.getMonth() + 1) +
    pad(d.getDate()) +
    "-" +
    pad(d.getHours()) +
    pad(d.getMinutes()) +
    pad(d.getSeconds())
  );
}

function mkdirp(p) {
  fs.mkdirSync(p, { recursive: true });
}

function writeJson(p, obj) {
  fs.writeFileSync(p, JSON.stringify(obj, null, 2));
}

function writeText(p, s) {
  fs.writeFileSync(p, s);
}

function extractGuildAndChannel(urlStr) {
  try {
    const u = new URL(urlStr);
    const m = u.pathname.match(/^\/channels\/(\d+)\/(\d+)/);
    if (!m) return null;
    return { guildId: m[1], channelId: m[2] };
  } catch {
    return null;
  }
}

function cleanChannelName(s) {
  return (s || "")
    .replace(/（文字频道）/g, "")
    .replace(/（频道）/g, "")
    .replace(/^未读，/g, "")
    .trim();
}

function guessLang(text) {
  if (!text) return "unknown";
  // Heuristic: detect dominant script, not just presence.
  const cjk = (text.match(/[\u4e00-\u9fff]/g) || []).length;
  const cyr = (text.match(/[\u0400-\u04FF]/g) || []).length;
  const hiraKata = (text.match(/[ぁ-んァ-ン]/g) || []).length;
  const hangul = (text.match(/[가-힣]/g) || []).length;
  const latin = (text.match(/[A-Za-z]/g) || []).length;

  const max = Math.max(cjk, cyr, hiraKata, hangul, latin);
  if (max === 0) return "unknown";
  if (max === cyr) return "ru";
  if (max === hiraKata) return "ja";
  if (max === hangul) return "ko";
  if (max === cjk) return "zh";
  // Default to English for Latin script.
  if (max === latin) return "en";

  if (/[\u0400-\u04FF]/.test(text)) return "ru";
  if (/[ぁ-んァ-ン]/.test(text)) return "ja";
  if (/[가-힣]/.test(text)) return "ko";
  if (/[àâçéèêëîïôùûüÿœæ]/i.test(text)) return "fr";
  if (/[ăâîșț]/i.test(text)) return "ro";
  if (/[áéíóúñü]/i.test(text)) return "es";
  return "en";
}

function classifyDisappointment(text) {
  const raw = text || "";
  const t = raw.toLowerCase();
  const hit = [];

  const add = (theme, re) => {
    if (re.test(t)) hit.push(theme);
  };

  // English
  add("shipping/delivery", /\b(where is my phone|when (?:do|will) (?:i|get|we get) (?:my|the) phone|send my phone|delivery|shipping|tracking)\b/);
  // Only count claim/reward when it's framed as a problem/question, not generic instructions.
  add(
    "claim/rewards",
    /\b((?:how|why|what|where|when)\b.*\b(claim|founder pass|pass|oys|airdrop|reward|points?)\b|\b(can't|cannot|failed|fail|error|issue|missing|only)\b.*\b(claim|founder pass|oys|airdrop|reward|points?)\b|\b(claim|founder pass|oys)\b.*\b(can't|cannot|failed|missing|only)\b)/i
  );
  add("lack of updates", /\b(no update|silence|any news|important news|what's new|update\?)\b/);
  add("product/app broken", /\b(bug|broken|doesn'?t work|can't|cannot|error|issue|problem)\b/);
  add("value/expectations", /\b(nothing (?:to|we can) claim|what kind of project is this|scam|rug)\b/);
  add("support", /\b(support|ticket|not responding|reply)\b/);

  // Chinese (same string, not lowercased relevance)
  const zh = raw;
  if (/发货|什么时候发|还没到|物流|快递|我的.*(手机|phone)/.test(zh)) hit.push("shipping/delivery");
  // Problem-framed claim issues.
  if (/(怎么领|怎么(领|连)|领取.*(失败|不到账|少了|不对)|连不上|一直失败|积分.*(少|不对)|空投.*(麻了|不到账|少)|founder.*(少|不对)|OYS.*(少|不对)|claim.*(失败|不了|不行)|没上链)/i.test(zh))
    hit.push("claim/rewards");
  if (/没消息|没更新|有啥进展|最近.*新闻|公告.*(呢|没)/i.test(zh)) hit.push("lack of updates");
  if (/坏了|不能用|出问题|bug|报错|卡住/i.test(zh)) hit.push("product/app broken");
  if (/失望|骗子|割韭菜|垃圾/i.test(zh)) hit.push("value/expectations");
  if (/客服|工单|ticket|不回复/i.test(zh)) hit.push("support");

  // Russian (tiny)
  if (/[\\u0400-\\u04FF]/.test(text || "")) {
    const r = (text || "").toLowerCase();
    if (/где.*телефон|когда.*телефон|доставка/.test(r)) hit.push("shipping/delivery");
    if (/клейм|claim|пасс|oys|награда/.test(r)) hit.push("claim/rewards");
    if (/нет.*новост|обновлен/.test(r)) hit.push("lack of updates");
  }

  const uniq = Array.from(new Set(hit));
  return uniq.length ? uniq : null;
}

async function waitForDiscord(page) {
  await page.waitForSelector('[aria-label="频道"]', { timeout: 60_000 });
  await page.waitForTimeout(800);
}

async function getGuildName(page) {
  return await page.evaluate(() => {
    // Prefer an element that exposes the guild name via aria-label.
    const ariaEl = Array.from(document.querySelectorAll("[aria-label]")).find((e) => {
      const a = (e.getAttribute("aria-label") || "").trim();
      return a.endsWith("(服务器)") || a.endsWith("（服务器）") || /\\bserver\\b/i.test(a);
    });
    const aria = (ariaEl?.getAttribute("aria-label") || "").trim();
    if (aria) {
      return aria
        .replace(/\\s*[（(]服务器[）)]\\s*$/, "")
        .replace(/\\s*server\\s*$/i, "")
        .trim();
    }

    const el = document.querySelector('h1[role="button"]') || document.querySelector("header h1");
    const t = (el?.textContent || "").trim();
    if (!t) return null;
    return t.split(/\\s{2,}|\\n/)[0].trim() || t;
  });
}

async function getChannelList(page) {
  for (let attempt = 0; attempt < 12; attempt++) {
    const out = await page.evaluate(() => {
      const items = Array.from(
        document.querySelectorAll('[data-list-item-id^="channels___"]')
      ).map((el) => {
        const dataId = el.getAttribute("data-list-item-id") || "";
        const m = dataId.match(/^channels___(\\d+)/);
        const channelId = m ? m[1] : null;
        const aria = el.getAttribute("aria-label") || null;
        const rawText = (el.textContent || "").trim() || null;
        return { channelId, aria, rawText, dataId };
      });
      const seen = new Set();
      const uniq = [];
      for (const it of items) {
        if (!it.channelId) continue;
        if (seen.has(it.channelId)) continue;
        seen.add(it.channelId);
        uniq.push(it);
      }
      return uniq.slice(0, 500);
    });
    if (out.length) return out;
    await page.waitForTimeout(500);
  }
  return [];
}

async function collectMessages(page, maxMessages = 350, maxScrollSteps = 60) {
  const seenIds = new Set();
  const out = [];
  let noNewIters = 0;

  const extractOnce = async () => {
    const msgs = await page.evaluate(() => {
      const lis = Array.from(document.querySelectorAll('li[id^="chat-messages-"]'));
      const parsed = [];
      for (const li of lis) {
        const mId = li.id.match(/^chat-messages-(\d+)-(\d+)$/);
        const channelId = mId ? mId[1] : null;
        const messageId = mId ? mId[2] : null;
        const timeEl = li.querySelector("time");
        const ts = timeEl?.getAttribute("datetime") || null;
        const author =
          (li.querySelector('span[class*="username"]')?.textContent ||
            li.querySelector('h3 span')?.textContent ||
            li.querySelector("h3")?.textContent ||
            "")
            .trim() || null;

        const contentNodes = Array.from(li.querySelectorAll('[id^="message-content-"]'));
        let content = "";
        if (contentNodes.length) {
          content = contentNodes.map((n) => n.innerText || n.textContent || "").join("\\n");
        } else {
          const markup = li.querySelector('[class*="markup"]');
          content = markup?.innerText || markup?.textContent || "";
        }
        content = (content || "").trim();
        if (!author && !content) continue;
        parsed.push({ liId: li.id, channelId, messageId, author, ts, content });
      }
      return parsed;
    });
    return msgs;
  };

  const scrollUp = async () => {
    await page.evaluate(() => {
      const scrollables = Array.from(document.querySelectorAll("main div"))
        .filter((el) => {
          const st = getComputedStyle(el);
          return (
            (st.overflowY === "scroll" || st.overflowY === "auto") &&
            el.scrollHeight > el.clientHeight + 20
          );
        })
        .sort(
          (a, b) =>
            b.scrollHeight - b.clientHeight - (a.scrollHeight - a.clientHeight)
        );
      const scroller = scrollables[0];
      if (!scroller) return;
      scroller.scrollTop = Math.max(0, scroller.scrollTop - scroller.clientHeight * 0.9);
    });
  };

  for (let i = 0; i < maxScrollSteps; i++) {
    const msgs = await extractOnce();
    let added = 0;
    for (const m of msgs) {
      // liId includes message id; use it if present.
      const key = m.liId || crypto.createHash("sha1").update(JSON.stringify(m)).digest("hex");
      if (seenIds.has(key)) continue;
      seenIds.add(key);
      out.push({ id: key, ...m });
      added++;
    }

    if (out.length >= maxMessages) break;
    if (added === 0) noNewIters++;
    else noNewIters = 0;

    if (noNewIters >= 6) break;
    await scrollUp();
    await page.waitForTimeout(650);
  }

  // Sort by timestamp if present; otherwise keep insertion order.
  out.sort((a, b) => {
    const ta = a.ts ? Date.parse(a.ts) : NaN;
    const tb = b.ts ? Date.parse(b.ts) : NaN;
    if (Number.isNaN(ta) || Number.isNaN(tb)) return 0;
    return ta - tb;
  });
  return out;
}

function summarizeDisappointment(allMessages) {
  const disappointed = [];
  for (const m of allMessages) {
    const authorNorm = (m.author || "").replace(/^@+/, "").trim();
    // Skip server/bot announcement authors to avoid false positives from copy text like "What's next? Claim..."
    if (authorNorm.toLowerCase() === "oyster republic") continue;
    const themes = classifyDisappointment(m.content || "");
    if (!themes) continue;
    const lang = guessLang(m.content || "");
    // Skip obvious announcement/instruction blocks.
    const c = (m.content || "").toLowerCase();
    if (c.includes("claim your passport") && c.includes("welcome")) continue;
    disappointed.push({ ...m, themes, lang, authorNorm: authorNorm || null });
  }

  const themesCount = new Map();
  for (const m of disappointed) {
    for (const th of m.themes) themesCount.set(th, (themesCount.get(th) || 0) + 1);
  }

  const byAuthor = new Map();
  for (const m of disappointed) {
    const a = m.authorNorm || m.author || "unknown";
    if (!byAuthor.has(a)) byAuthor.set(a, []);
    byAuthor.get(a).push(m);
  }

  const themesRanked = Array.from(themesCount.entries())
    .sort((a, b) => b[1] - a[1])
    .map(([theme, count]) => ({ theme, count }));

  return { disappointed, themesRanked, byAuthor };
}

function draftReply({ author, lang, themes, sample }) {
  const th = new Set(themes || []);

  // A sincere structure: acknowledge + restate + ask for detail + commit to next step.
  const core = {
    en: {
      open: `@${author} Thanks for calling this out. You're right to be frustrated.`,
      ship: `On shipping: can you drop your order number (or last 4 digits) and country/region? We'll check your status and give you a concrete ETA.`,
      claim: `On claims/rewards: tell me what you see in-app (screenshot is ok). We'll verify your Founder Pass / OYS allocation and fix any mismatch.`,
      updates: `On updates: we'll start posting regular, dated updates in #announcements so you don't have to chase info.`,
      support: `On support: if you already opened a ticket, paste the ticket number and we'll pick it up.`,
      close: `If you prefer, DM me your details and I'll handle it 1:1.`,
    },
    zh: {
      open: `@${author} 你提到的这些我看到了，确实会让人很失望/着急，对不起。`,
      ship: `关于发货：把订单号（或后四位）+ 国家/地区发一下，我这边直接查状态，给你明确的时间点。`,
      claim: `关于领取/奖励：你把 App 里看到的页面（截图也行）发一下，我来核对 Founder Pass/OYS 是否少发或显示异常，确认后给你处理。`,
      updates: `关于信息更新：我们会在 #announcements 固定频率发“带日期”的进展更新，避免大家一直问一直等。`,
      support: `关于客服/工单：如果你开过 ticket，把编号贴一下，我这边优先跟进。`,
      close: `不方便公开的话也可以私信我你的信息，我一对一帮你搞定。`,
    },
    ru: {
      open: `@${author} Спасибо, что написали. Понимаю ваше разочарование, извините за это.`,
      ship: `По доставке: пришлите номер заказа (или последние 4 цифры) и страну, я проверю статус и дам точный ETA.`,
      claim: `По клейму/наградам: напишите, что показывает приложение (можно скрин), мы сверим Founder Pass / OYS и исправим несоответствие.`,
      updates: `По обновлениям: будем публиковать регулярные апдейты с датами в #announcements.`,
      support: `Если уже есть тикет, пришлите номер тикета, возьмем в работу.`,
      close: `Можно также в личку, если не хотите писать публично.`,
    },
    ja: {
      open: `@${author} 書き込みありがとう。待たされるのは本当にストレスですよね。申し訳ないです。`,
      ship: `発送について：注文番号（または下4桁）と国/地域を教えてください。状況を確認して具体的なETAを出します。`,
      claim: `クレーム/報酬について：アプリで見えている内容を教えてください（スクショOK）。Founder Pass/OYSを確認してズレがあれば直します。`,
      updates: `更新について：#announcements で日付付きの定期アップデートを出します。`,
      support: `チケットがある場合は番号を貼ってください。優先で追います。`,
      close: `公開が難しければDMでも大丈夫です。`,
    },
    ko: {
      open: `@${author} 말씀해주셔서 감사합니다. 답답하셨을 것 같아요. 죄송합니다.`,
      ship: `배송 관련: 주문번호(또는 뒤 4자리)와 국가/지역을 알려주시면 상태 확인 후 정확한 ETA를 드릴게요.`,
      claim: `클레임/보상 관련: 앱에서 보이는 화면(스크린샷 가능)을 보내주세요. Founder Pass/OYS를 확인해서 불일치가 있으면 바로잡겠습니다.`,
      updates: `업데이트 관련: #announcements 에 날짜가 있는 정기 업데이트를 올리겠습니다.`,
      support: `이미 티켓이 있다면 티켓 번호를 공유해주세요. 우선 처리하겠습니다.`,
      close: `공개가 불편하면 DM으로 보내셔도 됩니다.`,
    },
    fr: {
      open: `@${author} Merci de l'avoir signalé. Je comprends la frustration, désolé pour ça.`,
      ship: `Pour la livraison : envoie le numéro de commande (ou les 4 derniers chiffres) + ton pays/région. Je vérifie et je te donne un ETA concret.`,
      claim: `Pour le claim/récompenses : dis-moi ce que tu vois dans l'app (capture OK). On vérifie Founder Pass / OYS et on corrige tout décalage.`,
      updates: `Pour les updates : on va poster des mises à jour régulières et datées dans #announcements.`,
      support: `Si tu as déjà un ticket, colle le numéro de ticket ici et on le prend en charge.`,
      close: `Sinon DM-moi tes infos et je gère en 1:1.`,
    },
  };

  const pack = core[lang] || core.en;
  const lines = [pack.open];
  if (th.has("shipping/delivery")) lines.push(pack.ship);
  if (th.has("claim/rewards")) lines.push(pack.claim);
  if (th.has("lack of updates")) lines.push(pack.updates);
  if (th.has("support")) lines.push(pack.support);

  // If we detected "value/expectations" or "product/app broken", acknowledge explicitly.
  if (th.has("value/expectations")) {
    if (lang === "zh") lines.push("你说的“拿到东西但看不到价值/可领取内容”这个点很关键，我们会把可用权益和下一步动作讲清楚。");
    else if (lang === "ru") lines.push("Если сейчас кажется, что «нет ценности/нечего клеймить», это на нас: мы обязаны четко объяснить, что доступно и что делать дальше.");
    else lines.push("If it feels like \"I got the phone but there's nothing to do/claim\", that's on us. We'll clarify what's available and what's next.");
  }
  if (th.has("product/app broken")) {
    if (lang === "zh") lines.push("如果是 App/设备功能问题，把报错/复现步骤发一下，我们会尽快定位修复。");
    else if (lang === "ru") lines.push("Если это баг в приложении/устройстве, пришлите ошибку или шаги воспроизведения, мы быстро разберемся.");
    else lines.push("If it's an app/device issue, share the error or steps to reproduce and we'll triage it fast.");
  }

  lines.push(pack.close);
  // Keep it short-ish; include one quoted snippet to show we actually read it.
  if (sample) {
    if (lang === "zh") lines.push(`我看到你说：\"${sample.slice(0, 120)}\"`);
    else lines.push(`I saw your message: \"${sample.slice(0, 120)}\"`);
  }
  return lines.join("\\n");
}

function draftReplyShort({ lang, themes, sample }) {
  const th = new Set(themes || []);
  const s = (sample || "").trim();
  const h = (() => {
    // Deterministic small hash to vary openers a bit (avoid same first line everywhere).
    let x = 0;
    for (let i = 0; i < s.length; i++) x = (x * 31 + s.charCodeAt(i)) >>> 0;
    return x;
  })();
  const pick = (arr) => arr[(h || 0) % arr.length];

  if (lang === "zh") {
    const openers = ["收到，我来帮你把这件事查清楚。", "懂，我来跟进到有明确结果。", "谢谢你说清楚，我马上处理。"];
    const opener = pick(openers);

    // Keep to 1-2 short sentences.
    if (th.has("shipping/delivery")) {
      return `${opener} 把订单号(或后四位)+国家/地区发我，我回你明确 ETA；不方便公开就私信。`;
    }
    if (th.has("claim/rewards")) {
      return `${opener} 发钱包地址+App里Founder Pass/OYS截图，我核对并修正；不方便公开就私信。`;
    }
    if (th.has("product/app broken")) {
      return `${opener} 发报错提示+复现步骤(机型/系统/App版本)，我让团队尽快定位。`;
    }
    if (th.has("support")) {
      return `${opener} 有ticket编号的话贴一下，我直接接手。`;
    }
    if (th.has("lack of updates")) {
      return `${opener} 我们会在 #announcements 固定发“带日期”的更新。`;
    }
    if (th.has("value/expectations")) {
      return `${opener} 你期待的权益/下一步是什么？我把现在能做什么和接下来时间点讲清楚。`;
    }
    return opener;
  }

  if (lang === "ru") {
    const openers = [
      "Понял(а) — давайте разберёмся и закроем вопрос.",
      "Спасибо, что написали — я возьму это в работу.",
      "Согласен(на), это важно прояснить.",
    ];
    const opener = pick(openers);
    if (th.has("shipping/delivery")) {
      return `${opener} Пришлите № заказа (или последние 4) + страну/регион — проверю статус и вернусь с ETA (можно в ЛС).`;
    }
    if (th.has("claim/rewards")) {
      return `${opener} Пришлите адрес кошелька + скрин Founder Pass/OYS в приложении — сверю и исправлю несоответствие (можно в ЛС).`;
    }
    if (th.has("product/app broken")) {
      return `${opener} Укажите устройство/версию приложения и точный текст ошибки; если можно — шаги воспроизведения (можно в ЛС).`;
    }
    if (th.has("lack of updates")) {
      return `${opener} Будем публиковать регулярные обновления с датами в #announcements.`;
    }
    if (th.has("support")) {
      return `${opener} Если уже есть тикет, пришлите номер — я подхвачу (можно в ЛС).`;
    }
    if (th.has("value/expectations")) {
      return `${opener} Что вы ожидали vs что видите сейчас? Я объясню, что доступно уже и что дальше (с датами).`;
    }
    return opener;
  }

  if (lang === "ja") {
    const openers = ["了解です。状況を確認して対応します。", "教えてくれてありがとう。こちらで確認します。", "把握しました。こちらで追います。"];
    const opener = pick(openers);
    if (th.has("shipping/delivery")) {
      return `${opener} 注文番号(または下4桁)と国/地域を送ってください。配送状況とETAを確認して返信します(DMでもOK)。`;
    }
    if (th.has("claim/rewards")) {
      return `${opener} ウォレットアドレスとアプリのFounder Pass/OYS画面のスクショを共有ください。照合してズレを直します(DM可)。`;
    }
    if (th.has("product/app broken")) {
      return `${opener} 端末/アプリ版とエラー文、再現手順があれば教えてください(DM可)。`;
    }
    if (th.has("lack of updates")) {
      return `${opener} #announcements に日付入りで定期アップデートを出します。`;
    }
    if (th.has("support")) {
      return `${opener} すでにチケットがあれば番号をください。こちらで追います(DM可)。`;
    }
    if (th.has("value/expectations")) {
      return `${opener} 期待していた点と現状のギャップを教えてください。今できること/次の予定(日時)を明確にします。`;
    }
    return opener;
  }

  if (lang === "ko") {
    const openers = ["확인했어요. 바로 체크해서 처리할게요.", "알려줘서 고마워요. 제가 확인해볼게요.", "네, 이건 분명히 정리해야 해요."];
    const opener = pick(openers);
    if (th.has("shipping/delivery")) {
      return `${opener} 주문번호(또는 마지막 4자리) + 국가/지역을 보내주세요. 상태와 ETA 확인해서 답드릴게요(DM 가능).`;
    }
    if (th.has("claim/rewards")) {
      return `${opener} 지갑 주소 + 앱의 Founder Pass/OYS 화면 스크린샷을 보내주세요. 확인해서 불일치 있으면 맞추겠습니다(DM 가능).`;
    }
    if (th.has("product/app broken")) {
      return `${opener} 기기/앱 버전과 에러 문구, 재현 단계가 있으면 알려주세요(DM 가능).`;
    }
    if (th.has("lack of updates")) {
      return `${opener} #announcements 에 날짜 포함 업데이트를 정기적으로 올리겠습니다.`;
    }
    if (th.has("support")) {
      return `${opener} 티켓이 있으면 번호를 보내주세요. 제가 바로 확인할게요(DM 가능).`;
    }
    if (th.has("value/expectations")) {
      return `${opener} 기대한 점 vs 현재 상황을 알려주세요. 지금 가능한 것과 다음 일정(날짜)을 명확히 정리해드릴게요.`;
    }
    return opener;
  }

  if (lang === "fr") {
    const openers = ["Bien noté — je m’en occupe.", "Merci de l’avoir signalé — je prends ça en charge.", "Compris — on va clarifier et corriger ça."];
    const opener = pick(openers);
    if (th.has("shipping/delivery")) {
      return `${opener} Envoie ton n° de commande (ou les 4 derniers) + pays/région : je vérifie le statut et je reviens avec un ETA (DM ok).`;
    }
    if (th.has("claim/rewards")) {
      return `${opener} Partage ton wallet + une capture de l’écran Founder Pass/OYS dans l’app : je vérifie et corrige tout écart (DM ok).`;
    }
    if (th.has("product/app broken")) {
      return `${opener} Quel appareil/quelle version d’app, et quel message d’erreur exact ? Si possible, étapes pour reproduire (DM ok).`;
    }
    if (th.has("lack of updates")) {
      return `${opener} On va poster des updates datées et régulières dans #announcements.`;
    }
    if (th.has("support")) {
      return `${opener} Si tu as déjà un ticket, envoie le numéro et je le reprends (DM ok).`;
    }
    if (th.has("value/expectations")) {
      return `${opener} Tu attendais quoi vs ce que tu vois maintenant ? Je te liste ce qui est live + la suite (avec dates).`;
    }
    return opener;
  }

  if (lang === "pt") {
    const openers = ["Entendi — vou verificar e resolver.", "Obrigado por avisar — vou cuidar disso.", "Faz sentido cobrar — vamos esclarecer e corrigir."];
    const opener = pick(openers);
    if (th.has("shipping/delivery")) {
      return `${opener} Me manda o nº do pedido (ou os 4 últimos) + país/região: verifico o status e volto com um ETA (DM ok).`;
    }
    if (th.has("claim/rewards")) {
      return `${opener} Envie sua carteira + print do Founder Pass/OYS no app: eu confiro e corrijo qualquer divergência (DM ok).`;
    }
    if (th.has("product/app broken")) {
      return `${opener} Qual dispositivo/versão do app e qual erro exato? Se puder, passos para reproduzir (DM ok).`;
    }
    if (th.has("lack of updates")) {
      return `${opener} Vamos postar atualizações regulares e datadas em #announcements.`;
    }
    if (th.has("support")) {
      return `${opener} Se você já abriu um ticket, manda o número que eu pego pra acompanhar (DM ok).`;
    }
    if (th.has("value/expectations")) {
      return `${opener} O que você esperava vs o que vê agora? Eu explico o que está ao vivo + o que vem depois (com datas).`;
    }
    return opener;
  }

  if (lang === "th") {
    const openers = ["รับทราบครับ เดี๋ยวผมเช็กให้ชัดเจน", "ขอบคุณที่แจ้งนะครับ ผมจะตามให้", "เข้าใจครับ เราจะเคลียร์ให้ชัดเจนและแก้ไขให้"];
    const opener = pick(openers);
    if (th.has("shipping/delivery")) {
      return `${opener} ส่งเลขออเดอร์(หรือ 4 ตัวท้าย) + ประเทศ/ภูมิภาคมาได้ไหม ผมจะเช็กสถานะและ ETA ให้ (DM ได้)`;
    }
    if (th.has("claim/rewards")) {
      return `${opener} ส่งที่อยู่กระเป๋า + สกรีนหน้า Founder Pass/OYS ในแอปมา ผมจะตรวจและแก้ความคลาดเคลื่อนให้ (DM ได้)`;
    }
    if (th.has("product/app broken")) {
      return `${opener} ใช้รุ่นเครื่อง/เวอร์ชันแอปอะไร และขึ้น error อะไรบ้าง ถ้ามีขั้นตอนที่ทำให้เกิดซ้ำช่วยส่งมา (DM ได้)`;
    }
    if (th.has("lack of updates")) {
      return `${opener} เราจะโพสต์อัปเดตแบบมีวันที่ใน #announcements เป็นประจำ`;
    }
    if (th.has("support")) {
      return `${opener} ถ้ามีเลข ticket ส่งมาได้เลย ผมจะรับไปตามให้ (DM ได้)`;
    }
    if (th.has("value/expectations")) {
      return `${opener} คุณคาดหวังอะไร vs ตอนนี้เห็นอะไรอยู่ ผมจะสรุปว่าอะไรใช้ได้แล้วและอะไรจะมา (พร้อมวันที่)`;
    }
    return opener;
  }

  const sn = s.toLowerCase();
  const has = (needle) => sn.includes(needle);
  const enOpen = (() => {
    if (th.has("shipping/delivery")) {
      return pick([
        "Totally fair question — shipping should be clearer.",
        "You’re right to ask — we owe you a clear shipping update.",
        "Thanks for checking in — let’s get you a real status update.",
      ]);
    }
    if (th.has("claim/rewards")) {
      return pick([
        "Thanks for raising this — we’ll reconcile the numbers.",
        "Got it — we’ll verify what you’re seeing and fix any mismatch.",
        "Appreciate the detail — we’ll get this checked and corrected.",
      ]);
    }
    if (th.has("lack of updates")) {
      return pick([
        "You’re right — we’ve been too quiet.",
        "Fair point — we owe you more consistent updates.",
        "Agreed — the update cadence hasn’t been good enough.",
      ]);
    }
    if (th.has("product/app broken")) {
      return pick([
        "Thanks for reporting this — we’ll get you unstuck.",
        "Got it — we’ll investigate the error and follow up.",
        "Appreciate the report — we’ll diagnose what’s breaking here.",
      ]);
    }
    return pick([
      "Thanks for flagging this.",
      "Got it — thanks for raising this.",
      "Appreciate you calling it out.",
    ]);
  })();

  // Keep to 1-2 sentences, single line.
  const looksLikeClaim =
    has("eligible") ||
    has("not eligible") ||
    has("nft") ||
    has("claim") ||
    has("founder pass") ||
    has("oys") ||
    has("points") ||
    has("balance");
  const looksLikeShipping =
    has("order") ||
    has("shipping") ||
    has("delivery") ||
    has("send my phone") ||
    has("where is my phone") ||
    has("custom") ||
    has("duties") ||
    has("border") ||
    has("address");

  if (th.has("claim/rewards") && (looksLikeClaim || !looksLikeShipping)) {
    const extra =
      has("no eligible") || has("not eligible")
        ? "If you’re seeing “No eligible NFT found”, share your wallet + a screenshot of that screen."
        : has("680") || has("1000") || has("founder pass")
          ? "If your Founder Pass shows but OYS looks short, share your wallet + a screenshot of the balance."
          : "Share your wallet + an in-app screenshot for Founder Pass/OYS.";
    return `${enOpen} ${extra} I’ll reconcile any mismatch (DM ok).`;
  }

  if (th.has("shipping/delivery") && (looksLikeShipping || !looksLikeClaim)) {
    const extra =
      has("custom") || has("duties") || has("border") || has("euro")
        ? "If this is about customs/address changes, tell me what the site shows and your country."
        : "What’s your order # (or last 4) + country/region?";
    return `${enOpen} ${extra} I’ll check status and come back with an ETA (DM ok).`;
  }
  if (th.has("product/app broken")) {
    return `${enOpen} What device/app version are you on, and what exact error do you see? If you can, share steps to reproduce (DM ok).`;
  }
  if (th.has("support")) {
    return `${enOpen} If you already opened a ticket, share the ticket # and I’ll pick it up (DM ok).`;
  }
  if (th.has("lack of updates")) {
    return `${enOpen} We’ll post regular, dated updates in #announcements so you don’t have to chase info.`;
  }
  if (th.has("value/expectations")) {
    return `${enOpen} What did you expect vs what you see now? I’ll map what’s live + what’s next (with dates).`;
  }
  return enOpen;
}

async function main() {
  const entryUrl = process.argv[2];
  if (!entryUrl) {
    console.error("Usage: node discord_disappointment_audit.mjs <discord channel url>");
    process.exit(2);
  }
  // Default headless to avoid popping windows / stealing focus. Pass --headed to show UI.
  const headless = !process.argv.includes("--headed");
  const ids = extractGuildAndChannel(entryUrl);
  if (!ids) {
    console.error("Not a /channels/<guildId>/<channelId> url");
    process.exit(2);
  }
  const entryOnly = process.argv.includes("--entry-only");

  const baseDir = path.resolve(process.cwd(), "audit");
  const runDir = path.join(baseDir, ts() + "-disappointment");
  mkdirp(runDir);

  const userDataDir = path.resolve(process.cwd(), "user-data");
  mkdirp(userDataDir);

  const context = await chromium.launchPersistentContext(userDataDir, {
    headless,
    viewport: { width: 1400, height: 900 },
    args: ["--disable-dev-shm-usage"],
  });
  const page = context.pages()[0] ?? (await context.newPage());
  page.setDefaultTimeout(60_000);

  await page.goto(entryUrl, { waitUntil: "networkidle" });
  await waitForDiscord(page);
  await page.screenshot({ path: path.join(runDir, "entry.png"), fullPage: true }).catch(() => {});

  const guildName = await getGuildName(page).catch(() => null);
  const channelsRaw = await getChannelList(page);
  const channels = channelsRaw
    .map((c) => ({
      channelId: c.channelId,
      name: cleanChannelName(c.aria || c.rawText || ""),
      aria: c.aria,
    }))
    .filter((c) => c.channelId && c.name)
    .slice(0, 200);

  // Prioritize likely discussion channels.
  const preferred = new Set([
    "general-english",
    "chinese",
    "russian",
    "japanese",
    "korean",
    "french",
    "portuguese",
    "thailand",
    "👋welcome",
  ]);
  // If channel discovery flakes (Discord UI changes), fall back to known channel IDs.
  const fallbackKnown = [
    { name: "👋welcome", channelId: "1404726112789073932" },
    { name: "announcements", channelId: "1416406372660023566" },
    { name: "general-english", channelId: "1404870331759591575" },
    { name: "chinese", channelId: "1416430673652355112" },
    { name: "russian", channelId: "1416430799225337876" },
    { name: "japanese", channelId: "1416431181934604420" },
    { name: "korean", channelId: "1416430948936943667" },
    { name: "french", channelId: "1416431205309456424" },
    { name: "portuguese", channelId: "1416431248921823284" },
    { name: "thailand", channelId: "1416431293997887590" },
  ];

  const pickedDiscovered = [
    ...channels.filter((c) => preferred.has(c.name)),
    ...channels.filter((c) => !preferred.has(c.name)),
  ].slice(0, 8); // keep runtime reasonable

  const picked = entryOnly
    ? [{ name: "entry-channel", channelId: ids.channelId, aria: null }]
    :
    pickedDiscovered.length > 0
      ? pickedDiscovered
      : fallbackKnown.map((c) => ({ ...c, aria: null }));

  writeJson(path.join(runDir, "channels.json"), {
    guildId: ids.guildId,
    guildName,
    channelsRawCount: channelsRaw.length,
    channelsSample: channelsRaw.slice(0, 8),
    channelsProcessedCount: channels.length,
    channelsProcessedSample: channels.slice(0, 12),
    picked,
  });

  const perChannel = [];
  for (const ch of picked) {
    const url = `https://discord.com/channels/${ids.guildId}/${ch.channelId}`;
    await page.goto(url, { waitUntil: "networkidle" });
    await page.waitForTimeout(1200);
    const messages = await collectMessages(page, 350, 60);
    perChannel.push({ ...ch, url, messagesCount: messages.length });
    writeJson(path.join(runDir, `messages_${ch.name}_${ch.channelId}.json`), {
      ...ch,
      url,
      messages,
    });
  }

  // Aggregate and analyze
  const all = [];
  for (const ch of picked) {
    const f = path.join(runDir, `messages_${ch.name}_${ch.channelId}.json`);
    const d = JSON.parse(fs.readFileSync(f, "utf8"));
    for (const m of d.messages || []) {
      all.push({
        channel: ch.name,
        channelId: ch.channelId,
        url: `https://discord.com/channels/${ids.guildId}/${ch.channelId}`,
        ...m,
      });
    }
  }

  const analysis = summarizeDisappointment(all);
  const byAuthorOut = [];
  for (const [author, msgs] of analysis.byAuthor.entries()) {
    // Never auto-reply to ourselves.
    if ((author || "").toLowerCase() === "oysterguard") continue;
    const themes = Array.from(new Set(msgs.flatMap((m) => m.themes)));
    // Use the latest message by timestamp when available.
    const sorted = [...msgs].sort((a, b) => {
      const ta = a.ts ? Date.parse(a.ts) : 0;
      const tb = b.ts ? Date.parse(b.ts) : 0;
      return ta - tb;
    });
    const last = sorted[sorted.length - 1] || msgs[msgs.length - 1];
    const sample = last?.content || "";
    const langByChannel = {
      "general-english": "en",
      "chinese": "zh",
      "russian": "ru",
      "japanese": "ja",
      "korean": "ko",
      "french": "fr",
      "portuguese": "pt",
      "thailand": "th",
    };
    const inferred = last?.lang || "unknown";
    const channelHint = last?.channel ? langByChannel[last.channel] : null;
    // If the message language is unclear/Latin, prefer channel language for language-specific channels.
    const lang =
      channelHint && (inferred === "unknown" || inferred === "en")
        ? channelHint
        : (inferred === "unknown" ? "en" : inferred);
    const targetChannelId = last?.channelId || null;
    const targetMessageId = last?.messageId || null;
    const targetMessageUrl =
      targetChannelId && targetMessageId
        ? `https://discord.com/channels/${ids.guildId}/${targetChannelId}/${targetMessageId}`
        : null;
    byAuthorOut.push({
      author,
      lang,
      themes,
      count: msgs.length,
      channels: Array.from(new Set(msgs.map((m) => m.channel))),
      sample: sample.slice(0, 400),
      targetChannelId,
      targetMessageId,
      targetMessageUrl,
      replyShort: draftReplyShort({ lang, themes, sample }),
      draft: draftReply({ author: author.replace(/^@/, ""), lang, themes, sample }),
    });
  }
  byAuthorOut.sort((a, b) => b.count - a.count);

  const report = {
    ok: true,
    guildId: ids.guildId,
    guildName,
    pickedChannels: perChannel,
    scannedMessages: all.length,
    disappointedMessages: analysis.disappointed.length,
    themes: analysis.themesRanked,
    authors: byAuthorOut,
    outputDir: runDir,
    note:
      "This is based on the messages loaded in the Discord web UI (virtualized). It may not include the full history.",
  };
  writeJson(path.join(runDir, "report.json"), report);

  // Render a readable markdown.
  const lines = [];
  lines.push(`# Oyster Discord Disappointment Audit`);
  lines.push(`- Guild: ${guildName || "(unknown)"} (${ids.guildId})`);
  lines.push(`- Channels scanned: ${perChannel.map((c) => c.name).join(", ")}`);
  lines.push(`- Messages scanned: ${all.length}`);
  lines.push(`- Disappointed messages flagged: ${analysis.disappointed.length}`);
  lines.push(``);
  lines.push(`## Top Themes`);
  for (const t of analysis.themesRanked) lines.push(`- ${t.theme}: ${t.count}`);
  lines.push(``);
  lines.push(`## People To Reply To (Drafts)`);
  for (const a of byAuthorOut) {
    lines.push(`### ${a.author} (${a.lang})`);
    lines.push(`- Themes: ${a.themes.join(", ") || "(unknown)"}`);
    lines.push(`- Channels: ${a.channels.join(", ")}`);
    lines.push(`- Sample: ${a.sample.replace(/\\n+/g, " ").slice(0, 240)}`);
    lines.push(`- ReplyShort: ${a.replyShort}`);
    lines.push(``);
  }
  // Use real newlines (not the literal "\\n" sequences).
  writeText(path.join(runDir, "report.md"), lines.join("\n"));

  await context.close();
}

main().catch((err) => {
  try {
    fs.writeFileSync(path.resolve(process.cwd(), "audit_crash.txt"), String(err?.stack || err));
  } catch {}
  process.exit(1);
});
