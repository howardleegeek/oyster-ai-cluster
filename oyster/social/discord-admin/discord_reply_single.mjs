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

async function main() {
  const messageId = argVal("--message");
  const channelId = argVal("--channel", DEFAULT_CHANNEL_ID);
  const text = argVal("--text");
  if (!messageId || !text) {
    console.error(
      'Usage: node discord_reply_single.mjs --message <messageId> --text "<reply>" [--channel <channelId>] [--headed]'
    );
    process.exit(2);
  }

  const headless = !hasFlag("--headed");
  const outDir = path.resolve(process.cwd(), "output");
  fs.mkdirSync(outDir, { recursive: true });
  const ts = new Date().toISOString().replace(/[:.]/g, "-");

  const userDataDir = path.resolve(process.cwd(), "user-data");
  const context = await chromium.launchPersistentContext(userDataDir, {
    headless,
    viewport: { width: 1400, height: 900 },
    args: ["--disable-dev-shm-usage"],
  });
  const page = context.pages()[0] ?? (await context.newPage());
  page.setDefaultTimeout(60_000);

  const url = `https://discord.com/channels/${GUILD_ID}/${channelId}/${messageId}`;
  await page.goto(url, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(1800);

  const liId = `chat-messages-${channelId}-${messageId}`;
  const li = page.locator(`li[id="${liId}"]`).first();
  await li.waitFor({ timeout: 30_000 });
  await li.scrollIntoViewIfNeeded();
  await li.hover().catch(() => {});
  await page.waitForTimeout(250);

  const snap = async (label) => {
    const p = path.join(outDir, `single-reply-${channelId}-${messageId}-${label}-${ts}.png`);
    await page.screenshot({ path: p, fullPage: false }).catch(() => {});
    return p;
  };

  // Open message context menu by right-clicking the timestamp. This avoids link-context menus.
  const timeEl = li.locator("time").first();
  if (!(await timeEl.count())) throw new Error("no_time_element_on_message");
  await timeEl.click({ button: "right", force: true, timeout: 5_000 });
  await page.waitForTimeout(250);
  await snap("after-context");

  // Click the menu item "回复"/"Reply" via DOM to avoid flaky visibility checks.
  const clicked = await page.evaluate(() => {
    const menus = Array.from(document.querySelectorAll('[role="menu"]'));
    for (const menu of menus) {
      const items = Array.from(menu.querySelectorAll('[role="menuitem"]'));
      const hit = items.find((n) => {
        const t = (n.textContent || "").trim();
        return t === "回复" || t === "Reply";
      });
      if (hit) {
        (hit).click();
        return true;
      }
    }
    return false;
  });
  if (!clicked) {
    await snap("no-reply-item");
    throw new Error("reply_menu_item_not_found");
  }

  await page.waitForTimeout(600);
  await snap("after-click-reply");

  const composer = page.locator('[role="textbox"][contenteditable="true"]').first();
  await composer.waitFor({ timeout: 15_000 });

  // Verify reply mode by checking composer form text contains "正在回复" / "Replying to".
  const form = composer.locator("xpath=ancestor::form[1]");
  const formText = ((await form.textContent().catch(() => "")) || "").replace(/\s+/g, " ").trim();
  if (!formText.includes("正在回复") && !formText.toLowerCase().includes("replying to")) {
    await snap("not-reply-mode");
    throw new Error("not_in_reply_mode(refusing_to_send)");
  }

  // Send short single-line reply.
  let t = String(text || "").replace(/\s+/g, " ").trim();
  if (t.length > 280) t = t.slice(0, 277) + "...";
  await composer.click();
  await page.keyboard.type(t, { delay: 2 });
  await page.keyboard.press("Enter");

  await page.waitForTimeout(1200);
  await snap("sent");

  await context.close();
  console.log(JSON.stringify({ ok: true, url }, null, 2));
}

main().catch((err) => {
  console.error(err?.stack || String(err));
  process.exit(1);
});

