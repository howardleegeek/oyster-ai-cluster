import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

function readJson(p) {
  return JSON.parse(fs.readFileSync(p, "utf8"));
}

function writeJson(p, obj) {
  fs.writeFileSync(p, JSON.stringify(obj, null, 2));
}

function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith("--")) {
      out._.push(a);
      continue;
    }
    const k = a.slice(2);
    if (k === "dry-run") out.dryRun = true;
    else if (k === "headless") out.headless = true;
    else if (k === "headed") out.headed = true;
    else if (k === "retry-failed") out.retryFailed = true;
    else {
      out[k] = argv[i + 1];
      i++;
    }
  }
  return out;
}

async function gotoMessage(page, url) {
  // Discord keeps long-lived connections; "domcontentloaded" is more stable than "networkidle".
  await page.goto(url, { waitUntil: "domcontentloaded" });
  await page.waitForSelector("main", { timeout: 30_000 }).catch(() => {});
  await page.waitForTimeout(1800);
}

async function openReplyBox(page, liId) {
  const sel = `li[id="${liId}"]`;
  const m = String(liId).match(/^chat-messages-(\d+)-(\d+)$/);
  const channelId = m?.[1] || "unknown";
  const messageId = m?.[2] || "unknown";
  const ts = new Date().toISOString().replace(/[:.]/g, "-");
  const outDir = path.resolve(process.cwd(), "output");
  fs.mkdirSync(outDir, { recursive: true });
  const snap = async (label) => {
    const p = path.join(outDir, `reply-open-${channelId}-${messageId}-${label}-${ts}.png`);
    await page.screenshot({ path: p, fullPage: false }).catch(() => {});
    return p;
  };

  // Sometimes permalinks load but the specific message isn't rendered immediately (virtualized list).
  // Keep this function deterministic and well-instrumented; avoid long waits without a snapshot.
  await snap("start");

  const li = page.locator(sel).first();
  const hasLi = await li
    .waitFor({ timeout: 30_000 })
    .then(() => true)
    .catch(() => false);
  if (!hasLi) {
    await snap("no-li");
    throw new Error("message_not_rendered(li_not_visible)");
  }

  const composer = page.locator('[role="textbox"][contenteditable="true"]').first();
  const isInReplyMode = async () => {
    // Reply mode adds a reply header inside the composer form.
    // CN UI example: "正在回复至 <user>".
    const form = composer.locator("xpath=ancestor::form[1]");
    const indicator = form.locator(':text-matches("replying to|正在回复", "i")').first();
    if ((await indicator.count().catch(() => 0)) > 0) return true;
    const txt = (await form.textContent({ timeout: 1000 }).catch(() => "")) || "";
    return txt.includes("正在回复") || txt.toLowerCase().includes("replying to");
  };

  // Hover message -> click hoverbar More/更多 -> menu item Reply/回复
  const replyMenuItem = page
    .locator('[role="menuitem"]:has-text("回复"), [role="menuitem"]:has-text("Reply")')
    .first();
  const moreBtnSel = [
    '[role="button"][aria-label="更多"]',
    '[role="button"][aria-label="More"]',
    'button[aria-label="更多"]',
    'button[aria-label="More"]',
    'div[role="button"][aria-label="更多"]',
    'div[role="button"][aria-label="More"]',
  ].join(", ");

  for (let attempt = 1; attempt <= 3; attempt++) {
    await li.scrollIntoViewIfNeeded({ timeout: 8_000 }).catch(() => {});
    const content = li.locator('[id^="message-content-"]').first();
    if ((await content.count().catch(() => 0)) > 0) {
      await content.hover({ timeout: 3_000 }).catch(() => {});
    } else {
      await li.hover({ timeout: 3_000 }).catch(() => {});
    }
    await page.waitForTimeout(200 + attempt * 150);
    await snap(`after-hover-a${attempt}`);

    const moreBtn = li.locator(moreBtnSel).first();
    if ((await moreBtn.count().catch(() => 0)) <= 0) {
      await snap(`no-more-a${attempt}`);
      continue;
    }

    await moreBtn.click({ timeout: 5_000 }).catch(() => {});
    await page.waitForTimeout(250);
    await snap(`after-more-a${attempt}`);

    const hasReply = await replyMenuItem
      .waitFor({ timeout: 6_000, state: "visible" })
      .then(() => true)
      .catch(() => false);
    if (!hasReply) {
      await snap(`no-reply-item-a${attempt}`);
      continue;
    }

    await replyMenuItem.click({ timeout: 5_000, force: true }).catch(() => {});
    await page.waitForTimeout(350);
    await snap(`after-click-reply-a${attempt}`);

    if (await isInReplyMode()) return;
  }

  // Last fallback: Discord has a keyboard shortcut `r` to reply to the currently focused message.
  // We only use it after forcing focus onto the message content to avoid typing `r` into the composer.
  {
    const content = li.locator('[id^="message-content-"]').first();
    if ((await content.count().catch(() => 0)) > 0) {
      await content.click({ timeout: 5_000 }).catch(() => {});
      await page.waitForTimeout(120);
      await page.keyboard.press("r").catch(() => {});
      await page.waitForTimeout(500);
      await snap("after-key-r");
      if (await isInReplyMode()) return;
    }
  }

  await snap("failed");
  throw new Error("open_reply_ui_failed");
}

