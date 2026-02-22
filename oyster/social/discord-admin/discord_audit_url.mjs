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

function walkA11y(node, out, trail = []) {
  if (!node) return;

  const role = node.role || "";
  const name = (node.name || "").trim();

  // Capture likely nodes in the left channel list: categories/headings and items.
  if ((role === "treeitem" || role === "heading") && name) {
    out.push({ role, name, trail });
  }

  const nextTrail =
    role === "heading" && name ? [...trail, name] : trail;

  const children = node.children || [];
  for (const c of children) walkA11y(c, out, nextTrail);
}

async function main() {
  const targetUrl = process.argv[2];
  if (!targetUrl) {
    console.error("Usage: node discord_audit_url.mjs <discord channel url>");
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
    viewport: { width: 1280, height: 800 },
    args: ["--disable-dev-shm-usage"],
  });

  const page = context.pages()[0] ?? (await context.newPage());
  page.setDefaultTimeout(60_000);

  await page.goto(targetUrl, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(1500);

  // If login is required, Discord will show a login page; wait until we land in /channels/<guild>/<channel>.
  const deadlineMs = Date.now() + 10 * 60_000;
  let ids = extractGuildAndChannel(page.url());
  while (!ids && Date.now() < deadlineMs) {
    await page.waitForTimeout(1000);
    ids = extractGuildAndChannel(page.url());
  }

  // Best-effort re-goto after login.
  if (!ids) {
    await page.goto(targetUrl, { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(1500);
    ids = extractGuildAndChannel(page.url());
  }

  await page.screenshot({ path: path.join(runDir, "current.png"), fullPage: true });
  writeJson(path.join(runDir, "meta.json"), {
    startedFrom: targetUrl,
    finalUrl: page.url(),
    title: await page.title().catch(() => null),
  });

  if (!ids) {
    writeJson(path.join(runDir, "result.json"), {
      ok: false,
      reason:
        "Timed out waiting for a /channels/<guildId>/<channelId> URL. Login in the opened window, then re-run.",
      lastUrl: page.url(),
      outputDir: runDir,
    });
    await context.close();
    return;
  }

  const a11y = await page.accessibility.snapshot({ interestingOnly: false });
  writeJson(path.join(runDir, "a11y.json"), a11y);

  const flat = [];
  walkA11y(a11y, flat);
  writeJson(path.join(runDir, "a11y_flat.json"), flat);

  // Deduplicate names to keep the summary small.
  const uniq = Array.from(new Set(flat.map((x) => `${x.role}:${x.name}`))).slice(0, 500);
  writeJson(path.join(runDir, "summary.json"), { items: uniq });

  writeJson(path.join(runDir, "result.json"), {
    ok: true,
    url: page.url(),
    ...ids,
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
