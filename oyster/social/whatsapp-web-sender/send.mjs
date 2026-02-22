import { chromium } from 'playwright-core';
import fs from 'node:fs';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';

function parseArgs(argv) {
  const args = {
    headless: true,
    dryRun: false,
    diagnose: false,
    loginOnly: false,
    loginMethod: 'qr', // qr|phone
    loginPhone: undefined,
    liveQr: false,
    liveQrPort: 0,
    to: undefined,
    text: undefined,
    profileDir: path.join(os.homedir(), '.whatsapp-web-sender', 'profile'),
    chromePath: process.env.WHATSAPP_CHROME_PATH || process.env.CHROME_PATH,
    waitLoginSecs: 180,
  };

  const it = argv[Symbol.iterator]();
  // Skip node + script
  it.next();
  it.next();

  for (let cur = it.next(); !cur.done; cur = it.next()) {
    const a = cur.value;
    if (a === '--headed') args.headless = false;
    else if (a === '--headless') args.headless = true;
    else if (a === '--dry-run') args.dryRun = true;
    else if (a === '--diagnose') args.diagnose = true;
    else if (a === '--login-only') args.loginOnly = true;
    else if (a === '--login-method') args.loginMethod = it.next().value;
    else if (a === '--login-phone') args.loginPhone = it.next().value;
    else if (a === '--live-qr') args.liveQr = true;
    else if (a === '--live-qr-port') args.liveQrPort = Number(it.next().value);
    else if (a === '--to' || a === '-t') args.to = it.next().value;
    else if (a === '--text' || a === '-m') args.text = it.next().value;
    else if (a === '--profile') args.profileDir = it.next().value;
    else if (a === '--chrome') args.chromePath = it.next().value;
    else if (a === '--wait-login-secs') args.waitLoginSecs = Number(it.next().value);
    else throw new Error(`Unknown arg: ${a}`);
  }

  return args;
}

function ensureDir(p) {
  fs.mkdirSync(p, { recursive: true });
}

function resolveChromeExecutable(userProvidedPath) {
  const candidates = [
    userProvidedPath,
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  ].filter(Boolean);

  for (const p of candidates) {
    if (fs.existsSync(p)) return p;
  }

  throw new Error(
    `Chrome not found. Install Google Chrome or pass --chrome /path/to/Chrome. Tried: ${candidates.join(', ')}`
  );
}

async function captureDiagnostics(page, outputDir, label) {
  const ts = new Date().toISOString().replace(/[:.]/g, '-');
  const pngPath = path.join(outputDir, `${label}_${ts}.png`);
  await page.screenshot({ path: pngPath, fullPage: true });

  const diag = await page.evaluate(() => {
    const testids = Array.from(document.querySelectorAll('[data-testid]'))
      .map((el) => el.getAttribute('data-testid'))
      .filter(Boolean);
    const uniqueTestids = Array.from(new Set(testids)).sort();

    const ariaLabels = Array.from(document.querySelectorAll('[aria-label]'))
      .map((el) => el.getAttribute('aria-label'))
      .filter(Boolean);
    const uniqueAriaLabels = Array.from(new Set(ariaLabels)).sort();

    return {
      title: document.title,
      url: location.href,
      testids: uniqueTestids.slice(0, 200),
      ariaLabels: uniqueAriaLabels.slice(0, 200),
    };
  });

  const jsonPath = path.join(outputDir, `${label}_${ts}.json`);
  fs.writeFileSync(jsonPath, JSON.stringify({ ...diag, screenshot: pngPath }, null, 2));

  return { pngPath, jsonPath, ts };
}

async function captureQrOnly(page, outputDir, ts) {
  const qr = page
    .locator('div[data-testid="qrcode"], canvas[aria-label*="QR"], canvas[aria-label*="Scan"], [data-testid="qr-code"]')
    .first();
  if (!(await qr.isVisible({ timeout: 2000 }).catch(() => false))) return null;

  const qrPngPath = path.join(outputDir, `whatsapp_qr_only_${ts}.png`);
  await qr.screenshot({ path: qrPngPath });
  return qrPngPath;
}

