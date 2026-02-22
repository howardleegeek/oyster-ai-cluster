import fs from "node:fs";
import path from "node:path";
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

async function waitForChannelsUi(page) {
  // Discord is heavy; rely on stable ARIA labels.
  await page.waitForSelector('[aria-label="频道"]', { timeout: 60_000 });
  await page.waitForTimeout(800);
}

async function getChannelIndex(page) {
  // Use aria-label strings; also capture channel ids from data-list-item-id.
  return await page.evaluate(() => {
    const items = Array.from(
      document.querySelectorAll('[data-list-item-id^="channels___"]')
    ).map((el) => {
      const dataId = el.getAttribute("data-list-item-id") || "";
      const m = dataId.match(/^channels___(\d+)/);
      const channelId = m ? m[1] : null;
      // aria-label includes "xxx（文字频道）" in Chinese UI.
      const aria = el.getAttribute("aria-label") || null;
      // textContent often includes unread markers; aria is cleaner.
      const rawText = (el.textContent || "").trim() || null;
      return { channelId, aria, rawText, dataId };
    });

    // De-dupe by channelId, preserve order.
    const seen = new Set();
    const out = [];
    for (const it of items) {
      if (!it.channelId) continue;
      if (seen.has(it.channelId)) continue;
      seen.add(it.channelId);
      out.push(it);
    }
    return out.slice(0, 300);
  });
}

async function scrapeVisibleMessages(page, limit = 80) {
  return await page.evaluate((limitInner) => {
    // Discord uses a virtualized list; only visible + some buffer exists in DOM.
    // Try multiple selectors for message groups.
    const roots = [
      document.querySelector('main [aria-label*="消息"]'),
      document.querySelector('main [role="log"]'),
      document.querySelector("main"),
    ].filter(Boolean);

    const collect = () => {
      const nodes = [];
      for (const r of roots) {
        nodes.push(
          ...Array.from(
            r.querySelectorAll(
              '[id^="chat-messages-"] [class*="messageListItem"], [role="listitem"]'
            )
          )
        );
      }
      // De-dupe by node reference.
      return Array.from(new Set(nodes));
    };

    const msgNodes = collect();
    const msgs = [];

    for (const n of msgNodes) {
      // Author
      const author =
        n.querySelector('[class*="header"] [class*="username"]')?.textContent?.trim() ||
        n.querySelector('[data-testid="message-username"]')?.textContent?.trim() ||
        n.querySelector('h3 [role="button"]')?.textContent?.trim() ||
        null;

      // Timestamp
      const timeEl = n.querySelector("time");
      const ts = timeEl?.getAttribute("datetime") || null;

      // Content (join multiple lines)
      const contentEl =
        n.querySelector('[id^="message-content-"]') ||
        n.querySelector('[class*="markup"]') ||
        null;
      let content = contentEl?.innerText || contentEl?.textContent || "";
      content = (content || "").replace(/\s+\n/g, "\n").trim();

      // Skip empty items (like dividers)
      if (!author && !content) continue;
      // Skip system UI noises
      if (content && /下载我们的桌面 APP|想要充分体验 Discord/.test(content)) continue;

      msgs.push({ author, ts, content });
    }

    // Keep last N in DOM order
    const tail = msgs.slice(-limitInner);
    return tail;
  }, limit);
}

async function scrollUpForMore(page, steps = 6) {
  // Scroll up in the message scroller to load older messages.
  for (let i = 0; i < steps; i++) {
    await page.evaluate(() => {
      const scroller =
        document.querySelector('main [class*="scroller"]') ||
        document.querySelector('main [role="log"]') ||
        document.querySelector("main");
      if (!scroller) return;
      scroller.scrollTop = Math.max(0, scroller.scrollTop - scroller.clientHeight * 0.9);
    });
    await page.waitForTimeout(700);
  }
}

async function main() {
  const entryUrl = process.argv[2];
  // Default headless to avoid popping windows / stealing focus. Pass --headed to show UI.
  const headless = !process.argv.includes("--headed");
  const onlyEntry = process.argv.includes("--only-entry") || !process.argv.includes("--picked");
  if (!entryUrl) {
    console.error(
      "Usage: node discord_scrape_recent.mjs <discord channel url> [--headed] [--only-entry] [--picked]"
    );
    process.exit(2);
  }

  const ids = extractGuildAndChannel(entryUrl);
  if (!ids) {
    console.error("Not a /channels/<guildId>/<channelId> url");
    process.exit(2);
  }

  const baseDir = path.resolve(process.cwd(), "audit");
  const runDir = path.join(baseDir, ts() + "-scrape");
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
  await waitForChannelsUi(page);

  const guildName = await page
    .evaluate(() => {
      const el =
        document.querySelector('[aria-label$="(服务器)"]') ||
        document.querySelector('h1[role="button"]') ||
        document.querySelector("header h1");
      return (el?.textContent || "").trim() || null;
    })
    .catch(() => null);

  const channelIndex = await getChannelIndex(page);
  writeJson(path.join(runDir, "channel_index.json"), { guildName, ...ids, channelIndex });

  // By default (for other communities), just scrape the entry channel to avoid assumptions about channel naming.
  // If --picked is passed, scrape a small set of common channels.
  let picked = [];
  if (onlyEntry) {
    picked = [{ channelId: ids.channelId, name: "(entry)", aria: null }];
  } else {
    const want = ["general-english", "chinese", "👋welcome", "announcements"];
    for (const it of channelIndex) {
      const name =
        (it.aria || it.rawText || "")
          .replace(/（文字频道）/g, "")
          .replace(/^未读，/g, "")
          .trim();
      if (!name) continue;
      if (want.includes(name) && it.channelId) {
        picked.push({ channelId: it.channelId, name, aria: it.aria });
      }
    }
    if (picked.length < 2) {
      for (const it of channelIndex) {
        const name =
          (it.aria || it.rawText || "")
            .replace(/（文字频道）/g, "")
            .replace(/^未读，/g, "")
            .trim();
        if (!name) continue;
        picked.push({ channelId: it.channelId, name, aria: it.aria });
        if (picked.length >= 3) break;
      }
    }
  }

  const results = [];
  for (const ch of picked) {
    const url = `https://discord.com/channels/${ids.guildId}/${ch.channelId}`;
    await page.goto(url, { waitUntil: "networkidle" });
    await page.waitForTimeout(1200);
    await scrollUpForMore(page, 4);
    const msgs = await scrapeVisibleMessages(page, 80);
    results.push({ ...ch, url, messages: msgs });
    writeJson(path.join(runDir, `messages_${ch.channelId}.json`), { ...ch, url, messages: msgs });
  }

  writeJson(path.join(runDir, "result.json"), {
    ok: true,
    entryUrl,
    guildId: ids.guildId,
    guildName,
    pickedChannels: results.map((r) => ({ channelId: r.channelId, name: r.name, url: r.url })),
    outputDir: runDir,
  });

  await context.close();
}

main().catch((err) => {
  try {
    fs.writeFileSync(
      path.resolve(process.cwd(), "audit_crash.txt"),
      String(err?.stack || err)
    );
  } catch {}
  process.exit(1);
});
