/* eslint-disable no-console */
// Session Control Panel v2 (spec: CodexClaudeSync/SPEC-session-control-panel-v2.md)
// Zero external deps: only node:* built-ins.

const fs = require("node:fs");
const fsp = fs.promises;
const http = require("node:http");
const os = require("node:os");
const path = require("node:path");
const readline = require("node:readline");
const { URL } = require("node:url");

const PORT = Number.parseInt(process.env.PORT || "3456", 10);
const HOST = process.env.HOST || "127.0.0.1";

const HOME = os.homedir();
const SYNC_DIR = path.join(HOME, "Library", "Application Support", "CodexClaudeSync");
const PATHS = {
  codexSessions: path.join(HOME, ".codex", "sessions"),
  codexArchived: path.join(HOME, ".codex", "archived_sessions"),
  claudeLocal: path.join(
    HOME,
    "Library",
    "Application Support",
    "Claude",
    "local-agent-mode-sessions",
  ),
  claudeCode: path.join(
    HOME,
    "Library",
    "Application Support",
    "Claude",
    "claude-code-sessions",
  ),
  issueInbox: path.join(
    HOME,
    "Library",
    "Application Support",
    "CodexClaudeSync",
    "issue_inbox.txt",
  ),
  progressLog: path.join(
    HOME,
    "Library",
    "Application Support",
    "CodexClaudeSync",
    "progress.log",
  ),
  sessionMeta: path.join(
    HOME,
    "Library",
    "Application Support",
    "CodexClaudeSync",
    "session_meta.json",
  ),
};

const CATEGORY_RULES = [
  {
    category: "hackathon",
    label: "🏆 Hackathon",
    keywords: ["hackathon", "x402", "solana ai"],
  },
  {
    category: "oysterworld",
    label: "🌍 Oysterworld",
    keywords: [
      "oysterworld",
      "claw-nation",
      "visionclaw",
      "relay",
      "funes",
      "map",
      "hex",
      "h3",
    ],
  },
  {
    category: "website",
    label: "🌐 Website",
    keywords: [
      "landing",
      "网站",
      "website",
      "clawphones-landing",
      "clawglasses-landing",
      "worldglasses-web",
      "oysterrepublic",
      "getpuffy",
      "nextjs",
      "前端整改",
    ],
  },
  {
    category: "twitter",
    label: "🐦 Twitter",
    keywords: [
      "twitter",
      "x.com",
      "推特",
      "reply",
      "engagement",
      "follower",
      "clawglasses",
      "oysterecosystem",
      "ubsphone",
      "puffy_ai",
      "clawrobo",
      "内容运营",
      "帐号管理",
      "账号管理",
    ],
  },
  {
    category: "discord",
    label: "💬 Discord",
    keywords: ["discord", "reply_1by1", "audit", "openreplybox", "客服", "社区"],
  },
  {
    category: "article",
    label: "📝 Article",
    keywords: ["article", "supergrok", "写article", "draft", "写Article"],
  },
  {
    category: "engineering",
    label: "🔧 Engineering",
    keywords: [
      "bug",
      "fix",
      "playwright",
      "venv",
      "worker",
      "crash",
      "断线",
      "断连",
      "修复",
    ],
  },
  {
    category: "infra",
    label: "🔐 Infra",
    keywords: [
      "tailscale",
      "ec2",
      "安全",
      "security",
      "部署",
      "deploy",
      "ssh",
      "pm2",
      "openclaw",
      "proxy",
      "llm",
    ],
  },
  {
    category: "other",
    label: "💬 Other",
    keywords: [],
  },
];

function detectCategory(text) {
  const t = String(text || "").toLowerCase();
  for (const rule of CATEGORY_RULES) {
    for (const kw of rule.keywords) {
      if (t.includes(String(kw).toLowerCase())) return rule;
    }
  }
  return CATEGORY_RULES[CATEGORY_RULES.length - 1];
}

function safeJsonParse(s) {
  try {
    return JSON.parse(s);
  } catch {
    return null;
  }
}

