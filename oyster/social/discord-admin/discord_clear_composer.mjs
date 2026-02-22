import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

const GUILD_ID = "1404726112159793172";
const CHANNEL_GENERAL_ENGLISH = "1404870331759591575";

async function gotoChannel(page, channelId) {
  const url = `https://discord.com/channels/${GUILD_ID}/${channelId}`;
  await page.goto(url, { waitUntil: "networkidle" });
  await page.waitForTimeout(1200);
  return url;
}

async function clearComposer(page) {
  const composer = page.locator('[role="textbox"][contenteditable="true"]').first();
  await composer.waitFor({ timeout: 20_000 });
  await composer.click();
  // macOS: Meta+A. (Ctrl+A also works sometimes, but be explicit.)
  await page.keyboard.press("Meta+A").catch(() => {});
  await page.keyboard.press("Backspace").catch(() => {});
  // Exit reply/menus if any.
  await page.keyboard.press("Escape").catch(() => {});
  await page.waitForTimeout(80);
  await page.keyboard.press("Escape").catch(() => {});
}

async function main() {
  const outDir = path.resolve(process.cwd(), "output");
  fs.mkdirSync(outDir, { recursive: true });
  const ts = new Date().toISOString().replace(/[:.]/g, "-");
  // Default headless to avoid popping windows / stealing focus. Pass --headed to show UI.
  const headless = !process.argv.includes("--headed");

  const context = await chromium.launchPersistentContext(path.resolve(process.cwd(), "user-data"), {
    headless,
    viewport: { width: 1400, height: 900 },
    args: ["--disable-dev-shm-usage"],
  });
  const page = context.pages()[0] ?? (await context.newPage());
  page.setDefaultTimeout(60_000);

  await gotoChannel(page, CHANNEL_GENERAL_ENGLISH);
  await clearComposer(page);

  const shot = path.join(outDir, `composer-cleared-${ts}.png`);
  await page.screenshot({ path: shot, fullPage: false });

  await context.close();
  console.log(JSON.stringify({ ok: true, screenshot: shot }, null, 2));
}

main().catch((err) => {
  console.error(err?.stack || String(err));
  process.exit(1);
});
