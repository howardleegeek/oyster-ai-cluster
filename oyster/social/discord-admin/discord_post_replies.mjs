import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

function readJson(p) {
  return JSON.parse(fs.readFileSync(p, "utf8"));
}

function chunkByLength(lines, maxLen = 1800) {
  const chunks = [];
  let cur = "";
  for (const line of lines) {
    const add = (cur ? "\n" : "") + line;
    if ((cur + add).length > maxLen) {
      if (cur) chunks.push(cur);
      // If a single line is too long, hard-slice it.
      if (line.length > maxLen) {
        chunks.push(line.slice(0, maxLen));
        cur = line.slice(maxLen);
      } else {
        cur = line;
      }
    } else {
      cur += add;
    }
  }
  if (cur) chunks.push(cur);
  return chunks;
}

function shortReply(lang, themes) {
  const th = new Set(themes || []);
  if (lang === "zh") {
    const parts = ["抱歉让你遇到这个问题。"];
    if (th.has("shipping/delivery")) parts.push("把订单号(或后四位)+国家/地区发我，我查物流并给明确 ETA。");
    if (th.has("claim/rewards")) parts.push("把钱包地址+App 里 Founder Pass/OYS/领取失败的截图发我，我核对并处理。");
    if (th.has("product/app broken")) parts.push("如果是连接/功能报错，发报错提示+复现步骤我马上排查。");
    if (th.has("support")) parts.push("有 ticket 编号的话也贴一下我优先跟进。");
    if (th.has("lack of updates")) parts.push("我们会在 #announcements 发带日期的更新。");
    if (th.has("value/expectations")) parts.push("你说的“权益/下一步不清楚”很关键，我们会讲清楚并补齐动作。");
    parts.push("不方便公开就私信我。");
    return parts.join(" ");
  }

  const parts = ["Sorry about this."];
  if (th.has("shipping/delivery")) parts.push("DM your order # (or last 4) + country/region and I'll confirm status + ETA.");
  if (th.has("claim/rewards")) parts.push("Share your wallet + what you see in-app (screenshot ok) and we'll reconcile Founder Pass/OYS/claim.");
  if (th.has("product/app broken")) parts.push("If it's an app/device issue, send the error + steps to reproduce.");
  if (th.has("support")) parts.push("If you have a ticket, paste the ticket # here.");
  if (th.has("lack of updates")) parts.push("We'll post dated updates in #announcements.");
  if (th.has("value/expectations")) parts.push("Fair point; we'll clarify what's available + what's next.");
  parts.push("DM me if you prefer.");
  return parts.join(" ");
}

async function typeAndSend(page, text) {
  // Discord composer is a contenteditable textbox.
  const composer = page.locator('[role="textbox"][contenteditable="true"]').first();
  await composer.waitFor({ timeout: 60_000 });
  await composer.click();
  await page.keyboard.type(text, { delay: 5 });
  await page.keyboard.press("Enter");
}

async function main() {
  const reportPath = process.argv[2];
  if (!reportPath) {
    console.error("Usage: node discord_post_replies.mjs <path-to-report.json> [--dry-run]");
    process.exit(2);
  }
  const dryRun = process.argv.includes("--dry-run");
  // Default headless to avoid popping windows / stealing focus. Pass --headed to show UI.
  const headless = !process.argv.includes("--headed");

  const rep = readJson(reportPath);
  const guildId = rep.guildId;
  if (!guildId) throw new Error("report.json missing guildId");

  // Channel IDs for where we will post roundups.
  const channelTargets = {
    "general-english": "1404870331759591575",
    chinese: "1416430673652355112",
  };

  // Group by language (zh -> chinese channel, else general-english) and post 1 message per person.
  const groups = { "general-english": [], chinese: [] };
  for (const a of rep.authors || []) {
    const author = (a.author || "").replace(/^@+/, "").trim();
    if (!author || author.toLowerCase() === "unknown") continue;
    const lang = a.lang === "zh" ? "zh" : "en";
    const channelKey = lang === "zh" ? "chinese" : "general-english";
    groups[channelKey].push({ author, lang, themes: a.themes || [] });
  }

  const payloads = [];
  for (const [channelKey, arr] of Object.entries(groups)) {
    if (!arr.length) continue;
    const msgs = arr.map((it) => `@${it.author} ${shortReply(it.lang, it.themes)}`);
    payloads.push({ channelKey, msgs });
  }

  if (dryRun) {
    console.log(JSON.stringify(payloads, null, 2));
    return;
  }

  const userDataDir = path.resolve(process.cwd(), "user-data");
  const context = await chromium.launchPersistentContext(userDataDir, {
    headless,
    viewport: { width: 1400, height: 900 },
    args: ["--disable-dev-shm-usage"],
  });
  const page = context.pages()[0] ?? (await context.newPage());
  page.setDefaultTimeout(60_000);

  for (const p of payloads) {
    const channelId = channelTargets[p.channelKey];
    const url = `https://discord.com/channels/${guildId}/${channelId}`;
    await page.goto(url, { waitUntil: "networkidle" });
    await page.waitForTimeout(1500);
    for (const msg of p.msgs) {
      await typeAndSend(page, msg);
      await page.waitForTimeout(650);
    }
  }

  await context.close();
}

main().catch((err) => {
  console.error(err?.stack || String(err));
  process.exit(1);
});
