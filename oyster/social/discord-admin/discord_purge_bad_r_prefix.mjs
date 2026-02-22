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

async function gotoChannel(page) {
  const url = `https://discord.com/channels/${GUILD_ID}/${CHANNEL_GENERAL_ENGLISH}`;
  await page.goto(url, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(1500);
  return url;
}

async function scrollToBottom(page) {
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
    scroller.scrollTop = scroller.scrollHeight;
  });
  await page.waitForTimeout(900);
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
    // Let virtualized history load.
    // eslint-disable-next-line no-await-in-loop
    await page.waitForTimeout(650);
  }
}

async function collectBad(page) {
  return await page.evaluate(() => {
    // Purge messages that clearly include a stray leading "r" before an English sentence,
    // e.g. "rThanks ..." or a line break then "rFair point ...".
    // Do NOT match normal "Thanks ..." replies.
    const badStart = /(^|\\n)r[A-Z]/;

    const lis = Array.from(document.querySelectorAll('li[id^="chat-messages-"]'));
    const ids = [];
    let checked = 0;
    for (const li of lis) {
      const author =
        (li.querySelector('span[class*="username"]')?.textContent ||
          li.querySelector("h3")?.textContent ||
          "")
          .trim();
      if (!author || author.toLowerCase() !== "oysterguard") continue;

      const contentNodes = Array.from(li.querySelectorAll('[id^="message-content-"]'));
      const text = contentNodes.map((n) => n.innerText || n.textContent || "").join("\n").trim();
      if (!text) continue;
      checked++;

      // Only delete the obvious wrong ones that begin with the stray "r" or the repetitive openers.
      if (!badStart.test(text)) continue;

      const mm = li.id.match(/^chat-messages-\\d+-(\\d+)$/);
      if (!mm) continue;
      ids.push(mm[1]);
    }
    return { ids: Array.from(new Set(ids)), checked, visibleLis: lis.length };
  });
}

async function deleteByPermalink(page, messageId) {
  const url = `https://discord.com/channels/${GUILD_ID}/${CHANNEL_GENERAL_ENGLISH}/${messageId}`;
  await page.goto(url, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(1200);

  const liId = `chat-messages-${CHANNEL_GENERAL_ENGLISH}-${messageId}`;
  const li = page.locator(`li[id="${liId}"]`).first();
  await li.waitFor({ timeout: 30_000 });
  await li.scrollIntoViewIfNeeded();
  await li.hover().catch(() => {});
  await page.waitForTimeout(250);

  const moreBtn = li.locator('[role="button"][aria-label="更多"], [role="button"][aria-label="More"]').first();
  if (await moreBtn.count()) {
    await moreBtn.click({ timeout: 5_000 });
  } else {
    // fallback to right-click time
    const timeEl = li.locator("time").first();
    if (await timeEl.count()) await timeEl.click({ button: "right", force: true, timeout: 5_000 });
    else await li.click({ button: "right", force: true, timeout: 5_000 });
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
  await page.waitForTimeout(900);

  return { messageId, url };
}

async function main() {
  const rounds = Number(argVal("--rounds", "8"));
  const scanScrollUps = Number(argVal("--scan-scroll-ups", "8"));
  const delayMs = Number(argVal("--delay-ms", "600"));
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

  const run = { startedAt: new Date().toISOString(), deleted: [], errors: [] };
  const debug = [];

  await gotoChannel(page);
  await scrollToBottom(page);

  for (let r = 1; r <= rounds; r++) {
    const seen = new Set();
    // Scan bottom + a few scroll-ups (bad messages may be slightly above).
    for (let i = 0; i < scanScrollUps; i++) {
      const got = await collectBad(page);
      debug.push({ round: r, scan: i + 1, ...got });
      for (const id of got.ids) seen.add(id);
      await scrollUp(page, 1);
    }

    const ids = Array.from(seen);
    if (!ids.length) break;

    for (const id of ids) {
      try {
        const d = await deleteByPermalink(page, id);
        run.deleted.push({ round: r, ...d });
        if (delayMs) await page.waitForTimeout(delayMs);
      } catch (e) {
        const shot = path.join(outDir, `purge-bad-r-error-${ts}-r${r}-${id}.png`);
        await page.screenshot({ path: shot, fullPage: false }).catch(() => {});
        run.errors.push({ round: r, messageId: id, error: e?.message || String(e), screenshot: shot });
        if (delayMs) await page.waitForTimeout(delayMs);
      }
    }

    // Return to channel and re-scan at the bottom.
    await gotoChannel(page);
    await scrollToBottom(page);
  }

  await context.close();
  const outJson = path.join(outDir, `purge-bad-r-${ts}.json`);
  fs.writeFileSync(outJson, JSON.stringify({ ...run, debug }, null, 2));
  console.log(JSON.stringify({ ok: run.errors.length === 0, outJson, deleted: run.deleted.length, errors: run.errors.length }, null, 2));
  if (run.errors.length) process.exit(1);
}

main().catch((err) => {
  console.error(err?.stack || String(err));
  process.exit(1);
});