async function listFilesRecursive(rootDir, { matchFile } = {}) {
  const out = [];
  async function walk(dir) {
    let ents;
    try {
      ents = await fsp.readdir(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const ent of ents) {
      const full = path.join(dir, ent.name);
      if (ent.isDirectory()) {
        await walk(full);
        continue;
      }
      if (!ent.isFile()) continue;
      if (typeof matchFile === "function" && !matchFile(full)) continue;
      out.push(full);
    }
  }
  await walk(rootDir);
  return out;
}

async function readFirstLine(filePath, maxBytes = 64 * 1024) {
  const fh = await fsp.open(filePath, "r");
  try {
    const buf = Buffer.alloc(maxBytes);
    const { bytesRead } = await fh.read(buf, 0, maxBytes, 0);
    const chunk = buf.subarray(0, bytesRead).toString("utf8");
    const idx = chunk.indexOf("\n");
    const line = (idx === -1 ? chunk : chunk.slice(0, idx)).trimEnd();
    return line;
  } finally {
    await fh.close();
  }
}

function extractTextFromContent(content) {
  if (typeof content === "string") return content;
  if (Array.isArray(content)) {
    const parts = [];
    for (const blk of content) {
      if (!blk || typeof blk !== "object") continue;
      if (typeof blk.text === "string") parts.push(blk.text);
      else if (typeof blk.content === "string") parts.push(blk.content);
    }
    return parts.join("");
  }
  if (content && typeof content === "object" && typeof content.text === "string") {
    return content.text;
  }
  return "";
}

function normalizeSnippet(s, maxLen = 1000) {
  const t = String(s || "").replace(/\r\n/g, "\n").replace(/\r/g, "\n").trim();
  if (!t) return "";
  if (t.length <= maxLen) return t;
  return t.slice(0, maxLen).trimEnd() + "…";
}

function isBoilerplateUserMessage(txt) {
  const t = txt.trim();
  if (!t) return true;
  if (t.includes("AGENTS.md instructions")) return true;
  if (t.includes("<INSTRUCTIONS>")) return true;
  if (t.includes("<environment_context>")) return true;
  if (t.startsWith("<environment_context>")) return true;
  if (t.startsWith("# AGENTS.md instructions")) return true;
  if (t.startsWith("# Codex desktop context")) return true;
  return false;
}

async function extractCodexFirstTask(jsonlPath) {
  const stream = fs.createReadStream(jsonlPath, { encoding: "utf8" });
  const rl = readline.createInterface({ input: stream, crlfDelay: Infinity });
  let lineNo = 0;
  try {
    for await (const line of rl) {
      lineNo += 1;
      if (lineNo === 1) continue; // session_meta
      if (lineNo > 800) break; // avoid scanning huge files

      const obj = safeJsonParse(line);
      if (!obj || obj.type !== "response_item") continue;

      const payload = obj.payload || {};
      if (payload.role !== "user" || payload.type !== "message") continue;

      const txt = normalizeSnippet(extractTextFromContent(payload.content), 1200);
      if (!txt) continue;
      if (isBoilerplateUserMessage(txt)) continue;

      return txt;
    }
  } catch {
    // Ignore parse/stream errors; we'll fall back to empty.
  } finally {
    rl.close();
    stream.destroy();
  }
  return "";
}

async function parseCodexSession(jsonlPath, status) {
  const st = await fsp.stat(jsonlPath);
  const firstLine = await readFirstLine(jsonlPath);
  const meta = safeJsonParse(firstLine) || {};
  const payload = meta.payload || {};

  const id =
    payload.id ||
    path.basename(jsonlPath).replace(/\.jsonl$/i, "").split("-").slice(-5).join("-");
  const timestamp = payload.timestamp || meta.timestamp || new Date(st.mtimeMs).toISOString();
  const cwd = payload.cwd || null;

  const firstTask = await extractCodexFirstTask(jsonlPath);
  const title =
    normalizeSnippet(firstTask.split("\n")[0] || "", 120) ||
    `Codex session ${String(id).slice(0, 8)}`;

  const cat = detectCategory(`${title}\n${firstTask}`);
  return {
    id,
    source: "codex",
    timestamp,
    title,
    cwd,
    category: cat.category,
    category_label: cat.label,
    first_task: firstTask,
    model: null,
    status,
    size_bytes: st.size,
  };
}

function msToIso(ms, fallbackMs) {
  const n = Number(ms);
  if (Number.isFinite(n) && n > 0) return new Date(n).toISOString();
  const f = Number(fallbackMs);
  if (Number.isFinite(f) && f > 0) return new Date(f).toISOString();
  return new Date().toISOString();
}

async function parseClaudeSession(jsonPath, source) {
  const st = await fsp.stat(jsonPath);
  let raw;
  try {
    raw = await fsp.readFile(jsonPath, "utf8");
  } catch {
    return null;
  }
  const data = safeJsonParse(raw);
  if (!data || typeof data !== "object") return null;

  const id = data.sessionId || data.cliSessionId || path.basename(jsonPath).replace(/\.json$/i, "");
  const timestamp = msToIso(data.lastActivityAt, data.createdAt);
  const title = normalizeSnippet(data.title || data.name || "", 160) || `Claude session ${String(id).slice(0, 8)}`;
  const cwd = data.cwd || data.originCwd || null;
  const model = data.model || null;
  const status = data.isArchived ? "archived" : "active";
  const firstTask = normalizeSnippet(data.initialMessage || "", 1200) || "";

  const cat = detectCategory(`${title}\n${firstTask}`);
  return {
    id,
    source,
    timestamp,
    title,
    cwd,
    category: cat.category,
    category_label: cat.label,
    first_task: firstTask,
    model,
    status,
    size_bytes: st.size,
  };
}

async function getSessionsUncached() {
  const codexActive = await listFilesRecursive(PATHS.codexSessions, {
    matchFile: (p) => p.endsWith(".jsonl"),
  });
  const codexArchived = await listFilesRecursive(PATHS.codexArchived, {
    matchFile: (p) => p.endsWith(".jsonl"),
  });

  const claudeLocal = await listFilesRecursive(PATHS.claudeLocal, {
    matchFile: (p) => {
      const base = path.basename(p);
      if (!/^local_[0-9a-f-]+\.json$/i.test(base)) return false;
      // Exclude aux files under .claude
      return !p.includes(`${path.sep}.claude${path.sep}`);
    },
  });

  const claudeCode = await listFilesRecursive(PATHS.claudeCode, {
    matchFile: (p) => {
      const base = path.basename(p);
      if (!/^local_[0-9a-f-]+\.json$/i.test(base)) return false;
      return !p.includes(`${path.sep}.claude${path.sep}`);
    },
  });

  const mapWithConcurrency = async (items, limit, mapper) => {
    const results = new Array(items.length);
    let idx = 0;
    const workers = Array.from({ length: Math.min(limit, items.length || 1) }, async () => {
      while (idx < items.length) {
        const i = idx++;
        try {
          results[i] = await mapper(items[i]);
        } catch {
          results[i] = null;
        }
      }
    });
    await Promise.all(workers);
    return results.filter(Boolean);
  };

  const codexItems = [
    ...codexActive.map((p) => ({ p, status: "active" })),
    ...codexArchived.map((p) => ({ p, status: "archived" })),
  ];

  const codexParsed = await mapWithConcurrency(codexItems, 10, (it) =>
    parseCodexSession(it.p, it.status),
  );
  const claudeLocalParsed = await mapWithConcurrency(claudeLocal, 10, (p) =>
    parseClaudeSession(p, "claude_local"),
  );
  const claudeCodeParsed = await mapWithConcurrency(claudeCode, 10, (p) =>
    parseClaudeSession(p, "claude_code"),
  );

  const sessions = [...codexParsed, ...claudeLocalParsed, ...claudeCodeParsed];
  sessions.sort((a, b) => {
    const ta = Date.parse(a.timestamp) || 0;
    const tb = Date.parse(b.timestamp) || 0;
    return tb - ta;
  });
  return sessions;
}

let SESSIONS_CACHE = { at: 0, data: null };
const SESSIONS_CACHE_TTL_MS = 10_000;

async function getSessionsCached() {
  const now = Date.now();
  if (SESSIONS_CACHE.data && now - SESSIONS_CACHE.at < SESSIONS_CACHE_TTL_MS) {
    return SESSIONS_CACHE.data;
  }
  const data = await getSessionsUncached();
  SESSIONS_CACHE = { at: now, data };
  return data;
}

async function getIssues() {
  let raw = "";
  try {
    raw = await fsp.readFile(PATHS.issueInbox, "utf8");
  } catch {
    return [];
  }
  const out = [];
  for (const line of raw.split(/\r?\n/)) {
    const m = line.match(/^\[(P\d+)\]\[((?:BUG|ENG|OPS)-\d+)\]\s*(.+)$/);
    if (!m) continue;
    const [, priority, id, rest] = m;
    const parts = rest.split("|").map((s) => s.trim());
    const title = parts[0] || "";
    const sessionType = parts[1] || "";
    const status = /已修复|已修復|fixed|✅/i.test(line) ? "fixed" : "open";
    out.push({
      id,
      priority,
      title,
      status,
      session_type: sessionType,
    });
  }
  return out;
}

async function getProgress() {
  let raw = "";
  try {
    raw = await fsp.readFile(PATHS.progressLog, "utf8");
  } catch {
    return [];
  }
  const lines = raw.split(/\r?\n/).filter(Boolean);
  const last = lines.slice(-50);
  const out = [];
  for (const line of last) {
    const m = line.match(/^\[(.+?)\]\s*\[(.+?)\]\s*\[(DONE|FAIL|BLOCKED)\]\s*(.+)$/);
    if (!m) continue;
    const [, timestamp, session, status, rest] = m;
    const parts = rest.split("|").map((s) => s.trim());
    out.push({
      timestamp,
      session,
      status,
      task: parts[0] || "",
      output: parts[1] || "",
    });
  }
  return out;
}

// ---------- Live Codex session tails ----------
// Returns the last N agent messages from each recently-modified Codex session JSONL.
async function getLiveCodexSessions(maxSessions = 20, maxMessages = 5) {
  const sessionDir = PATHS.codexSessions;
  const allJsonl = await listFilesRecursive(sessionDir, {
    matchFile: (p) => p.endsWith(".jsonl"),
  });

  // Sort by mtime desc, take most recent N
  const withStats = [];
  for (const p of allJsonl) {
    try {
      const st = await fsp.stat(p);
      withStats.push({ path: p, mtimeMs: st.mtimeMs, size: st.size });
    } catch { /* skip */ }
  }
  withStats.sort((a, b) => b.mtimeMs - a.mtimeMs);
  const recent = withStats.slice(0, maxSessions);

  const results = [];
  for (const entry of recent) {
    // Read last ~32KB to find recent messages
    const tailBytes = 32 * 1024;
    let tail = "";
    try {
      const fh = await fsp.open(entry.path, "r");
      const offset = Math.max(0, entry.size - tailBytes);
      const buf = Buffer.alloc(Math.min(tailBytes, entry.size));
      await fh.read(buf, 0, buf.length, offset);
      await fh.close();
      tail = buf.toString("utf8");
    } catch { continue; }

    const lines = tail.split("\n").filter(Boolean);
    const messages = [];
    const toolCalls = [];
    let lastTokenInfo = null;

    for (const line of lines) {
      const obj = safeJsonParse(line);
      if (!obj) continue;

      if (obj.type === "event_msg" && obj.payload) {
        if (obj.payload.type === "agent_message") {
          messages.push({
            ts: obj.timestamp,
            text: normalizeSnippet(obj.payload.message || "", 300),
          });
        }
        if (obj.payload.type === "token_count") {
          lastTokenInfo = obj.payload.info?.total_token_usage || null;
        }
      }
      if (obj.type === "response_item" && obj.payload) {
        if (obj.payload.type === "tool_call") {
          toolCalls.push({
            ts: obj.timestamp,
            name: obj.payload.name || obj.payload.tool_name || "unknown",
            status: obj.payload.status || "running",
          });
        }
      }
    }

    // Extract session ID from filename
    const basename = path.basename(entry.path, ".jsonl");
    const idMatch = basename.match(/([0-9a-f]{8}-[0-9a-f-]+)$/);
    const sessionId = idMatch ? idMatch[1] : basename;

    // Read first task for context
    const firstTask = await extractCodexFirstTask(entry.path);
    const cat = detectCategory(firstTask);

    const lastMessages = messages.slice(-maxMessages);
    const lastTools = toolCalls.slice(-3);
    const lastActivity = messages.length > 0 ? messages[messages.length - 1].ts : null;
    const isActive = (Date.now() - entry.mtimeMs) < 5 * 60 * 1000; // active if modified in last 5 min

    results.push({
      id: sessionId,
      path: entry.path,
      category: cat.category,
      category_label: cat.label,
      first_task: normalizeSnippet(firstTask.split("\n")[0] || "", 120),
      is_active: isActive,
      last_modified: new Date(entry.mtimeMs).toISOString(),
      last_activity: lastActivity,
      messages: lastMessages,
      recent_tools: lastTools,
      tokens: lastTokenInfo,
      size_bytes: entry.size,
    });
  }

  return results;
}

// ---------- Session Meta (v2) ----------

async function readSessionMeta() {
  try {
    const raw = await fsp.readFile(PATHS.sessionMeta, "utf8");
    return JSON.parse(raw);
  } catch {
    return { sessions: {}, milestones: [], updated_at: new Date().toISOString() };
  }
}

async function writeSessionMeta(meta) {
  meta.updated_at = new Date().toISOString();
  await fsp.writeFile(PATHS.sessionMeta, JSON.stringify(meta, null, 2), "utf8");
}

function computeEisenhower(urgency, importance) {
  const u = String(urgency || "").toLowerCase();
  const i = String(importance || "").toLowerCase();
  if (u === "high" && i === "high") return "DO";
  if (u !== "high" && i === "high") return "PLAN";
  if (u === "high" && i !== "high") return "DELEGATE";
  return "DROP";
}

function detectStale(sessionMeta, progressEntries) {
  const now = Date.now();
  const STALE_MS = 48 * 60 * 60 * 1000;
  for (const [id, meta] of Object.entries(sessionMeta.sessions || {})) {
    if (id === "_README") continue;
    if (meta.conclusion === "completed" || meta.conclusion === "archived") continue;
    const reviewed = meta.last_reviewed ? Date.parse(meta.last_reviewed) : 0;
    if (now - reviewed > STALE_MS) {
      const hasRecentProgress = progressEntries.some(
        (e) => e.session && e.session.toLowerCase().includes(id.toLowerCase()) && e.status === "DONE"
      );
      if (!hasRecentProgress && meta.conclusion !== "blocked") {
        meta.conclusion = "stalled";
      }
    }
  }
  return sessionMeta;
}

async function getEisenhowerGroups() {
  const meta = await readSessionMeta();
  const groups = { DO: [], PLAN: [], DELEGATE: [], DROP: [] };
  for (const [id, s] of Object.entries(meta.sessions || {})) {
    if (id === "_README") continue;
    const quad = s.eisenhower || computeEisenhower(s.urgency, s.importance);
    const entry = { id, ...s, eisenhower: quad };
    if (groups[quad]) groups[quad].push(entry);
    else groups.DO.push(entry);
  }
  return { groups, milestones: meta.milestones || [] };
}

async function getGanttData() {
  const meta = await readSessionMeta();
  const items = [];
  for (const [id, s] of Object.entries(meta.sessions || {})) {
    if (id === "_README") continue;
    items.push({
      id,
      label: s.label || id,
      conclusion: s.conclusion || "active",
      priority: s.priority || "P2",
      start_date: s.start_date || null,
      target_date: s.target_date || null,
      actual_end: s.actual_end || null,
      depends_on: s.depends_on || [],
      tags: s.tags || [],
    });
  }
  items.sort((a, b) => {
    const po = { P0: 0, P1: 1, P2: 2, P3: 3 };
    return (po[a.priority] || 9) - (po[b.priority] || 9);
  });
  return { items, milestones: meta.milestones || [] };
}

async function getStaleItems() {
  const meta = await readSessionMeta();
  const prog = await getProgress();
  detectStale(meta, prog);
  const stale = [];
  for (const [id, s] of Object.entries(meta.sessions || {})) {
    if (id === "_README") continue;
    if (s.conclusion === "stalled") stale.push({ id, ...s });
  }
  return stale;
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on("data", (c) => chunks.push(c));
    req.on("end", () => {
      try {
        resolve(JSON.parse(Buffer.concat(chunks).toString("utf8")));
      } catch (e) {
        reject(new Error("Invalid JSON body"));
      }
    });
    req.on("error", reject);
  });
}