async function startLiveQr(page, outputDir, { port = 0, intervalMs = 1000 } = {}) {
  const pngPath = path.join(outputDir, 'whatsapp_qr_live.png');
  const tmpPath = `${pngPath}.tmp.png`;

  const html = `<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\" />\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />\n<title>WhatsApp Web QR</title>\n<style>\n  body { font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial; padding: 24px; line-height: 1.4; }\n  .wrap { max-width: 720px; margin: 0 auto; }\n  img { width: 360px; height: 360px; image-rendering: pixelated; border: 1px solid #ddd; border-radius: 12px; }\n  .muted { color: #555; }\n  code { background: #f4f4f4; padding: 2px 6px; border-radius: 6px; }\n</style>\n</head>\n<body>\n<div class=\"wrap\">\n  <h1>WhatsApp Web Login</h1>\n  <p>Open WhatsApp on your phone: <b>Settings</b> &rarr; <b>Linked devices</b> &rarr; <b>Link a device</b>, then scan.</p>\n  <p class=\"muted\">This page refreshes the QR automatically. Keep it open until the script reports login success.</p>\n  <p><img id=\"qr\" alt=\"WhatsApp QR\" src=\"/qr.png\" /></p>\n  <p class=\"muted\">Last refresh: <span id=\"ts\">...</span></p>\n  <script>\n    const img = document.getElementById('qr');\n    const ts = document.getElementById('ts');\n    function refresh() {\n      img.src = '/qr.png?ts=' + Date.now();\n      ts.textContent = new Date().toLocaleTimeString();\n    }\n    setInterval(refresh, 1000);\n    refresh();\n  </script>\n</div>\n</body>\n</html>\n`;

  let stopped = false;

  const server = http.createServer((req, res) => {
    try {
      const url = new URL(req.url ?? '/', 'http://127.0.0.1');
      if (req.method !== 'GET') {
        res.statusCode = 405;
        res.setHeader('content-type', 'text/plain; charset=utf-8');
        res.end('Method not allowed');
        return;
      }

      if (url.pathname === '/' || url.pathname === '/index.html') {
        res.statusCode = 200;
        res.setHeader('content-type', 'text/html; charset=utf-8');
        res.setHeader('cache-control', 'no-store, max-age=0');
        res.end(html);
        return;
      }

      if (url.pathname === '/qr.png') {
        if (!fs.existsSync(pngPath)) {
          res.statusCode = 503;
          res.setHeader('content-type', 'text/plain; charset=utf-8');
          res.setHeader('cache-control', 'no-store, max-age=0');
          res.end('QR not ready yet. Refresh.');
          return;
        }

        res.statusCode = 200;
        res.setHeader('content-type', 'image/png');
        res.setHeader('cache-control', 'no-store, max-age=0');
        fs.createReadStream(pngPath).pipe(res);
        return;
      }

      res.statusCode = 404;
      res.setHeader('content-type', 'text/plain; charset=utf-8');
      res.end('Not found');
    } catch (err) {
      res.statusCode = 500;
      res.setHeader('content-type', 'text/plain; charset=utf-8');
      res.end(String(err?.message || err));
    }
  });

  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(port, '127.0.0.1', resolve);
  });

  const address = server.address();
  const actualPort = typeof address === 'object' && address ? address.port : port;
  const liveUrl = `http://127.0.0.1:${actualPort}/`;

  const qrLocator = page
    .locator('div[data-testid=\"qrcode\"], canvas[aria-label*=\"QR\"], canvas[aria-label*=\"Scan\"], [data-testid=\"qr-code\"]')
    .first();

  async function updateQrOnce() {
    if (!(await qrLocator.isVisible({ timeout: 500 }).catch(() => false))) return false;
    await qrLocator.screenshot({ path: tmpPath });
    fs.renameSync(tmpPath, pngPath);
    return true;
  }

  // Try once immediately so the URL isn't blank on first load.
  await updateQrOnce().catch((err) => {
    console.error(`[whatsapp-web-sender] Live QR first capture failed: ${String(err?.message || err)}`);
  });

  const loop = (async () => {
    let lastErrPrint = 0;
    while (!stopped) {
      try {
        await updateQrOnce();
      } catch {
        const now = Date.now();
        if (now - lastErrPrint > 10_000) {
          lastErrPrint = now;
          // Best-effort; page may be navigating or QR temporarily hidden.
          console.error('[whatsapp-web-sender] Live QR update failed (will retry)...');
        }
      }
      await page.waitForTimeout(intervalMs);
    }
  })();

  const stop = async () => {
    stopped = true;
    try {
      await loop;
    } catch {
      // ignore
    }
    await new Promise((resolve) => server.close(resolve));
  };

  return { url: liveUrl, pngPath, stop };
}

