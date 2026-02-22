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
    // https://discord.com/channels/<guildId>/<channelId>
    const m = u.pathname.match(/^\/channels\/(\d+)\/(\d+)/);
    if (!m) return null;
    return { guildId: m[1], channelId: m[2] };
  } catch {
    return null;
  }
}

function walkA11y(node, out, parentNames = []) {
  if (!node) return;
  const name = node.name || "";
  const role = node.role || "";

  // Channels and categories are typically exposed as treeitems / headings.
  if (role === "treeitem" || role === "heading") {
    const text = name.trim();
    if (text) out.push({ role, name: text, parents: parentNames });
  }

  const children = node.children || [];
  for (const c of children) walkA11y(c, out, parentNames);
}

async function main() {
  // Default headless to avoid popping windows / stealing focus. Pass --headed to show UI.
  const headless = !process.argv.includes("--headed");
  const baseDir = path.resolve(process.cwd(), "audit");
  const runDir = path.join(baseDir, ts());
  mkdirp(runDir);

  const userDataDir = path.resolve(process.cwd(), "user-data");
  mkdirp(userDataDir);

  const context = await chromium.launchPersistentContext(userDataDir, {
    headless,
    viewport: { width: 1280, height: 800 },
    args: ["--disable-dev-shm-usage"],
  });

  const page = context.pages()[0] ?? (await context.newPage());
  page.setDefaultTimeout(60_000);

  await page.goto("https://discord.com/app", { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(1500);

  // Wait until the user is inside a guild channel (URL includes guild id).
  // If not logged in, the user can log in in the opened browser window.
  const deadlineMs = Date.now() + 10 * 60_000;
  let ids = extractGuildAndChannel(page.url());
  while (!ids && Date.now() < deadlineMs) {
    await page.waitForTimeout(1000);
    ids = extractGuildAndChannel(page.url());
  }

  await page.screenshot({ path: path.join(runDir, "current.png"), fullPage: true });

  if (!ids) {
    writeJson(path.join(runDir, "result.json"), {
      ok: false,
      reason:
        "Timed out waiting for a /channels/<guildId>/<channelId> URL. Open the target server and click any channel, then re-run.",
      lastUrl: page.url(),
    });
    await context.close();
    return;
  }

  // Snapshot the whole page accessibility tree; then filter for likely channel/category nodes.
  const a11y = await page.accessibility.snapshot({ interestingOnly: false });
  writeJson(path.join(runDir, "a11y.json"), a11y);

  const flat = [];
  walkA11y(a11y, flat);
  writeJson(path.join(runDir, "a11y_flat.json"), flat);

  writeJson(path.join(runDir, "result.json"), {
    ok: true,
    url: page.url(),
    ...ids,
    outputDir: runDir,
    note: "a11y.json contains the raw accessibility snapshot; a11y_flat.json is a flat list of treeitems/headings.",
  });

  // Keep the browser open for follow-up scripts.
  // eslint-disable-next-line no-constant-condition
  while (true) {
    await page.waitForTimeout(10_000);
  }
}

main().catch((err) => {
  // Best-effort crash dump
  try {
    fs.writeFileSync(
      path.resolve(process.cwd(), "audit_crash.txt"),
      String(err?.stack || err)
    );
  } catch {}
  process.exit(1);
});