// Parse CONCLUDE lines from progress.log and auto-update meta
async function syncConcludesFromProgress() {
  const meta = await readSessionMeta();
  let raw = "";
  try {
    raw = await fsp.readFile(PATHS.progressLog, "utf8");
  } catch {
    return;
  }
  let changed = false;
  for (const line of raw.split(/\r?\n/)) {
    const m = line.match(/\[CONCLUDE:(\w+)\]\s*(.*)$/);
    if (!m) continue;
    const conclusion = m[1];
    const note = m[2].trim();
    const sm = line.match(/\[(.+?)\]\s*\[(.+?)\]/);
    if (!sm) continue;
    const sessionKey = sm[2].trim();
    for (const [id, s] of Object.entries(meta.sessions || {})) {
      if (id === "_README") continue;
      if (id === sessionKey || (s.label && s.label.toLowerCase().includes(sessionKey.toLowerCase()))) {
        if (s.conclusion !== conclusion) {
          s.conclusion = conclusion;
          s.conclusion_note = note || s.conclusion_note;
          s.last_reviewed = new Date().toISOString();
          if (conclusion === "completed") s.actual_end = new Date().toISOString().slice(0, 10);
          changed = true;
        }
      }
    }
  }
  if (changed) await writeSessionMeta(meta);
}