async function waitForEither(page, locators, timeoutMs) {
  const start = Date.now();
  // Polling loop keeps this robust even if selectors are slightly off.
  while (Date.now() - start < timeoutMs) {
    for (const [key, locator] of locators) {
      try {
        if (await locator.first().isVisible({ timeout: 250 })) return key;
      } catch {
        // ignore transient DOM errors
      }
    }
    await page.waitForTimeout(250);
  }
  return null;
}

async function ensureLoggedIn(page, outputDir, opts) {
  const { waitLoginSecs = 180, liveQr = false, liveQrPort = 0 } = opts ?? {};
  await page.goto('https://web.whatsapp.com/', { waitUntil: 'domcontentloaded' });

  const qrSelectors = [
    'div[data-testid="qrcode"]',
    'canvas[aria-label*="QR"]',
    'canvas[aria-label*="Scan"]',
    '[data-testid="qr-code"]',
  ];
  const appSelectors = [
    '[data-testid="chat-list"]',
    '[aria-label="Chat list"]',
    '[data-testid="chatlist-header"]',
    '[data-testid="chat-list-search"]',
    'div[role="application"] [contenteditable="true"][role="textbox"]',
  ];

  const state = await waitForEither(
    page,
    [
      ['qr', page.locator(qrSelectors.join(','))],
      ['app', page.locator(appSelectors.join(','))],
    ],
    30_000
  );

  if (state === 'app') return { loggedIn: true };

  if (state !== 'qr') {
    const { pngPath, jsonPath } = await captureDiagnostics(page, outputDir, 'whatsapp_unknown_state');
    throw new Error(`Could not determine WhatsApp login state. Diagnostics: ${jsonPath} (screenshot: ${pngPath})`);
  }

  const { pngPath, jsonPath, ts } = await captureDiagnostics(page, outputDir, 'whatsapp_qr');
  const qrOnlyPngPath = await captureQrOnly(page, outputDir, ts).catch(() => null);
  // Print early so the user can scan while this process is still waiting.
  // Use stderr to avoid breaking the machine-readable JSON printed to stdout.
  console.error(`[whatsapp-web-sender] QR captured: ${pngPath}`);
  if (qrOnlyPngPath) console.error(`[whatsapp-web-sender] QR only: ${qrOnlyPngPath}`);
  console.error('[whatsapp-web-sender] Scan with WhatsApp Mobile: Settings -> Linked devices -> Link a device.');

  let live = null;
  try {
    if (liveQr) {
      live = await startLiveQr(page, outputDir, { port: liveQrPort });
      console.error(`[whatsapp-web-sender] Live QR URL: ${live.url}`);
    }

    // Wait for login to complete.
    const loggedInState = await waitForEither(
      page,
      [['app', page.locator(appSelectors.join(','))]],
      waitLoginSecs * 1000
    );

    const qr = {
      pngPath,
      jsonPath,
      qrOnlyPngPath,
      liveQrUrl: live?.url,
      liveQrPngPath: live?.pngPath,
    };

    if (loggedInState === 'app') return { loggedIn: true, qr };
    return { loggedIn: false, qr };
  } finally {
    await live?.stop?.().catch(() => {});
  }
}

