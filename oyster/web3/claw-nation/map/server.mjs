import http from 'node:http';
import { createReadStream, existsSync, statSync } from 'node:fs';
import { dirname, extname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { Readable } from 'node:stream';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Repo root: /.../claw-nation
const ROOT_DIR = resolve(__dirname, '..');

const PORT = Number(process.env.PORT || 3456);
const RELAY_BASE_URL = (process.env.RELAY_BASE_URL || 'http://127.0.0.1:8787').replace(/\\/+$/, '');

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.jsonl': 'application/x-ndjson; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml; charset=utf-8',
  '.txt': 'text/plain; charset=utf-8',
  '.map': 'application/json; charset=utf-8',
};

function mimeFor(path) {
  return MIME[extname(path).toLowerCase()] || 'application/octet-stream';
}

function safePathFromUrlPath(urlPath) {
  // Prevent path traversal: resolve against ROOT_DIR and ensure it stays within ROOT_DIR.
  let p = urlPath;
  try {
    p = decodeURIComponent(p);
  } catch {
    return null;
  }
  p = p.replace(/^\\/+/, '');
  const abs = resolve(ROOT_DIR, p);
  const rootWithSep = ROOT_DIR.endsWith('/') ? ROOT_DIR : `${ROOT_DIR}/`;
  if (!abs.startsWith(rootWithSep) && abs !== ROOT_DIR) return null;
  return abs;
}

function serveFile(res, absPath) {
  const st = statSync(absPath);
  res.writeHead(200, {
    'content-type': mimeFor(absPath),
    'content-length': st.size,
    'cache-control': 'no-store',
  });
  createReadStream(absPath).pipe(res);
}

async function proxyToRelay(req, res) {
  const target = new URL(req.url || '/', RELAY_BASE_URL);

  const headers = new Headers();
  for (const [k, v] of Object.entries(req.headers)) {
    if (v == null) continue;
    // Avoid hop-by-hop / conflicting headers.
    if (k.toLowerCase() === 'host') continue;
    if (k.toLowerCase() === 'connection') continue;
    if (k.toLowerCase() === 'content-length') continue;
    headers.set(k, Array.isArray(v) ? v.join(',') : String(v));
  }

  const init = { method: req.method || 'GET', headers };
  if (init.method !== 'GET' && init.method !== 'HEAD') {
    const chunks = [];
    for await (const chunk of req) chunks.push(chunk);
    init.body = Buffer.concat(chunks);
  }

  const upstream = await fetch(target, init);

  const outHeaders = {};
  upstream.headers.forEach((value, key) => {
    if (key.toLowerCase() === 'transfer-encoding') return;
    outHeaders[key] = value;
  });
  outHeaders['cache-control'] = 'no-store';

  res.writeHead(upstream.status, outHeaders);

  if (!upstream.body) return res.end();
  Readable.fromWeb(upstream.body).pipe(res);
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url || '/', 'http://localhost');

  try {
    // Same-origin relay proxy (optional but convenient).
    // With this, pages served from :3456 can call /v1/* without CORS.
    if (url.pathname.startsWith('/v1/')) {
      return await proxyToRelay(req, res);
    }

    // Friendly routes.
    if (url.pathname === '/') {
      const abs = join(ROOT_DIR, 'node-web', 'index.html');
      if (!existsSync(abs)) {
        res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' });
        return res.end('missing node-web/index.html');
      }
      return serveFile(res, abs);
    }
    if (url.pathname === '/map' || url.pathname === '/map/') {
      const abs = join(ROOT_DIR, 'map', 'heatmap.html');
      if (!existsSync(abs)) {
        res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' });
        return res.end('missing map/heatmap.html');
      }
      return serveFile(res, abs);
    }

    const abs = safePathFromUrlPath(url.pathname);
    if (!abs) {
      res.writeHead(400, { 'content-type': 'text/plain; charset=utf-8' });
      return res.end('bad path');
    }

    if (!existsSync(abs)) {
      res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' });
      return res.end('not found');
    }

    const st = statSync(abs);
    if (st.isDirectory()) {
      // Directory listing disabled; try index.html.
      const idx = join(abs, 'index.html');
      if (existsSync(idx)) return serveFile(res, idx);
      res.writeHead(403, { 'content-type': 'text/plain; charset=utf-8' });
      return res.end('directory listing disabled');
    }

    return serveFile(res, abs);
  } catch (e) {
    res.writeHead(500, { 'content-type': 'text/plain; charset=utf-8' });
    res.end(`server error: ${e?.message || e}`);
  }
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`[map] dashboard+map server listening on http://127.0.0.1:${PORT}`);
  console.log(`[map] proxy: /v1/* -> ${RELAY_BASE_URL}`);
  console.log(`[map] heatmap: http://127.0.0.1:${PORT}/map/heatmap.html`);
});