async function typeAndSend(page, text) {
  const composer = page.locator('[role="textbox"][contenteditable="true"]').first();
  await composer.waitFor({ timeout: 60_000 });
  await composer.click();

  // Safety: ensure we're in reply mode (avoid posting a standalone message).
  const form = composer.locator("xpath=ancestor::form[1]");
  const formText = (await form.textContent().catch(() => "")) || "";
  const inReplyMode = formText.includes("正在回复") || formText.toLowerCase().includes("replying to");
  if (!inReplyMode) throw new Error("not_in_reply_mode(refusing_to_send)");

  // Keep messages short: single paragraph, no accidental leading shortcut chars.
  let t = String(text || "");
  t = t.replace(/^\s*r(?=[A-Z])/g, ""); // e.g. "rThanks..." from stray shortcut
  t = t.replace(/\s+/g, " ").trim();
  if (t.length > 280) t = t.slice(0, 277) + "...";

  await page.keyboard.type(t, { delay: 2 });
  await page.keyboard.press("Enter");
}

function resolveTargetsFromRunDir(runDir) {
  // Best-effort: map author -> last message (channelId, messageId) from messages_*.json under runDir.
  const files = fs
    .readdirSync(runDir)
    .filter((f) => f.startsWith("messages_") && f.endsWith(".json"))
    .map((f) => path.join(runDir, f));

  const byAuthor = new Map();
  for (const f of files) {
    let d;
    try {
      d = JSON.parse(fs.readFileSync(f, "utf8"));
    } catch {
      continue;
    }
    const msgs = Array.isArray(d.messages) ? d.messages : [];
    for (const m of msgs) {
      const author = (m.author || "").trim();
      const liId = m.liId || m.id || "";
      const mm = String(liId).match(/^chat-messages-(\d+)-(\d+)$/);
      if (!author || !mm) continue;
      const channelId = mm[1];
      const messageId = mm[2];
      const ts = m.ts ? Date.parse(m.ts) : NaN;
      const prev = byAuthor.get(author);
      const prevTs = prev?.ts ? Date.parse(prev.ts) : NaN;
      if (!prev || (Number.isFinite(ts) && (!Number.isFinite(prevTs) || ts >= prevTs))) {
        byAuthor.set(author, { channelId, messageId, ts: m.ts || null });
      }
    }
  }
  return byAuthor;
}

function withTimeout(promise, ms, label) {
  if (!Number.isFinite(ms) || ms <= 0) return promise;
  let to;
  const timeout = new Promise((_, reject) => {
    to = setTimeout(() => reject(new Error(`timeout(${label || "op"}): ${ms}ms`)), ms);
  });
  return Promise.race([promise, timeout]).finally(() => clearTimeout(to));
}

