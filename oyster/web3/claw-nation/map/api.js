// Oysterworld coverage API helpers.
// Supports two data sources:
// - relay: calls the relay HTTP API (/v1/world/cells + /v1/world/stats)
// - file:  reads JSONL from /relay/data/events.jsonl (served by the dashboard host)

function clampInt(n, min, max, fallback) {
  const x = Number(n);
  if (!Number.isFinite(x)) return fallback;
  const xi = Math.trunc(x);
  if (xi < min || xi > max) return fallback;
  return xi;
}

function clampPosInt(n, min, max, fallback) {
  const x = Number(n);
  if (!Number.isFinite(x)) return fallback;
  const xi = Math.trunc(x);
  if (xi < min || xi > max) return fallback;
  return xi;
}

function sinceMsFromHours(hours) {
  const h = Number(hours);
  if (!Number.isFinite(h) || h <= 0) return null;
  return Date.now() - h * 3600 * 1000;
}

async function fetchWithTimeout(url, { timeoutMs = 10000, ...init } = {}) {
  const ac = new AbortController();
  const t = setTimeout(() => ac.abort(new Error('timeout')), timeoutMs);
  try {
    return await fetch(url, { ...init, signal: ac.signal });
  } finally {
    clearTimeout(t);
  }
}

async function fetchJson(url, opts) {
  const resp = await fetchWithTimeout(url, opts);
  const text = await resp.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = null;
  }
  return { resp, data, text };
}

async function fetchText(url, opts) {
  const resp = await fetchWithTimeout(url, opts);
  const text = await resp.text();
  return { resp, text };
}

function safeIso(ts) {
  if (typeof ts !== 'string' || !ts) return null;
  const ms = Date.parse(ts);
  if (!Number.isFinite(ms)) return null;
  return new Date(ms).toISOString();
}

function parseJsonl(text, { maxLines = 2_000_000 } = {}) {
  const events = [];
  if (!text) return events;
  const lines = text.split('\n');
  for (let i = 0; i < lines.length && events.length < maxLines; i++) {
    const line = lines[i];
    if (!line) continue;
    try {
      const obj = JSON.parse(line);
      if (obj && typeof obj === 'object') events.push(obj);
    } catch {
      // ignore bad lines
    }
  }
  return events;
}

function requireH3() {
  const h3 = globalThis.h3;
  if (!h3 || typeof h3.latLngToCell !== 'function' || typeof h3.cellToBoundary !== 'function') {
    throw new Error('h3-js not loaded (expected globalThis.h3)');
  }
  return h3;
}

function normalizeBaseUrl(u) {
  const s = String(u || '').trim();
  if (!s) return '';
  return s.replace(/\\/+$/, '');
}

function eventToCell(evt, res) {
  const h3 = requireH3();
  const lat = Number(evt?.lat);
  const lon = Number(evt?.lon);
  if (Number.isFinite(lat) && Number.isFinite(lon)) {
    try {
      return h3.latLngToCell(lat, lon, res);
    } catch {
      // fallthrough
    }
  }

  const cell = typeof evt?.cell === 'string' ? evt.cell : null;
  if (!cell) return null;

  // Best-effort: convert parent if possible.
  try {
    const r0 = typeof h3.getResolution === 'function' ? h3.getResolution(cell) : null;
    if (Number.isInteger(r0) && r0 === res) return cell;
    if (Number.isInteger(r0) && r0 > res && typeof h3.cellToParent === 'function') {
      return h3.cellToParent(cell, res);
    }
  } catch {
    // ignore
  }
  return null;
}

function computeFromEvents(events, { res, hours, limit }) {
  const sinceMs = sinceMsFromHours(hours);

  const counts = new Map(); // cell -> count
  const activeNodes = new Set();

  let eventsTotal = 0;
  let skipped = 0;
  let lastEvent = null;
  let lastEventTsMs = -Infinity;

  for (const evt of events) {
    const tsIso = typeof evt?.ts === 'string' ? evt.ts : '';
    const tsMs = Date.parse(tsIso);
    if (sinceMs != null && Number.isFinite(tsMs) && tsMs < sinceMs) continue;

    const cell = eventToCell(evt, res);
    if (!cell) {
      skipped++;
      continue;
    }

    eventsTotal++;
    counts.set(cell, (counts.get(cell) || 0) + 1);
    if (typeof evt?.node_id === 'string') activeNodes.add(evt.node_id);

    if (Number.isFinite(tsMs) && tsMs > lastEventTsMs) {
      lastEventTsMs = tsMs;
      lastEvent = {
        id: typeof evt?.id === 'string' ? evt.id : null,
        ts: safeIso(tsIso),
        node_id: typeof evt?.node_id === 'string' ? evt.node_id : null,
        lat: Number.isFinite(Number(evt?.lat)) ? Number(evt.lat) : null,
        lon: Number.isFinite(Number(evt?.lon)) ? Number(evt.lon) : null,
        cell,
      };
    }
  }

  const cellsAll = Array.from(counts.entries()).map(([cell, count]) => ({ cell, count }));
  cellsAll.sort((a, b) => b.count - a.count);
  const truncated = cellsAll.length > limit;
  const cells = truncated ? cellsAll.slice(0, limit) : cellsAll;

  let minCount = Infinity;
  let maxCount = 0;
  for (const c of cellsAll) {
    if (c.count < minCount) minCount = c.count;
    if (c.count > maxCount) maxCount = c.count;
  }
  if (!Number.isFinite(minCount)) minCount = 0;

  return {
    ok: true,
    source: 'file',
    res,
    since: sinceMs ? new Date(sinceMs).toISOString() : null,
    nodes_total: null, // filled by caller if available
    events_total: eventsTotal,
    unique_cells: counts.size,
    active_nodes: activeNodes.size,
    skipped_lines: skipped,
    last_event: lastEvent,
    min_count: minCount,
    max_count: maxCount,
    truncated,
    cells,
  };
}

