#!/usr/bin/env node
/**
 * discord_auto_cs.mjs - Autonomous Discord CS Loop
 *
 * Full pipeline: audit → generate replies → execute 1-by-1 → verify → fix → repeat
 *
 * Usage:
 *   node discord_auto_cs.mjs <channel-url> [--limit 30] [--dry-run] [--headed] [--max-retries 3]
 *
 * Example:
 *   node discord_auto_cs.mjs https://discord.com/channels/1404726112159793172/1404870331759591575
 *   node discord_auto_cs.mjs https://discord.com/channels/1404726112159793172/1404870331759591575 --limit 20 --headed
 */

import { execSync, spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const SCRIPT_DIR = path.dirname(new URL(import.meta.url).pathname);

function ts() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}-${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}`;
}

function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith("--")) { out._.push(a); continue; }
    const k = a.slice(2);
    if (k === "dry-run") out.dryRun = true;
    else if (k === "headed") out.headed = true;
    else { out[k] = argv[i + 1]; i++; }
  }
  return out;
}

function runScript(name, args = []) {
  const script = path.join(SCRIPT_DIR, name);
  console.log(`\n=== Running: ${name} ${args.join(" ")} ===`);
  try {
    const result = execSync(`node "${script}" ${args.map(a => `"${a}"`).join(" ")}`, {
      cwd: SCRIPT_DIR,
      stdio: "pipe",
      timeout: 300_000, // 5 min per step
      encoding: "utf8",
    });
    console.log(result.slice(-500)); // last 500 chars
    return { success: true, output: result };
  } catch (err) {
    console.error(`FAILED: ${name}`, err.stderr?.slice(-300) || err.message);
    return { success: false, error: err.message, stderr: err.stderr };
  }
}

function findLatestReport() {
  const auditDir = path.join(SCRIPT_DIR, "audit");
  if (!fs.existsSync(auditDir)) return null;
  const dirs = fs.readdirSync(auditDir)
    .filter(d => d.includes("disappointment"))
    .sort()
    .reverse();
  for (const d of dirs) {
    const rp = path.join(auditDir, d, "report.json");
    if (fs.existsSync(rp)) return rp;
  }
  return null;
}

function analyzeReport(reportPath) {
  const rep = JSON.parse(fs.readFileSync(reportPath, "utf8"));
  const authors = rep.authors || [];
  const total = authors.length;
  const withReply = authors.filter(a => a.replyShort).length;
  const withTarget = authors.filter(a => a.targetMessageUrl).length;

  // Check for template-like replies (too similar)
  const replies = authors.map(a => a.replyShort || "").filter(Boolean);
  const templateCount = detectTemplates(replies);

  return { total, withReply, withTarget, templateCount, reportPath, rep };
}

function detectTemplates(replies) {
  if (replies.length < 3) return 0;
  let templateCount = 0;
  for (let i = 0; i < replies.length; i++) {
    for (let j = i + 1; j < replies.length; j++) {
      if (similarity(replies[i], replies[j]) > 0.7) templateCount++;
    }
  }
  return templateCount;
}

function similarity(a, b) {
  const sa = new Set(a.toLowerCase().split(/\s+/));
  const sb = new Set(b.toLowerCase().split(/\s+/));
  const intersection = new Set([...sa].filter(x => sb.has(x)));
  const union = new Set([...sa, ...sb]);
  return union.size === 0 ? 0 : intersection.size / union.size;
}

function writeIssueLog(issues, runTs) {
  const logPath = path.join(SCRIPT_DIR, "output", `issue_log_${runTs}.md`);
  const content = `# Issue Log - ${runTs}\n\n` +
    issues.map((iss, i) =>
      `## Issue ${i + 1}\n- Task: ${iss.task}\n- Expected: ${iss.expected}\n- Actual: ${iss.actual}\n- Root Cause: ${iss.rootCause || "unknown"}\n- Fix: ${iss.fix || "pending"}\n- Status: ${iss.status || "open"}\n`
    ).join("\n");
  fs.mkdirSync(path.dirname(logPath), { recursive: true });
  fs.writeFileSync(logPath, content);
  console.log(`Issue log: ${logPath}`);
  return logPath;
}

