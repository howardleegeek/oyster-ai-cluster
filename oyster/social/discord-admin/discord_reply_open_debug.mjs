import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

const GUILD_ID = "1404726112159793172";
const DEFAULT_CHANNEL_ID = "1404870331759591575";

function argVal(flag, def = null) {
  const i = process.argv.indexOf(flag);
  if (i === -1) return def;
  return process.argv[i + 1] ?? def;
}

function now() {
  return Date.now();
}

async function main() {
  const messageId = argVal("--message");
  const channelId = argVal("--channel", DEFAULT_CHANNEL_ID);
  if (!messageId) {
    console.error("Usage: node discord_reply_open_debug.mjs --message <messageId> [--channel <channelId>]");
    process.exit(2);
  }

  const outDir = path.resolve(process.cwd(), "output");
  fs.mkdirSync(outDir, { recursive: true });
  const ts = new Date().toISOString().replace(/[:.]/g, "-");

  const context = await chromium.launchPersistentContext(path.resolve(process.cwd(), "user-data"), {
    headless: !process.argv.includes("--headed"),
    viewport: { width: 1400, height: 900 },
    args: ["--disable-dev-shm-usage"],
  });
  const page = context.pages()[0] ?? (await context.newPage());
  page.setDefaultTimeout(60_000);

  const url = `https://discord.com/channels/${GUILD_ID}/${channelId}/${messageId}`;
  const t0 = now();
  await page.goto(url, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(1800);
  const t1 = now();

  const liId = `chat-messages-${channelId}-${messageId}`;
  const sel = `li[id="${liId}"]`;

  const steps = [];
  const snap = async (label) => {
    const p = path.join(outDir, `reply-open-${channelId}-${messageId}-${label}-${ts}.png`);
    await page.screenshot({ path: p, fullPage: false }).catch(() => {});
    return p;
  };

  steps.push({ step: "goto", ms: t1 - t0, screenshot: await snap("after-goto") });

  const t2 = now();
  await page.waitForSelector(sel, { timeout: 30_000 });
  const t3 = now();
  steps.push({ step: "wait-li", ms: t3 - t2 });

  const li = page.locator(sel).first();
  await li.scrollIntoViewIfNeeded().catch(() => {});
  await li.hover().catch(() => {});
  await page.waitForTimeout(250);
  steps.push({ step: "hover", screenshot: await snap("after-hover") });

  const moreBtn = li.locator('[role="button"][aria-label="更多"], [role="button"][aria-label="More"]').first();
  const moreCount = await moreBtn.count();
  steps.push({ step: "more-count", count: moreCount });
  if (moreCount) {
    await moreBtn.click({ timeout: 5_000 }).catch(() => {});
    await page.waitForTimeout(300);
    steps.push({ step: "clicked-more", screenshot: await snap("after-more") });
  }

  const replyItem = page.locator('[role="menuitem"]:has-text("回复"), [role="menuitem"]:has-text("Reply")').first();
  const replyVisible = await replyItem.isVisible().catch(() => false);
  steps.push({ step: "reply-menu-visible", replyVisible, screenshot: await snap("after-reply-visible-check") });

  if (replyVisible) {
    await replyItem.click({ timeout: 5_000 }).catch(() => {});
    await page.waitForTimeout(300);
    steps.push({ step: "clicked-reply", screenshot: await snap("after-click-reply") });
  }

  const composer = page.locator('[role="textbox"][contenteditable="true"]').first();
  const composerVisible = await composer.isVisible().catch(() => false);
  steps.push({ step: "composer-visible", composerVisible, screenshot: await snap("final") });

  await context.close();
  console.log(JSON.stringify({ url, liId, steps }, null, 2));
}

main().catch((err) => {
  console.error(err?.stack || String(err));
  process.exit(1);
});

