import path from "node:path";
import { chromium } from "playwright";

const DEFAULT_GUILD_ID = "1404726112159793172";
const DEFAULT_CHANNEL_GENERAL_ENGLISH = "1404870331759591575";

function argVal(flag, def = null) {
  const i = process.argv.indexOf(flag);
  if (i === -1) return def;
  return process.argv[i + 1] ?? def;
}

function hasFlag(flag) {
  return process.argv.includes(flag);
}

async function gotoChannel(page, guildId, channelId) {
  const url = `https://discord.com/channels/${guildId}/${channelId}`;
  await page.goto(url, { waitUntil: "networkidle" });
  await page.waitForTimeout(1500);
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

async function findVisibleCandidateLiIds(page, { authorIncludes = "oysterguard" } = {}) {
  return await page.evaluate(({ authorIncludesInner }) => {
    const want = (authorIncludesInner || "").toLowerCase();
    const lis = Array.from(document.querySelectorAll('li[id^="chat-messages-"]'));
    const out = [];

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

      // Heuristic: template dump markers (EN). We only use this for smoke coverage.
      const hit =
        text.includes("Sorry about this") ||
        text.includes("Share what you see in-app") ||
        text.includes("Founder Pass") ||
        text.includes("OYS") ||
        text.includes("We'll start posting dated updates");

      if (hit) out.push({ liId: li.id, preview: text.slice(0, 120) });
    }

    return out.slice(-10);
  }, { authorIncludesInner: authorIncludes });
}

async function findAnyVisibleLiId(page) {
  return await page.evaluate(() => {
    const li = Array.from(document.querySelectorAll('li[id^="chat-messages-"]')).pop();
    return li?.id || null;
  });
}

async function openDeleteMenuViaTime(page, liId) {
  const li = page.locator(`li[id="${liId}"]`).first();
  await li.waitFor({ timeout: 20_000 });
  await li.scrollIntoViewIfNeeded();
  await li.hover().catch(() => {});
  await page.keyboard.press("Escape").catch(() => {});
  await page.waitForTimeout(80);

  const timeEl = li.locator("time").first();
  if (await timeEl.count()) {
    await timeEl.click({ button: "right", force: true, timeout: 5_000 });
    return;
  }
  const contentEl = li.locator('[id^="message-content-"]').first();
  if (await contentEl.count()) {
    await contentEl.click({ button: "right", force: true, timeout: 5_000 });
    return;
  }
  await li.click({ button: "right", force: true, timeout: 5_000 });
}

async function assertDeleteMenuItemVisible(page) {
  const del = page.locator(
    [
      '[role="menuitem"][data-list-item-id*="delete"]',
      '[role="menuitem"]:has-text("删除信息")',
      '[role="menuitem"]:has-text("删除消息")',
      '[role="menuitem"]:has-text("Delete Message")',
    ].join(", ")
  ).first();
  await del.waitFor({ timeout: 8_000 });
}

async function assertReplyMenuItemVisible(page) {
  const reply = page
    .locator('[role="menuitem"]:has-text("回复"), [role="menuitem"]:has-text("Reply")')
    .first();
  await reply.waitFor({ timeout: 8_000 });
}

async function openReplyUI(page, liId) {
  const li = page.locator(`li[id="${liId}"]`).first();
  await li.waitFor({ timeout: 20_000 });
  await li.scrollIntoViewIfNeeded();
  await li.hover().catch(() => {});

  const replyBtn = li.locator('[aria-label="回复"], [aria-label="Reply"]').first();
  if (await replyBtn.count()) {
    await replyBtn.click({ timeout: 5_000 });
  } else {
    await openDeleteMenuViaTime(page, liId);
    const menuItem = page
      .locator('[role="menuitem"]:has-text("回复"), [role="menuitem"]:has-text("Reply")')
      .first();
    await menuItem.waitFor({ timeout: 8_000 });
    await menuItem.click();
  }

  const composer = page.locator('[role="textbox"][contenteditable="true"]').first();
  await composer.waitFor({ timeout: 10_000 });
  await composer.click();
  await page.keyboard.type("smoke test (no send)", { delay: 1 });
  // Cleanup: avoid sending and remove draft text.
  await page.keyboard.press("Meta+A").catch(() => {});
  await page.keyboard.press("Backspace").catch(() => {});
  await page.keyboard.press("Escape").catch(() => {});
  await page.waitForTimeout(120);
  await page.keyboard.press("Escape").catch(() => {});
}

