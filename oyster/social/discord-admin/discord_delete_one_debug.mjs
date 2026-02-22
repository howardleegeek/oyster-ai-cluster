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

async function gotoMessage(page, channelId, messageId) {
  const url = `https://discord.com/channels/${GUILD_ID}/${channelId}/${messageId}`;
  await page.goto(url, { waitUntil: "networkidle" });
  await page.waitForTimeout(1500);
  return url;
}

async function dumpMenuItems(page) {
  return await page.evaluate(() => {
    const menu = document.querySelector('[role="menu"]');
    if (!menu) return [];
    const items = Array.from(menu.querySelectorAll('[role="menuitem"]'));
    return items.map((n) => (n.textContent || "").trim()).filter(Boolean);
  });
}

async function openMessageMenu(page, li) {
  // First try right-click on time (fast when it works).
  await page.keyboard.press("Escape").catch(() => {});
  await page.waitForTimeout(80);

  const timeEl = li.locator("time").first();
  if (await timeEl.count()) {
    await timeEl.click({ button: "right", force: true, timeout: 5_000 }).catch(() => {});
  } else {
    await li.click({ button: "right", force: true, timeout: 5_000 }).catch(() => {});
  }

  // If no menu appears, fall back to clicking the message "More/更多" button.
  const menu = page.locator('[role="menu"]').first();
  if (await menu.count()) return;

  await li.hover().catch(() => {});
  const moreBtn = li
    .locator('button[aria-label*="更多"], button[aria-label*="More"], [aria-label*="更多"], [aria-label*="More"]')
    .first();
  if (await moreBtn.count()) {
    await moreBtn.click({ timeout: 5_000 }).catch(() => {});
  }
}

async function main() {
  const messageId = argVal("--message");
  const channelId = argVal("--channel", DEFAULT_CHANNEL_ID);
  if (!messageId) {
    console.error("Usage: node discord_delete_one_debug.mjs --message <messageId> [--channel <channelId>]");
    process.exit(2);
  }
  // Default headless to avoid popping windows / stealing focus. Pass --headed to show UI.
  const headless = !process.argv.includes("--headed");

  const outDir = path.resolve(process.cwd(), "output");
  fs.mkdirSync(outDir, { recursive: true });
  const ts = new Date().toISOString().replace(/[:.]/g, "-");

  const context = await chromium.launchPersistentContext(path.resolve(process.cwd(), "user-data"), {
    headless,
    viewport: { width: 1400, height: 900 },
    args: ["--disable-dev-shm-usage"],
  });
  const page = context.pages()[0] ?? (await context.newPage());
  page.setDefaultTimeout(60_000);

  const url = await gotoMessage(page, channelId, messageId);
  const liId = `chat-messages-${channelId}-${messageId}`;
  const li = page.locator(`li[id="${liId}"]`).first();
  await li.waitFor({ timeout: 30_000 });
  await li.scrollIntoViewIfNeeded();
  await li.hover().catch(() => {});

  await openMessageMenu(page, li);

  const del = page
    .locator(
      [
        '[role="menuitem"][data-list-item-id*="delete"]',
        '[role="menuitem"]:has-text("删除信息")',
        '[role="menuitem"]:has-text("删除消息")',
        '[role="menuitem"]:has-text("Delete Message")',
      ].join(", ")
    )
    .first();

  try {
    await del.waitFor({ timeout: 8_000 });
  } catch {
    const items = await dumpMenuItems(page);
    const shot = path.join(outDir, `delete-debug-no-delete-item-${ts}.png`);
    await page.screenshot({ path: shot, fullPage: false });
    console.log(JSON.stringify({ ok: false, stage: "no_delete_menuitem", url, liId, menuItems: items, screenshot: shot }, null, 2));
    await context.close();
    process.exit(1);
  }

  await del.click();

  const confirm = page.locator('button:has-text("删除"), button:has-text("Delete")').first();
  try {
    await confirm.waitFor({ timeout: 8_000 });
  } catch {
    const items = await dumpMenuItems(page);
    const shot = path.join(outDir, `delete-debug-no-confirm-${ts}.png`);
    await page.screenshot({ path: shot, fullPage: false });
    console.log(JSON.stringify({ ok: false, stage: "no_confirm", url, liId, menuItems: items, screenshot: shot }, null, 2));
    await context.close();
    process.exit(1);
  }

  await confirm.click();
  await page.waitForTimeout(1200);

  // Best-effort verify it's gone from DOM in this view.
  const stillThere = await li.count();
  const shot = path.join(outDir, `delete-debug-after-${ts}.png`);
  await page.screenshot({ path: shot, fullPage: false });

  await context.close();
  console.log(JSON.stringify({ ok: stillThere === 0, url, liId, stillThere, screenshot: shot }, null, 2));
  if (stillThere !== 0) process.exit(1);
}

main().catch((err) => {
  console.error(err?.stack || String(err));
  process.exit(1);
});