async function loadFromRelayApi({ relayBaseUrl, res, hours, limit }) {
  const base = normalizeBaseUrl(relayBaseUrl);
  if (!base) throw new Error('missing relayBaseUrl');

  const qsCells = new URLSearchParams({ res: String(res), limit: String(limit) });
  if (hours) qsCells.set('hours', String(hours));
  const qsStats = new URLSearchParams({ res: String(res) });
  if (hours) qsStats.set('hours', String(hours));

  const [cellsResp, statsResp] = await Promise.all([
    fetchJson(`${base}/v1/world/cells?${qsCells.toString()}`, { timeoutMs: 15000 }),
    fetchJson(`${base}/v1/world/stats?${qsStats.toString()}`, { timeoutMs: 15000 }),
  ]);

  if (!cellsResp.resp.ok || !cellsResp.data?.ok) {
    throw new Error(`relay cells failed: HTTP ${cellsResp.resp.status}: ${cellsResp.text.slice(0, 300)}`);
  }
  if (!statsResp.resp.ok || !statsResp.data?.ok) {
    throw new Error(`relay stats failed: HTTP ${statsResp.resp.status}: ${statsResp.text.slice(0, 300)}`);
  }

  // Normalize to the same shape as file source.
  const cellsData = cellsResp.data;
  const statsData = statsResp.data;

  return {
    ok: true,
    source: 'relay',
    res: cellsData.res,
    since: cellsData.since ?? statsData.since ?? null,
    nodes_total: typeof statsData.nodes_total === 'number' ? statsData.nodes_total : null,
    events_total: typeof statsData.events_total === 'number' ? statsData.events_total : null,
    unique_cells: typeof statsData.unique_cells === 'number' ? statsData.unique_cells : cellsData.unique_cells,
    active_nodes: typeof statsData.active_nodes === 'number' ? statsData.active_nodes : null,
    skipped_lines: typeof statsData.skipped_lines === 'number' ? statsData.skipped_lines : cellsData.skipped_lines,
    last_event: statsData.last_event ?? null,
    min_count: typeof cellsData.min_count === 'number' ? cellsData.min_count : 0,
    max_count: typeof cellsData.max_count === 'number' ? cellsData.max_count : 0,
    truncated: Boolean(cellsData.truncated),
    cells: Array.isArray(cellsData.cells) ? cellsData.cells : [],
  };
}

async function loadFromLocalFiles({ nodesPath, eventsPath, res, hours, limit }) {
  // Events JSONL is required.
  const eventsTxt = await fetchText(eventsPath, { timeoutMs: 15000 });
  if (!eventsTxt.resp.ok) {
    throw new Error(`events fetch failed: HTTP ${eventsTxt.resp.status}`);
  }
  const events = parseJsonl(eventsTxt.text);
  const computed = computeFromEvents(events, { res, hours, limit });

  // nodes.json is optional (only used for nodes_total).
  try {
    const nodesResp = await fetchJson(nodesPath, { timeoutMs: 8000 });
    if (nodesResp.resp.ok && nodesResp.data && typeof nodesResp.data === 'object') {
      const nodesTotal = Object.keys(nodesResp.data?.nodes || {}).length;
      computed.nodes_total = nodesTotal;
    }
  } catch {
    // ignore
  }

  return computed;
}

export function defaultSettings() {
  return {
    source: 'auto', // auto | relay | file
    relayBaseUrl: 'http://127.0.0.1:8787',
    res: 9,
    hours: 24,
    limit: 15000,
  };
}

export async function loadCoverage(raw = {}) {
  // Validate inputs early.
  const source = String(raw.source || 'auto');
  const relayBaseUrl = normalizeBaseUrl(raw.relayBaseUrl || '');
  const res = clampInt(raw.res, 0, 15, 9);
  const limit = clampPosInt(raw.limit, 1, 50000, 15000);
  const hours = raw.hours === '' || raw.hours == null ? '' : clampPosInt(raw.hours, 1, 24 * 365, 24);

  const fileNodesPath = raw.fileNodesPath || '/relay/data/nodes.json';
  const fileEventsPath = raw.fileEventsPath || '/relay/data/events.jsonl';

  if (source === 'file') {
    return await loadFromLocalFiles({ nodesPath: fileNodesPath, eventsPath: fileEventsPath, res, hours, limit });
  }
  if (source === 'relay') {
    return await loadFromRelayApi({ relayBaseUrl, res, hours, limit });
  }

  // auto: try local files first (same-origin). If missing, fall back to relay API.
  try {
    return await loadFromLocalFiles({ nodesPath: fileNodesPath, eventsPath: fileEventsPath, res, hours, limit });
  } catch (eFile) {
    if (!relayBaseUrl) throw eFile;
    return await loadFromRelayApi({ relayBaseUrl, res, hours, limit });
  }
}