async function main() {
  const guildId = argVal("--guild", DEFAULT_GUILD_ID);
  const channelId = argVal("--channel", DEFAULT_CHANNEL_GENERAL_ENGLISH);
  const iterations = Number(argVal("--iterations", "3"));
  const scrollSteps = Number(argVal("--scroll-up-steps", "2"));
  const userDataDir = path.resolve(process.cwd(), "user-data");
  // Default headless to avoid popping windows / stealing focus. Pass --headed to show UI.
  const headless = !process.argv.includes("--headed");

  const context = await chromium.launchPersistentContext(userDataDir, {
    headless,
    viewport: { width: 1400, height: 900 },
    args: ["--disable-dev-shm-usage"],
  });
  const page = context.pages()[0] ?? (await context.newPage());
  page.setDefaultTimeout(60_000);

  const results = [];

  for (let iter = 1; iter <= iterations; iter++) {
    const r = {
      iter,
      // "deleteMenu" is only meaningful when the picked message is ours. We treat it as best-effort.
      deleteMenu: false,
      replyUi: false,
      picked: null,
      mode: null,
      error: null,
    };
    try {
      await gotoChannel(page, guildId, channelId);

      let candidates = await findVisibleCandidateLiIds(page, { authorIncludes: "Oysterguard" });
      if (!candidates.length) {
        await scrollUp(page, scrollSteps);
        candidates = await findVisibleCandidateLiIds(page, { authorIncludes: "Oysterguard" });
      }

      if (!candidates.length) {
        // No leftover template messages (good). Run a generic check: can we open the message menu
        // and see "Reply" (prevents the link-context-menu regression).
        const anyLiId = await findAnyVisibleLiId(page);
        if (!anyLiId) {
          r.error = "no messages visible";
          results.push(r);
          continue;
        }

        r.mode = "generic";
        r.picked = { liId: anyLiId, preview: "(generic latest message)" };

        await openDeleteMenuViaTime(page, anyLiId);
        await assertReplyMenuItemVisible(page);
        r.replyUi = true;

        // Best-effort: if delete is present, record it; do not fail if absent.
        try {
          await assertDeleteMenuItemVisible(page);
          r.deleteMenu = true;
        } catch {
          r.deleteMenu = false;
        }

        await page.keyboard.press("Escape").catch(() => {});
        results.push(r);
        continue;
      }

      const picked = candidates[candidates.length - 1];
      r.picked = picked;
      r.mode = "template";

      // A: Can open delete menu and see delete item.
      await openDeleteMenuViaTime(page, picked.liId);
      await assertDeleteMenuItemVisible(page);
      r.deleteMenu = true;

      // Close menu.
      await page.keyboard.press("Escape").catch(() => {});
      await page.waitForTimeout(120);

      // C: Can open Reply UI without sending.
      await openReplyUI(page, picked.liId);
      r.replyUi = true;
    } catch (e) {
      r.error = e?.message || String(e);
      // Best-effort cleanup
      await page.keyboard.press("Escape").catch(() => {});
      await page.keyboard.press("Escape").catch(() => {});
    }
    results.push(r);
    await page.waitForTimeout(500);
  }

  await context.close();

  const ok = results.every((x) => x.replyUi);
  const out = { ok, iterations, guildId, channelId, results };
  // eslint-disable-next-line no-console
  console.log(JSON.stringify(out, null, 2));

  if (!ok && !hasFlag("--no-exit-1")) process.exit(1);
}

main().catch((err) => {
  console.error(err?.stack || String(err));
  process.exit(1);
});
