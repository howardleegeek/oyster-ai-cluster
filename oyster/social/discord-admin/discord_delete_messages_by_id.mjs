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

function hasFlag(flag) {
  return process.argv.includes(flag);
}

async function gotoMessage(page, channelId, messageId) {
  const url = `https://discord.com/channels/${GUILD_ID}/${channelId}/${messageId}`;
  // Discord keeps long-lived connections; "domcontentloaded" is more stable than "networkidle".
  await page.goto(url, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(1200);
  return url;
}

async function openMessageMenu(page, li) {
  await page.keyboard.press("Escape").catch(() => {});
  await page.waitForTimeout(80);

  // Prefer hover bar "More/更多" (more reliable than right-click in Discord).
  await li.hover().catch(() => {});
  await page.waitForTimeout(180);

  const moreBtn = li
    .locator(
      [
        '[role="button"][aria-label="更多"]',
        '[role="button"][aria-label="More"]',
        'button[aria-label="更多"]',
        'button[aria-label="More"]',
        'div[role="button"][aria-label="更多"]',
        'div[role="button"][aria-label="More"]',
      ].join(", ")
    )
    .first();

  if (await moreBtn.count()) {
    await moreBtn.click({ timeout: 5_000 }).catch(() => {});
  } else {
    // Fallback: right-click time.
    const timeEl = li.locator("time").first();
    if (await timeEl.count()) {
      await timeEl.click({ button: "right", force: true, timeout: 5_000 }).catch(() => {});
    } else {
      await li.click({ button: "right", force: true, timeout: 5_000 }).catch(() => {});
    }
  }
}

async function deleteCurrentMessage(page, channelId, messageId) {
  const url = await gotoMessage(page, channelId, messageId);
  const liId = `chat-messages-${channelId}-${messageId}`;
  const li = page.locator(`li[id="${liId}"]`).first();
  await li.waitFor({ timeout: 30_000 });
  await li.scrollIntoViewIfNeeded();

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
  await del.waitFor({ timeout: 10_000 });
  await del.click();

  const confirm = page.locator('button:has-text("删除"), button:has-text("Delete")').first();
  await confirm.waitFor({ timeout: 10_000 });
  await confirm.click();
  await page.waitForTimeout(1100);

  const stillThere = await li.count();
  return { ok: stillThere === 0, url, liId, stillThere };
}

async function main() {
  const channelId = argVal("--channel", DEFAULT_CHANNEL_ID);
  const idsArg = argVal("--ids");
  const fromJson = argVal("--from-json");
  const delayMs = Number(argVal("--delay-ms", "900"));
  // Default headless to avoid popping windows / stealing focus. Pass --headed to show UI.
  const headless = !process.argv.includes("--headed");

  let ids = [];
  if (idsArg) ids = idsArg.split(",").map((s) => s.trim()).filter(Boolean);
  if (fromJson) {
    const j = JSON.parse(fs.readFileSync(fromJson, "utf8"));
    if (Array.isArray(j)) ids.push(...j);
    else if (Array.isArray(j.ids)) ids.push(...j.ids);
  }
  ids = Array.from(new Set(ids));

  if (!ids.length) {
    console.error("Usage: node discord_delete_messages_by_id.mjs --ids <id1,id2,...> [--channel <channelId>]");
    process.exit(2);
  }

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

  const run = { startedAt: new Date().toISOString(), channelId, ids, deleted: [], errors: [] };

  for (const messageId of ids) {
    try {
      const r = await deleteCurrentMessage(page, channelId, messageId);
      run.deleted.push({ messageId, ...r });
      if (delayMs) await page.waitForTimeout(delayMs);
    } catch (e) {
      const shot = path.join(outDir, `delete-by-id-error-${ts}-${messageId}.png`);
      await page.screenshot({ path: shot, fullPage: false }).catch(() => {});
      run.errors.push({ messageId, error: e?.message || String(e), screenshot: shot });
      if (delayMs) await page.waitForTimeout(delayMs);
    }
  }

  await context.close();

  const outJson = path.join(outDir, `delete-by-id-${ts}.json`);
  fs.writeFileSync(outJson, JSON.stringify(run, null, 2));
  console.log(JSON.stringify({ ok: run.errors.length === 0, outJson, deleted: run.deleted.length, errors: run.errors.length }, null, 2));
  if (run.errors.length && !hasFlag("--no-exit-1")) process.exit(1);
}

main().catch((err) => {
  console.error(err?.stack || String(err));
  process.exit(1);
});
