import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

const GUILD_ID = "1404726112159793172";
const CHANNEL_GENERAL_ENGLISH = "1404870331759591575";

async function gotoChannel(page, channelId) {
  const url = `https://discord.com/channels/${GUILD_ID}/${channelId}`;
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

async function collectVisibleOysterguardMessages(page) {
  const includeAll = process.argv.includes("--all");
  return await page.evaluate(({ includeAllInner }) => {
    const lis = Array.from(document.querySelectorAll('li[id^="chat-messages-"]'));
    const out = [];
    for (const li of lis) {
      const author =
        (li.querySelector('span[class*="username"]')?.textContent ||
          li.querySelector("h3")?.textContent ||
          "")
          .trim();
      if (!author.toLowerCase().includes("oysterguard")) continue;

      const contentNodes = Array.from(li.querySelectorAll('[id^="message-content-"]'));
      const text = contentNodes.map((n) => n.innerText || n.textContent || "").join("\n").trim();
      if (!text) continue;

      if (!includeAllInner) {
        // Only keep likely-template posts.
        const looksTemplate =
          text.includes("Sorry about this") ||
          text.includes("Share what you see in-app") ||
          text.includes("Founder Pass") ||
          text.includes("OYS") ||
          text.includes("DM") ||
          text.includes("dated updates") ||
          (text.match(/@\\S+:/g) || []).length >= 1;
        if (!looksTemplate) continue;
      }

      // Extract messageId from li.id: chat-messages-<channelId>-<messageId>
      const parts = li.id.split("-");
      const messageId = parts[parts.length - 1];
      out.push({
        liId: li.id,
        messageId,
        preview: text.slice(0, 160),
      });
    }
    return out;
  }, { includeAllInner: includeAll });
}

async function main() {
  const outDir = path.resolve(process.cwd(), "output");
  fs.mkdirSync(outDir, { recursive: true });
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

  // Try a couple scroll-ups to catch older leftovers in view.
  await scrollUp(page, 2);

  const messages = await collectVisibleOysterguardMessages(page);

  const ts = new Date().toISOString().replace(/[:.]/g, "-");
  const screenshotPath = path.join(outDir, `discord-state-${ts}.png`);
  await page.screenshot({ path: screenshotPath, fullPage: false });

  const jsonPath = path.join(outDir, `discord-state-${ts}.json`);
  fs.writeFileSync(jsonPath, JSON.stringify({ screenshotPath, messages }, null, 2));

  await context.close();

  console.log(JSON.stringify({ screenshotPath, jsonPath, count: messages.length, messages }, null, 2));
}

main().catch((err) => {
  console.error(err?.stack || String(err));
  process.exit(1);
});