async function main() {
  const args = parseArgs(process.argv);
  const channelUrl = args._[0];
  if (!channelUrl) {
    console.error("Usage: node discord_auto_cs.mjs <channel-url> [--limit N] [--dry-run] [--headed] [--max-retries N]");
    process.exit(2);
  }

  const limit = args.limit ? Number(args.limit) : 30;
  const maxRetries = args["max-retries"] ? Number(args["max-retries"]) : 3;
  const dryRun = !!args.dryRun;
  const headed = args.headed ? "--headed" : "";
  const runTimestamp = ts();
  const issues = [];

  console.log(`\n${"=".repeat(60)}`);
  console.log(`Discord Auto CS - ${runTimestamp}`);
  console.log(`Channel: ${channelUrl}`);
  console.log(`Limit: ${limit}, Max retries: ${maxRetries}, Dry run: ${dryRun}`);
  console.log(`${"=".repeat(60)}`);

  // ── Step 1: Audit ──
  console.log("\n[Step 1/4] Auditing channel for user issues...");
  const auditArgs = [channelUrl, "--limit", String(limit)];
  if (headed) auditArgs.push(headed);
  const auditResult = runScript("discord_disappointment_audit.mjs", auditArgs);

  if (!auditResult.success) {
    issues.push({
      task: "audit",
      expected: "Successfully scan channel messages",
      actual: `Audit failed: ${auditResult.error?.slice(0, 200)}`,
      status: "blocking",
    });
    writeIssueLog(issues, runTimestamp);
    console.error("Audit failed. Check issue log.");
    process.exit(1);
  }

  // ── Step 2: Analyze report ──
  console.log("\n[Step 2/4] Analyzing audit report...");
  const reportPath = findLatestReport();
  if (!reportPath) {
    issues.push({
      task: "find report",
      expected: "report.json exists in audit/",
      actual: "No report found",
      status: "blocking",
    });
    writeIssueLog(issues, runTimestamp);
    process.exit(1);
  }

  const analysis = analyzeReport(reportPath);
  console.log(`  Total users: ${analysis.total}`);
  console.log(`  With replies: ${analysis.withReply}`);
  console.log(`  With targets: ${analysis.withTarget}`);
  console.log(`  Template-like pairs: ${analysis.templateCount}`);

  if (analysis.templateCount > analysis.withReply * 0.3) {
    issues.push({
      task: "reply quality",
      expected: "Unique, customized replies",
      actual: `${analysis.templateCount} template-like reply pairs (>30% threshold)`,
      rootCause: "Audit script generating generic replies",
      fix: "Replies need manual review or re-generation with discord_cs prompt",
      status: "warning",
    });
    console.warn(`  WARNING: ${analysis.templateCount} template-like replies detected!`);
  }

  // ── Step 3: Execute replies ──
  console.log("\n[Step 3/4] Executing 1-by-1 replies...");
  const replyArgs = [reportPath, "--delay-ms", "10000"];
  if (dryRun) replyArgs.push("--dry-run");
  if (headed) replyArgs.push(headed);

  let retries = 0;
  let replySuccess = false;

  while (retries < maxRetries && !replySuccess) {
    if (retries > 0) console.log(`  Retry ${retries}/${maxRetries}...`);
    const replyResult = runScript("discord_reply_1by1.mjs", replyArgs);

    if (replyResult.success) {
      replySuccess = true;
    } else {
      retries++;
      issues.push({
        task: `reply execution (attempt ${retries})`,
        expected: "All replies sent successfully",
        actual: `Failed: ${replyResult.error?.slice(0, 200)}`,
        rootCause: replyResult.stderr?.includes("Extension disconnected")
          ? "Playwright extension disconnected"
          : replyResult.stderr?.includes("timeout")
          ? "Element timeout (DOM changed or slow load)"
          : "Unknown",
        fix: retries < maxRetries ? "Retrying with fresh browser context" : "Manual intervention needed",
        status: retries >= maxRetries ? "escalate" : "retrying",
      });

      if (retries < maxRetries) {
        console.log("  Waiting 10s before retry...");
        await new Promise(r => setTimeout(r, 10_000));
      }
    }
  }

  // ── Step 4: Verify & Report ──
  console.log("\n[Step 4/4] Generating report...");

  if (issues.length > 0) {
    const logPath = writeIssueLog(issues, runTimestamp);
    const escalations = issues.filter(i => i.status === "escalate" || i.status === "blocking");

    if (escalations.length > 0) {
      console.log(`\n!! ${escalations.length} issue(s) need Howard's attention. See: ${logPath}`);
    }
  }

  const summary = {
    timestamp: runTimestamp,
    channelUrl,
    usersAudited: analysis.total,
    repliesSent: replySuccess ? analysis.withTarget : 0,
    templateWarnings: analysis.templateCount,
    retries,
    issues: issues.length,
    dryRun,
    reportPath,
  };

  const summaryPath = path.join(SCRIPT_DIR, "output", `cs_run_${runTimestamp}.json`);
  fs.mkdirSync(path.dirname(summaryPath), { recursive: true });
  fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2));

  console.log(`\n${"=".repeat(60)}`);
  console.log("Run Summary:");
  console.log(`  Users: ${summary.usersAudited}, Replies: ${summary.repliesSent}`);
  console.log(`  Issues: ${summary.issues}, Retries: ${summary.retries}`);
  console.log(`  Report: ${summaryPath}`);
  console.log(`${"=".repeat(60)}`);
}

main().catch((err) => {
  console.error(err?.stack || String(err));
  process.exit(1);
});