function normalizePhone(input) {
  const s = String(input || '').trim();
  if (!s) return null;
  const digits = s.replace(/[^0-9]/g, '');
  return digits || null;
}

function normalizeE164ish(input) {
  const s = String(input || '').trim();
  if (!s) return null;
  const digits = s.replace(/[^0-9]/g, '');
  if (!digits) return null;
  return s.startsWith('+') ? `+${digits}` : `+${digits}`;
}

async function maybeSwitchToPhoneLogin(page) {
  // WhatsApp uses slightly different copy depending on locale/experiment.
  const candidates = [
    page.locator('text=Log in with phone number').first(),
    page.locator('text=Link with phone number instead').first(),
  ];
  for (const link of candidates) {
    if (await link.isVisible({ timeout: 1500 }).catch(() => false)) {
      await link.click();
      await page.waitForTimeout(1500);
      return true;
    }
  }
  return false;
}

async function phoneLoginFlow(page, outputDir, waitLoginSecs, loginPhoneRaw) {
  // If already logged in for this profile, no-op.
  await page.goto('https://web.whatsapp.com/', { waitUntil: 'domcontentloaded' });

  const appSelectors = [
    '[data-testid="chat-list"]',
    '[aria-label="Chat list"]',
    '[data-testid="chatlist-header"]',
    '[data-testid="chat-list-search"]',
    'div[role="application"] [contenteditable="true"][role="textbox"]',
  ];

  const qrSelectors = [
    'div[data-testid="qrcode"]',
    'canvas[aria-label*="QR"]',
    'canvas[aria-label*="Scan"]',
    '[data-testid="qr-code"]',
  ];

  const initialState = await waitForEither(
    page,
    [
      ['app', page.locator(appSelectors.join(','))],
      ['qr', page.locator(qrSelectors.join(','))],
    ],
    30_000
  );

  if (initialState === 'app') return { loggedIn: true };

  await maybeSwitchToPhoneLogin(page);

  const phoneInput = page.locator('input[aria-label="Type your phone number to log in to WhatsApp"]').first();
  await phoneInput.waitFor({ state: 'visible', timeout: 30_000 });

  const loginPhone = normalizeE164ish(loginPhoneRaw);
  if (!loginPhone) {
    const { pngPath, jsonPath } = await captureDiagnostics(page, outputDir, 'whatsapp_phone_login');
    // Use stderr to avoid breaking the machine-readable JSON printed to stdout.
    console.error(`[whatsapp-web-sender] Phone login page captured: ${pngPath}`);
    console.error('[whatsapp-web-sender] Re-run with: --login-phone \"+<countrycode><number>\" (E.164), then follow the on-phone linking steps.');
    return { loggedIn: false, phone: { pngPath, jsonPath } };
  }

  await phoneInput.fill(loginPhone);

  const nextBtn = page.locator('button:has-text("Next")').first();
  await nextBtn.click();

  // Give the page time to validate/navigate.
  await page.waitForTimeout(2500);

  const after = await captureDiagnostics(page, outputDir, 'whatsapp_phone_after_next');
  console.error(`[whatsapp-web-sender] After Next: ${after.pngPath}`);
  console.error('[whatsapp-web-sender] On your phone: WhatsApp -> Settings -> Linked devices -> Link a device -> \"Link with phone number\" (if shown).');

  // Wait for login to complete (same as QR path).
  const loggedInState = await waitForEither(
    page,
    [['app', page.locator(appSelectors.join(','))]],
    waitLoginSecs * 1000
  );

  if (loggedInState === 'app') return { loggedIn: true, phone: { ...after, loginPhone } };
  return { loggedIn: false, phone: { ...after, loginPhone } };
}