function sendJson(res, code, obj) {
  const body = JSON.stringify(obj);
  res.writeHead(code, {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, PUT, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  });
  res.end(body);
}

function sendText(res, code, body, contentType = "text/plain; charset=utf-8") {
  res.writeHead(code, {
    "Content-Type": contentType,
    "Cache-Control": "no-store",
  });
  res.end(body);
}

async function sendIndexHtml(res) {
  const p = path.join(__dirname, "index.html");
  let html;
  try {
    html = await fsp.readFile(p, "utf8");
  } catch {
    sendText(res, 500, "index.html not found");
    return;
  }
  sendText(res, 200, html, "text/html; charset=utf-8");
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url || "/", `http://${req.headers.host || "localhost"}`);

  if (req.method === "OPTIONS") {
    res.writeHead(204, {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, PUT, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
      "Access-Control-Max-Age": "86400",
    });
    res.end();
    return;
  }

  try {
    // ---- GET routes ----
    if (req.method === "GET") {
      if (url.pathname === "/" || url.pathname === "/index.html") {
        await sendIndexHtml(res);
        return;
      }
      if (url.pathname === "/health") {
        sendJson(res, 200, { ok: true });
        return;
      }
      if (url.pathname === "/api/sessions") {
        const sessions = await getSessionsCached();
        sendJson(res, 200, sessions);
        return;
      }
      if (url.pathname === "/api/issues") {
        const issues = await getIssues();
        sendJson(res, 200, issues);
        return;
      }
      if (url.pathname === "/api/progress") {
        const prog = await getProgress();
        sendJson(res, 200, prog);
        return;
      }
      if (url.pathname === "/api/meta") {
        await syncConcludesFromProgress();
        const meta = await readSessionMeta();
        sendJson(res, 200, meta);
        return;
      }
      if (url.pathname === "/api/eisenhower") {
        await syncConcludesFromProgress();
        const data = await getEisenhowerGroups();
        sendJson(res, 200, data);
        return;
      }
      if (url.pathname === "/api/gantt") {
        const data = await getGanttData();
        sendJson(res, 200, data);
        return;
      }
      if (url.pathname === "/api/stale") {
        const stale = await getStaleItems();
        sendJson(res, 200, stale);
        return;
      }
      if (url.pathname === "/api/live") {
        const live = await getLiveCodexSessions();
        sendJson(res, 200, live);
        return;
      }
    }

    // ---- PUT /api/meta/:sessionId ----
    const putMatch = url.pathname.match(/^\/api\/meta\/(.+)$/);
    if (req.method === "PUT" && putMatch) {
      const sessionId = decodeURIComponent(putMatch[1]);
      const body = await readBody(req);
      const meta = await readSessionMeta();
      if (!meta.sessions) meta.sessions = {};
      const existing = meta.sessions[sessionId] || {};
      meta.sessions[sessionId] = { ...existing, ...body, last_reviewed: new Date().toISOString() };
      if (body.urgency || body.importance) {
        meta.sessions[sessionId].eisenhower = computeEisenhower(
          body.urgency || existing.urgency,
          body.importance || existing.importance,
        );
      }
      await writeSessionMeta(meta);
      sendJson(res, 200, { ok: true, session: meta.sessions[sessionId] });
      return;
    }

    // ---- POST /api/meta/batch ----
    if (req.method === "POST" && url.pathname === "/api/meta/batch") {
      const body = await readBody(req);
      const meta = await readSessionMeta();
      if (!meta.sessions) meta.sessions = {};
      const updates = body.updates || body;
      if (typeof updates === "object") {
        for (const [id, patch] of Object.entries(updates)) {
          const existing = meta.sessions[id] || {};
          meta.sessions[id] = { ...existing, ...patch, last_reviewed: new Date().toISOString() };
        }
      }
      await writeSessionMeta(meta);
      sendJson(res, 200, { ok: true });
      return;
    }

    // ---- POST /api/conclude/:sessionId ----
    const concludeMatch = url.pathname.match(/^\/api\/conclude\/(.+)$/);
    if (req.method === "POST" && concludeMatch) {
      const sessionId = decodeURIComponent(concludeMatch[1]);
      const body = await readBody(req);
      const meta = await readSessionMeta();
      if (!meta.sessions) meta.sessions = {};
      if (!meta.sessions[sessionId]) {
        sendJson(res, 404, { error: `Session ${sessionId} not found` });
        return;
      }
      meta.sessions[sessionId].conclusion = body.conclusion || meta.sessions[sessionId].conclusion;
      meta.sessions[sessionId].conclusion_note = body.conclusion_note ?? meta.sessions[sessionId].conclusion_note;
      meta.sessions[sessionId].last_reviewed = new Date().toISOString();
      if (body.conclusion === "completed") {
        meta.sessions[sessionId].actual_end = new Date().toISOString().slice(0, 10);
      }
      await writeSessionMeta(meta);
      sendJson(res, 200, { ok: true, session: meta.sessions[sessionId] });
      return;
    }

    sendJson(res, 404, { error: "Not Found" });
  } catch (err) {
    sendJson(res, 500, { error: err && err.message ? err.message : String(err) });
  }
});

server.on("error", (err) => {
  if (err && err.code === "EADDRINUSE") {
    console.error(`Port ${PORT} is already in use.`);
  } else {
    console.error("Server error:", err);
  }
  process.exit(1);
});

server.listen(PORT, HOST, () => {
  console.log(`Session dashboard listening on http://${HOST}:${PORT}`);
  if (HOST !== "localhost") console.log(`(Also try) http://localhost:${PORT}`);
});
