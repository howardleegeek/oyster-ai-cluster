#!/usr/bin/env python3
"""
Context Hub (localhost HTTP) -> append NDJSON events to ai_os/events/YYYY-MM.ndjson


- Receives POST /report with JSON:
  { "source": "chrome", "domain": "...", "title": "...", "intent": "bd|research|content|infra|none" }


- Writes events:
  - context.browser
  - intent.set (when intent != none)
"""

import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EVENTS_DIR = os.path.join(ROOT, "events")


def now_iso_local() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)


def month_key(ts_iso: str) -> str:
    return ts_iso[:7]


def append_event(event: dict) -> str:
    ensure_dir(EVENTS_DIR)
    path = os.path.join(EVENTS_DIR, f"{month_key(event['ts'])}.ndjson")
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    return path


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: dict):
        data = json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        # allow only localhost callers; extension uses localhost anyway
        self.send_header("Access-Control-Allow-Origin", "chrome-extension://*")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "chrome-extension://*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-AIOS-Token")
        self.end_headers()

    def do_POST(self):
        if urlparse(self.path).path != "/report":
            return self._send(404, {"ok": False, "error": "not_found"})

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"

        try:
            payload = json.loads(raw.decode("utf-8"))
        except Exception:
            return self._send(400, {"ok": False, "error": "bad_json"})

        # Optional shared secret (recommended). If not set, accept local calls.
        expected = os.environ.get("AIOS_TOKEN")
        got = self.headers.get("X-AIOS-Token")
        if expected and got != expected:
            return self._send(401, {"ok": False, "error": "unauthorized"})

        source = payload.get("source", "chrome")
        domain = payload.get("domain", "")
        title = payload.get("title", "")
        intent = payload.get("intent", "none")

        ts = now_iso_local()

        # context.browser
        append_event(
            {
                "ts": ts,
                "actor": "agent",
                "project": "GLOBAL",
                "type": "context.browser",
                "summary": f"[{source}] Active domain={domain}",
                "refs": {"source": source, "domain": domain},
                "meta": {"title": title[:120]} if title else {},
            }
        )

        # intent.set
        if intent and intent != "none":
            append_event(
                {
                    "ts": ts,
                    "actor": "user",
                    "project": "GLOBAL",
                    "type": "intent.set",
                    "summary": f"User intent set to {intent} (via {source})",
                    "refs": {"source": source, "domain": domain},
                    "meta": {"intent": intent},
                }
            )

        return self._send(200, {"ok": True})


def main():
    ensure_dir(EVENTS_DIR)
    host = "127.0.0.1"
    port = int(os.environ.get("AIOS_HUB_PORT", "8787"))
    httpd = HTTPServer((host, port), Handler)
    print(f"Context Hub listening on http://{host}:{port}/report")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
