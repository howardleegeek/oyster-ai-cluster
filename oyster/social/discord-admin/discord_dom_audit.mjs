import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

function ts() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  return (
    d.getFullYear() +
    pad(d.getMonth() + 1) +
    pad(d.getDate()) +
    "-" +
    pad(d.getHours()) +
    pad(d.getMinutes()) +
    pad(d.getSeconds())
  );
}

function mkdirp(p) {
  fs.mkdirSync(p, { recursive: true });
}

function writeJson(p, obj) {
  fs.writeFileSync(p, JSON.stringify(obj, null, 2));
}

function extractGuildAndChannel(urlStr) {
  try {
    const u = new URL(urlStr);
    const m = u.pathname.match(/^\/channels\/(\d+)\/(\d+)/);
    if (!m) return null;
    return { guildId: m[1], channelId: m[2] };
  } catch {
    return null;
  }
}

async function main() {
  const targetUrl = process.argv[2];
  if (!targetUrl) {
    console.error("Usage: node discord_dom_audit.mjs <discord channel url>");
    process.exit(2);
  }
  // Default headless to avoid popping windows / stealing focus. Pass --headed to show UI.
  const headless = !process.argv.includes("--headed");

  const baseDir = path.resolve(process.cwd(), "audit");
  const runDir = path.join(baseDir, ts());
  mkdirp(runDir);

  const userDataDir = path.resolve(process.cwd(), "user-data");
  mkdirp(userDataDir);

  const context = await chromium.launchPersistentContext(userDataDir, {
    headless,
    viewport: { width: 1400, height: 900 },
    args: ["--disable-dev-shm-usage"],
  });

  const page = context.pages()[0] ?? (await context.newPage());
  page.setDefaultTimeout(60_000);

  await page.goto(targetUrl, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(1500);

  const deadlineMs = Date.now() + 5 * 60_000;
  let ids = extractGuildAndChannel(page.url());
  while (!ids && Date.now() < deadlineMs) {
    await page.waitForTimeout(1000);
    ids = extractGuildAndChannel(page.url());
  }

  // If still not in /channels/..., likely sitting at login.
  const isLoggedIn = !!ids;

  // Extract via ARIA where possible (Discord's classnames are unstable).
  const data = await page.evaluate(() => {
    const bySelText = (sel) => {
      const el = document.querySelector(sel);
      return (el?.textContent || "").trim() || null;
    };

    const pickFirst = (sels) => {
      for (const s of sels) {
        const el = document.querySelector(s);
        if (el) return el;
      }
      return null;
    };

    const guildNameEl = pickFirst([
      // Often the server name is the first h1 in the header region.
      'h1[role="button"]',
      "header h1",
      'header [class*="name"]',
    ]);
    const guildName = (guildNameEl?.textContent || "").trim() || null;

    const channelHeaderEl = pickFirst([
      '[aria-label^="Channel header"]',
      '[data-list-item-id^="channels___"]',
      "main header",
    ]);
    const channelHeaderText = (channelHeaderEl?.textContent || "").trim() || null;

    // Channel list: look for elements with data-list-item-id channels___<id>
    const channelItems = Array.from(
      document.querySelectorAll('[data-list-item-id^="channels___"]')
    )
      .map((el) => {
        const id = el.getAttribute("data-list-item-id") || "";
        const name = (el.textContent || "").trim();
        const aria = el.getAttribute("aria-label") || null;
        return { id, name, aria };
      })
      .filter((x) => x.name)
      .slice(0, 500);

    // Category headings: best-effort (Discord uses role="button" for collapsers).
    const categoryCandidates = Array.from(
      document.querySelectorAll('nav [role="button"], nav h2, nav h3')
    )
      .map((el) => (el.textContent || "").trim())
      .filter((t) => t && t.length < 80)
      .slice(0, 200);

    // Member list existence check.
    const memberListPresent =
      !!document.querySelector('[aria-label*="Members"]') ||
      !!document.querySelector('[data-list-id="members"]');

    // Message input placeholder/label.
    const composer =
      document.querySelector('[role="textbox"][data-slate-editor="true"]') ||
      document.querySelector('[role="textbox"][contenteditable="true"]');
    const composerAria = composer?.getAttribute("aria-label") || null;

    const title = document.title || null;
    return {
      title,
      guildName,
      channelHeaderText,
      channelItemsCount: channelItems.length,
      channelItems,
      categoryCandidates,
      memberListPresent,
      composerAria,
      locationHref: location.href,
    };
  });

  await page.screenshot({ path: path.join(runDir, "current.png"), fullPage: true });

  writeJson(path.join(runDir, "result.json"), {
    ok: true,
    startedFrom: targetUrl,
    finalUrl: page.url(),
    isLoggedIn,
    ids,
    extracted: data,
    outputDir: runDir,
  });

  await context.close();
}

main().catch((err) => {
  try {
    fs.writeFileSync(
      path.resolve(process.cwd(), "audit_crash.txt"),
      String(err?.stack || err)
    );
  } catch {}
  process.exit(1);
});
