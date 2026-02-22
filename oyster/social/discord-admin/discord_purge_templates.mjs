import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

const GUILD_ID = "1404726112159793172";
const CHANNEL_GENERAL_ENGLISH = "1404870331759591575";

function argVal(flag, def = null) {
  const i = process.argv.indexOf(flag);
  if (i === -1) return def;
  return process.argv[i + 1] ?? def;
}

async function gotoChannel(page, channelId) {
  const url = `https://discord.com/channels/${GUILD_ID}/${channelId}`;
  await page.goto(url, { waitUntil: "networkidle" });
  await page.waitForTimeout(1500);
  return url;
}

async function gotoMessage(page, channelId, messageId) {
  const url = `https://discord.com/channels/${GUILD_ID}/${channelId}/${messageId}`;
  await page.goto(url, { waitUntil: "networkidle" });
  await page.waitForTimeout(1200);
  return url;
}

async function scrollUp(page, steps = 1) {
  for (let i = 0; i < steps; i++) {
    await page.evaluate(() => {
      const scroller =
        document.querySelector("main div.scroller__36d07") ||
        Array.from(document.querySelectorAll("main div")).find((el) => {
          const st = getComputedStyle(el);
          return (
            (st.overflowY === "scroll" || st.overflowY === "auto") &&
            el.scrollHeight > el.clientHeight + 20
          );
        });
      if (!scroller) return;
      scroller.scrollTop = Math.max(0, scroller.scrollTop - scroller.clientHeight * 0.95);
    });
    await page.waitForTimeout(650);
  }
}

async function collectVisibleTemplateMessageIds(page, { authorIncludes = "oysterguard" } = {}) {
  return await page.evaluate(({ authorIncludesInner }) => {
    const want = (authorIncludesInner || "").toLowerCase();
    const lis = Array.from(document.querySelectorAll('li[id^="chat-messages-"]'));
    const ids = [];

    for (const li of lis) {
      const author =
        (li.querySelector('span[class*="username"]')?.textContent ||
          li.querySelector("h3")?.textContent ||
          "")
          .trim();
      if (want && !author.toLowerCase().includes(want)) continue;

      const contentNodes = Array.from(li.querySelectorAll('[id^="message-content-"]'));
      const text = contentNodes.map((n) => n.innerText || n.textContent || "").join("\n").trim();
      if (!text) continue;

      // Template markers (EN/ZH-lite).
      const looksTemplate =
        text.includes("Sorry about this") ||
        text.includes("Share what you see in-app") ||
        text.includes("Founder Pass") ||
        text.includes("OYS") ||
        text.includes("DM") ||
        text.includes("dated updates") ||
        text.includes("不方便公开") ||
        (text.match(/@\\S+:/g) || []).length >= 1;
      if (!looksTemplate) continue;

      const parts = li.id.split("-");
      const messageId = parts[parts.length - 1];
      ids.push(messageId);
    }

    // De-dupe while preserving order.
    return Array.from(new Set(ids));
  }, { authorIncludesInner: authorIncludes });
}

async function deleteByPermalink(page, channelId, messageId) {
  await gotoMessage(page, channelId, messageId);
  const liId = `chat-messages-${channelId}-${messageId}`;
  const li = page.locator(`li[id="${liId}"]`).first();
  await li.waitFor({ timeout: 30_000 });
  await li.scrollIntoViewIfNeeded();
  await li.hover().catch(() => {});

  await page.keyboard.press("Escape").catch(() => {});
  await page.waitForTimeout(80);

  const timeEl = li.locator("time").first();
  if (await timeEl.count()) {
    await timeEl.click({ button: "right", force: true, timeout: 5_000 });
  } else {
    await li.click({ button: "right", force: true, timeout: 5_000 });
  }

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
}

async function main() {
  const channelId = argVal("--channel", CHANNEL_GENERAL_ENGLISH);
  const rounds = Number(argVal("--rounds", "20"));
  const scrollSteps = Number(argVal("--scroll-up-steps", "2"));
  // Default headless to avoid popping windows / stealing focus. Pass --headed to show UI.
  const headless = !process.argv.includes("--headed");

  const outDir = path.resolve(process.cwd(), "output");
  fs.mkdirSync(outDir, { recursive: true });
  const tsBase = new Date().toISOString().replace(/[:.]/g, "-");

  const context = await chromium.launchPersistentContext(path.resolve(process.cwd(), "user-data"), {
    headless,
    viewport: { width: 1400, height: 900 },
    args: ["--disable-dev-shm-usage"],
  });
  const page = context.pages()[0] ?? (await context.newPage());
  page.setDefaultTimeout(60_000);

  const run = {
    startedAt: new Date().toISOString(),
    channelId,
    rounds,
    scrollSteps,
    deleted: [],
    errors: [],
  };

  await gotoChannel(page, channelId);

  for (let r = 1; r <= rounds; r++) {
    await scrollUp(page, scrollSteps);

    const ids = await collectVisibleTemplateMessageIds(page, { authorIncludes: "Oysterguard" });
    const shot = path.join(outDir, `purge-round-${tsBase}-r${r}.png`);
    await page.screenshot({ path: shot, fullPage: false });

    if (!ids.length) break;

    for (const messageId of ids) {
      try {
        await deleteByPermalink(page, channelId, messageId);
        run.deleted.push({ messageId, round: r });
      } catch (e) {
        const errShot = path.join(outDir, `purge-error-${tsBase}-r${r}-${messageId}.png`);
        await page.screenshot({ path: errShot, fullPage: false }).catch(() => {});
        run.errors.push({
          messageId,
          round: r,
          error: e?.message || String(e),
          screenshot: errShot,
        });
      }
    }

    // Return to channel after batch to keep scrolling.
    await gotoChannel(page, channelId);
  }

  await context.close();

  const outJson = path.join(outDir, `purge-run-${tsBase}.json`);
  fs.writeFileSync(outJson, JSON.stringify(run, null, 2));
  console.log(JSON.stringify({ ok: run.errors.length === 0, outJson, deleted: run.deleted.length, errors: run.errors.length }, null, 2));
  if (run.errors.length) process.exit(1);
}

main().catch((err) => {
  console.error(err?.stack || String(err));
  process.exit(1);
});
