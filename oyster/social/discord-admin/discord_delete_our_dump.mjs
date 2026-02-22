import { chromium } from "playwright";

const GUILD_ID = "1404726112159793172";
const CHANNELS = {
  generalEnglish: "1404870331759591575",
  chinese: "1416430673652355112",
};

function norm(s) {
  return (s || "").replace(/^@+/, "").trim().toLowerCase();
}

async function gotoChannel(page, channelId) {
  const url = `https://discord.com/channels/${GUILD_ID}/${channelId}`;
  await page.goto(url, { waitUntil: "networkidle" });
  await page.waitForTimeout(1500);
  return url;
}

async function findDumpLiIds(page, { authorMustInclude = "oysterguard", mode = "en" }) {
  return await page.evaluate(
    ({ authorMustIncludeInner, modeInner }) => {
      const wantAuthor = (authorMustIncludeInner || "").toLowerCase();
      const lis = Array.from(document.querySelectorAll('li[id^="chat-messages-"]'));
      const out = [];

      for (const li of lis) {
        const author =
          (li.querySelector('span[class*="username"]')?.textContent ||
            li.querySelector("h3")?.textContent ||
            "")
            .trim();
        const authorNorm = author.toLowerCase();
        if (wantAuthor && !authorNorm.includes(wantAuthor)) continue;

        const contentNodes = Array.from(li.querySelectorAll('[id^="message-content-"]'));
        const text = contentNodes.map((n) => n.innerText || n.textContent || "").join("\n").trim();
        if (!text) continue;

        const mentionLines = (text.match(/@\S+:/g) || []).length;
        const sorryCount = (text.match(/Sorry about this\./g) || []).length;

        let hit = false;
        if (modeInner === "en") {
          hit =
            text.includes("Quick support roundup") ||
            mentionLines >= 2 ||
            sorryCount >= 2 ||
            // Also delete the recent per-user template posts (still not threaded replies).
            ((text.startsWith("@") || text.includes("@")) &&
              (text.includes("Share what you see in-app") ||
                text.includes("Share your wallet") ||
                text.includes("DM your order") ||
                text.includes("DM order") ||
                text.includes("order #") ||
                text.includes("We'll post dated updates") ||
                text.includes("We'll start posting dated updates") ||
                text.includes("dated updates")));
        } else {
          hit =
            text.includes("大家好，我在集中处理") ||
            text.includes("为了我能马上推进") ||
            text.includes("你遇到的问题截图") ||
            text.includes("不方便公开") ||
            // Also delete short per-user template posts to re-do as real threaded replies.
            (text.includes("把钱包地址") ||
              text.includes("订单号") ||
              text.includes("复现步骤") ||
              text.includes("不方便公开就私信")) &&
              text.includes("@");
        }

        if (hit) out.push({ liId: li.id, preview: text.slice(0, 140) });
      }
      // Return more than a screenful; virtualized scrolling means we need to process in batches.
      return out.slice(-60);
    },
    { authorMustIncludeInner: authorMustInclude, modeInner: mode }
  );
}

async function deleteMessageByLiId(page, liId) {
  const li = page.locator(`li[id="${liId}"]`).first();
  await li.waitFor({ timeout: 15_000 });

  // Clear any stale menus/overlays that can steal pointer events.
  await page.keyboard.press("Escape").catch(() => {});
  await page.waitForTimeout(80);

  // Discord can show different context menus depending on which sub-node you right-click.
  // Some message bodies get intercepted by layerContainer/clickTrap and only show a minimal menu.
  // Empirically, right-clicking the <time> element is much more reliable for opening the full menu.
  const timeEl = li.locator("time").first();
  const contentEl = li.locator('[id^="message-content-"]').first();

  const tryOpenMenu = async () => {
    if (await timeEl.count()) {
      await timeEl.click({ button: "right", force: true, timeout: 5_000 });
      return;
    }
    if (await contentEl.count()) {
      await contentEl.click({ button: "right", force: true, timeout: 5_000 });
      return;
    }
    await li.click({ button: "right", force: true, timeout: 5_000 });
  };

  try {
    await tryOpenMenu();
  } catch {
    // Fallback to the "More" button path if context menu is blocked.
    const moreBtn = li.locator('[aria-label="更多"], [aria-label="More"]').first();
    if (await moreBtn.count()) {
      await moreBtn.click({ timeout: 5_000 }).catch(() => {});
    } else {
      await li.click({ button: "right", force: true, timeout: 5_000 }).catch(() => {});
    }
  }

  const del = page
    .locator(
      [
        // Discord uses stable data-list-item-id in some builds.
        '[role="menuitem"][data-list-item-id*="delete"]',
        // Chinese UI (observed): "删除信息" (sometimes also "删除消息").
        '[role="menuitem"]:has-text("删除信息")',
        '[role="menuitem"]:has-text("删除消息")',
        // English UI.
        '[role="menuitem"]:has-text("Delete Message")',
      ].join(", ")
    )
    .first();
  await del.waitFor({ timeout: 10_000 });
  await del.click();

  const confirm = page.locator('button:has-text("删除"), button:has-text("Delete")').first();
  await confirm.waitFor({ timeout: 10_000 });
  await confirm.click();

  await page.waitForTimeout(800);
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

async function main() {
  // Default headless to avoid popping windows / stealing focus. Pass --headed to show UI.
  const headless = !process.argv.includes("--headed");
  const context = await chromium.launchPersistentContext("./user-data", {
    headless,
    viewport: { width: 1400, height: 900 },
    args: ["--disable-dev-shm-usage"],
  });
  const page = context.pages()[0] ?? (await context.newPage());
  page.setDefaultTimeout(60_000);

  // General English: delete our dump(s)
  await gotoChannel(page, CHANNELS.generalEnglish);
  {
    let noHitStreak = 0;
    for (let pass = 0; pass < 80; pass++) {
      const en = await findDumpLiIds(page, { authorMustInclude: "Oysterguard", mode: "en" });
      if (!en.length) {
        noHitStreak++;
        if (noHitStreak >= 10) break;
        await scrollUp(page, 2);
        continue;
      }

      noHitStreak = 0;
      for (const c of en) {
        try {
          await deleteMessageByLiId(page, c.liId);
        } catch {
          // best-effort
        }
      }
      // After deleting, scan again without scrolling to catch leftovers at the same position.
      await page.waitForTimeout(650);
    }
  }

  // Chinese: delete our earlier long helper message fragments if present
  await gotoChannel(page, CHANNELS.chinese);
  {
    let noHitStreak = 0;
    for (let pass = 0; pass < 80; pass++) {
      const zh = await findDumpLiIds(page, { authorMustInclude: "Oysterguard", mode: "zh" });
      if (!zh.length) {
        noHitStreak++;
        if (noHitStreak >= 10) break;
        await scrollUp(page, 2);
        continue;
      }

      noHitStreak = 0;
      for (const c of zh) {
        try {
          await deleteMessageByLiId(page, c.liId);
        } catch {
          // best-effort
        }
      }
      await page.waitForTimeout(650);
    }
  }

  await context.close();
}

main().catch((err) => {
  console.error(err?.stack || String(err));
  process.exit(1);
});
