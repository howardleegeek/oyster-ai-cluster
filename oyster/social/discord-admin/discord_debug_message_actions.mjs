import { chromium } from "playwright";
import path from "node:path";
import fs from "node:fs";

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

async function main() {
  const messageId = argVal("--message");
  const channelId = argVal("--channel", DEFAULT_CHANNEL_ID);
  if (!messageId) {
    console.error("Usage: node discord_debug_message_actions.mjs --message <messageId> [--channel <channelId>]");
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

  // Hover to reveal the message toolbar.
  await li.hover().catch(() => {});
  await page.waitForTimeout(350);

  // Try opening "More/更多" menu and capture any resulting menu items.
  const moreBtn = li.locator('[role="button"][aria-label="更多"], [role="button"][aria-label="More"]').first();
  if (await moreBtn.count()) {
    await moreBtn.click({ timeout: 5_000 }).catch(() => {});
    await page.waitForTimeout(300);
  }

  const info = await page.evaluate(({ liIdInner }) => {
    const li = document.getElementById(liIdInner);
    if (!li) return { ok: false, error: "li_not_found" };

    const pickAttrs = (el) => {
      const out = {};
      for (const k of ["aria-label", "role", "data-list-item-id", "data-testid", "class"]) {
        const v = el.getAttribute(k);
        if (v) out[k] = v;
      }
      return out;
    };

    const buttons = Array.from(li.querySelectorAll("button, [role='button']"))
      .map((el) => ({
        tag: el.tagName.toLowerCase(),
        text: (el.textContent || "").trim().slice(0, 80),
        ...pickAttrs(el),
      }))
      .filter((x) => x["aria-label"] || x["data-testid"] || x.text);

    // Also check any global menus currently open.
    const menus = Array.from(document.querySelectorAll('[role="menu"]'));
    const menuItems = menus
      .flatMap((menu) =>
        Array.from(menu.querySelectorAll('[role="menuitem"]')).map((n) => (n.textContent || "").trim())
      )
      .filter(Boolean);

    return { ok: true, buttons: buttons.slice(0, 80), menuItems };
  }, { liIdInner: liId });

  const shot = path.join(outDir, `debug-actions-${channelId}-${messageId}-${ts}.png`);
  await page.screenshot({ path: shot, fullPage: false });
  await context.close();

  console.log(JSON.stringify({ url, liId, screenshot: shot, ...info }, null, 2));
}

main().catch((err) => {
  console.error(err?.stack || String(err));
  process.exit(1);
});