async function sendWhatsAppMessage(page, { to, text, dryRun }, outputDir) {
  const phone = normalizePhone(to);
  if (!phone) throw new Error('Missing/invalid --to. Expected international phone number digits, e.g. +14155551234');
  if (typeof text !== 'string' || !text.trim()) throw new Error('Missing/invalid --text');

  const url = `https://web.whatsapp.com/send?phone=${encodeURIComponent(phone)}&text=${encodeURIComponent(text)}&type=phone_number&app_absent=0`;
  await page.goto(url, { waitUntil: 'domcontentloaded' });

  // Message box appears after chat loads.
  const messageBox = page
    .locator('[data-testid="conversation-compose-box-input"], footer [contenteditable="true"][role="textbox"]')
    .first();

  await messageBox.waitFor({ state: 'visible', timeout: 60_000 });

  if (dryRun) {
    const { pngPath, jsonPath } = await captureDiagnostics(page, outputDir, 'whatsapp_dry_run');
    return { sent: false, dryRun: true, diagnostics: { pngPath, jsonPath } };
  }

  // WhatsApp pre-fills the text from the URL; hitting Enter sends.
  await messageBox.focus();
  await page.keyboard.press('Enter');

  // Verify: text should appear somewhere in the conversation soon after sending.
  const snippet = text.trim().slice(0, 32).replace(/"/g, '');
  if (snippet) {
    try {
      await page.locator(`text=${snippet}`).first().waitFor({ timeout: 20_000 });
    } catch {
      // Fall back to diagnostics for manual verification.
    }
  }

  const { pngPath, jsonPath } = await captureDiagnostics(page, outputDir, 'whatsapp_sent');
  return { sent: true, diagnostics: { pngPath, jsonPath } };
}

async function main() {
  const args = parseArgs(process.argv);

  if (!['qr', 'phone'].includes(args.loginMethod)) {
    throw new Error(`Invalid --login-method: ${args.loginMethod}. Expected: qr|phone`);
  }

  const chrome = resolveChromeExecutable(args.chromePath);

  ensureDir(path.dirname(args.profileDir));
  ensureDir(args.profileDir);

  const outputDir = path.join(process.cwd(), 'output');
  ensureDir(outputDir);

  const context = await chromium.launchPersistentContext(args.profileDir, {
    executablePath: chrome,
    headless: args.headless,
    deviceScaleFactor: 2,
    viewport: { width: 1280, height: 800 },
    args: [
      '--disable-blink-features=AutomationControlled',
      '--no-first-run',
      '--no-default-browser-check',
    ],
  });

  const page = context.pages()[0] ?? (await context.newPage());
  page.setDefaultTimeout(60_000);

  try {
    const login =
      args.loginMethod === 'phone'
        ? await phoneLoginFlow(page, outputDir, args.waitLoginSecs, args.loginPhone)
        : await ensureLoggedIn(page, outputDir, {
            waitLoginSecs: args.waitLoginSecs,
            liveQr: args.liveQr,
            liveQrPort: args.liveQrPort,
          });

    if (args.diagnose) {
      const { pngPath, jsonPath } = await captureDiagnostics(page, outputDir, 'whatsapp_diagnose');
      console.log(JSON.stringify({ ok: true, login, diagnose: { pngPath, jsonPath } }, null, 2));
      return;
    }

    if (!login.loggedIn) {
      console.log(
        JSON.stringify(
          {
            ok: false,
            error: 'NOT_LOGGED_IN',
            qr: login.qr,
            phone: login.phone,
            hint:
              args.loginMethod === 'phone'
                ? 'Complete phone login on WhatsApp Mobile (Linked devices), then re-run.'
                : 'Scan the QR code with WhatsApp Mobile: Settings -> Linked devices -> Link a device, then re-run.',
          },
          null,
          2
        )
      );
      process.exitCode = 2;
      return;
    }

    if (args.loginOnly) {
      console.log(JSON.stringify({ ok: true, loginOnly: true }, null, 2));
      return;
    }

    const result = await sendWhatsAppMessage(page, args, outputDir);
    console.log(JSON.stringify({ ok: true, result }, null, 2));
  } finally {
    await context.close();
  }
}

main().catch((err) => {
  console.error(err?.stack || String(err));
  process.exitCode = 1;
});