async function main() {
  const args = parseArgs(process.argv);
  const reportPath = args._[0];
  if (!reportPath) {
    console.error(
      "Usage: node discord_reply_1by1.mjs <path-to-report.json> [--limit N] [--delay-ms N] [--dry-run] [--state path]"
    );
    process.exit(2);
  }

  const limit = args.limit ? Number(args.limit) : Infinity;
  const delayMs = args["delay-ms"] ? Number(args["delay-ms"]) : 8000;
  const dryRun = !!args.dryRun;
  // Default headless to avoid popping windows / stealing focus. Pass --headed to show UI.
  const headless = !args.headed;
  const retryFailed = !!args.retryFailed;

  const rep = readJson(reportPath);
  const runDir = rep.outputDir || path.dirname(reportPath);

  const statePath = args.state
    ? path.resolve(process.cwd(), String(args.state))
    : path.join(runDir, "reply_state.json");
  const state = fs.existsSync(statePath) ? readJson(statePath) : { replied: [], failed: [] };
  const replied = new Set(Array.isArray(state.replied) ? state.replied : []);
  // Drop stale failures for targets that have since been replied successfully.
  const failed = (Array.isArray(state.failed) ? state.failed : []).filter(
    (f) => !replied.has(f?.targetMessageUrl)
  );
  // Persist cleanup so the state file doesn't grow unbounded.
  writeJson(statePath, { replied: Array.from(replied), failed });

  const failCounts = new Map();
  for (const f of failed) {
    const u = f?.targetMessageUrl;
    if (!u) continue;
    failCounts.set(u, (failCounts.get(u) || 0) + 1);
  }

  // Prefer report-provided targets; otherwise derive from messages files in the run directory.
  const derived = resolveTargetsFromRunDir(runDir);

  const authors = (rep.authors || [])
    .filter((a) => a && a.replyShort)
    .filter((a) => (a.author || "").toLowerCase() !== "unknown")
    // Skip our own/bot accounts (best-effort).
    .filter((a) => {
      const n = (a.author || "").trim().toLowerCase();
      if (!n) return false;
      if (n === "oysterguard") return false;
      if (n === "oyster republic") return false;
      if (n.includes("oyster republic")) return false;
      return true;
    })
    .map((a) => {
      if (a.targetMessageUrl && a.targetChannelId && a.targetMessageId) return a;
      const hit = derived.get(a.author);
      if (!hit) return a;
      const guildId = rep.guildId;
      const targetChannelId = hit.channelId;
      const targetMessageId = hit.messageId;
      const targetMessageUrl =
        guildId && targetChannelId && targetMessageId
          ? `https://discord.com/channels/${guildId}/${targetChannelId}/${targetMessageId}`
          : null;
      return { ...a, targetChannelId, targetMessageId, targetMessageUrl };
    })
    .filter((a) => a.targetMessageUrl && a.targetChannelId && a.targetMessageId)
    .slice(0, Number.isFinite(limit) ? limit : (rep.authors || []).length);

  const userDataDir = path.resolve(process.cwd(), "user-data");
  const MAX_CONTEXT_RESTARTS = 3;
  let contextRestarts = 0;

  async function launchCtx() {
    const ctx = await chromium.launchPersistentContext(userDataDir, {
      headless,
      viewport: { width: 1400, height: 900 },
      args: ["--disable-dev-shm-usage"],
    });
    const pg = ctx.pages()[0] ?? (await ctx.newPage());
    pg.setDefaultTimeout(60_000);
    return { ctx, pg };
  }

  let { ctx: context, pg: page } = await launchCtx();

  // Health check: can the page still navigate?
  async function isContextAlive() {
    try {
      if (page.isClosed()) return false;
      await page.evaluate(() => document.title);
      return true;
    } catch {
      return false;
    }
  }

  // Restart context if it crashed (BUG-012 watchdog)
  async function ensureContext() {
    if (await isContextAlive()) return true;
    if (contextRestarts >= MAX_CONTEXT_RESTARTS) {
      console.error(`Context crashed ${MAX_CONTEXT_RESTARTS} times, giving up.`);
      return false;
    }
    contextRestarts++;
    console.log(`⚠️ Context dead — restarting (${contextRestarts}/${MAX_CONTEXT_RESTARTS})...`);
    try { await context.close().catch(() => {}); } catch {}
    ({ ctx: context, pg: page } = await launchCtx());
    return true;
  }

  for (const a of authors) {
    const url = a.targetMessageUrl;
    if (replied.has(url)) continue;
    if (!retryFailed && (failCounts.get(url) || 0) >= 2) continue;

    // Retry each target once if we hit a context crash mid-flight.
    for (let attempt = 1; attempt <= 2; attempt++) {
      // Watchdog: ensure context is alive before each reply
      if (!(await ensureContext())) return;

      try {
        await withTimeout(gotoMessage(page, url), 90_000, "gotoMessage");

        const liId = `chat-messages-${a.targetChannelId}-${a.targetMessageId}`;
        await withTimeout(openReplyBox(page, liId), 60_000, "openReplyBox");

        if (!dryRun) {
          await withTimeout(typeAndSend(page, a.replyShort), 30_000, "typeAndSend");
          {
            const ts = new Date().toISOString().replace(/[:.]/g, "-");
            const outDir = path.resolve(process.cwd(), "output");
            fs.mkdirSync(outDir, { recursive: true });
            const shot = path.join(outDir, `reply-sent-${a.targetChannelId}-${a.targetMessageId}-${ts}.png`);
            await page.screenshot({ path: shot, fullPage: false }).catch(() => {});
          }
          replied.add(url);
          // If we succeeded, drop prior failure records for the same target.
          for (let i = failed.length - 1; i >= 0; i--) {
            const f = failed[i];
            if (f?.targetMessageUrl === url) failed.splice(i, 1);
            else if (f?.targetChannelId === a.targetChannelId && f?.targetMessageId === a.targetMessageId)
              failed.splice(i, 1);
          }
          writeJson(statePath, { replied: Array.from(replied), failed });
          await page.waitForTimeout(Number.isFinite(delayMs) ? delayMs : 8000);
        } else {
          await page.waitForTimeout(250);
        }

        // success
        break;
      } catch (e) {
        const errMsg = e?.message || String(e);
        const isContextDead = errMsg.includes("has been closed") || errMsg.includes("Target page") || errMsg.includes("crashed");

        if (isContextDead && attempt === 1) {
          // Immediate restart + retry the same target once.
          console.log(`⚠️ Context crashed during reply to ${a.author}, restarting + retrying...`);
          try { await context.close().catch(() => {}); } catch {}
          ({ ctx: context, pg: page } = await launchCtx());
          continue;
        }

        const ts = new Date().toISOString().replace(/[:.]/g, "-");
        const outDir = path.resolve(process.cwd(), "output");
        fs.mkdirSync(outDir, { recursive: true });
        let failShot = null;
        if (!isContextDead) {
          failShot = path.join(outDir, `reply-fail-${a.targetChannelId}-${a.targetMessageId}-${ts}.png`);
          await page.screenshot({ path: failShot, fullPage: false }).catch(() => {});
        }
        failed.push({
          author: a.author,
          targetMessageUrl: url,
          targetChannelId: a.targetChannelId,
          targetMessageId: a.targetMessageId,
          error: errMsg,
          screenshot: failShot,
          at: new Date().toISOString(),
        });
        writeJson(statePath, { replied: Array.from(replied), failed });

        if (!isContextDead) {
          // Normal error — reset UI and keep going
          await page.keyboard.press("Escape").catch(() => {});
          await page.keyboard.press("Escape").catch(() => {});
          await page.waitForTimeout(800).catch(() => {});
        }
        break;
      }
    }
  }

  await context.close().catch(() => {});
}

main().catch((err) => {
  console.error(err?.stack || String(err));
  process.exit(1);
});
