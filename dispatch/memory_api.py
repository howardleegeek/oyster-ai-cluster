#!/usr/bin/env python3
"""
Memory API Server - REST API for memory queries

Provides endpoints:
- GET /health - Health check
- GET /memory/search?q=<query>&type=<type>&limit=<n> - Semantic search
- GET /memory/stats - Memory statistics
- POST /memory/add - Add a memory entry
- POST /memory/learn - Learn from recent dispatch tasks
"""

import json
import sys
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add dispatch to path
sys.path.insert(0, str(Path(__file__).parent))

from memory_store import MemoryStore


class MemoryHandler(BaseHTTPRequestHandler):
    """HTTP handler for memory API"""

    store = MemoryStore()

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

    def send_json(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/health":
            self.send_json({"status": "ok"})

        elif path == "/memory/stats":
            try:
                stats = self.store.get_stats()
                self.send_json(stats)
            except Exception as e:
                self.send_json({"error": str(e)}, 500)

        elif path == "/memory/search":
            q = query.get("q", [""])[0]
            mem_type = query.get("type", [None])[0]
            limit = int(query.get("limit", [5])[0])

            if not q:
                self.send_json({"error": "Missing query parameter q"}, 400)
                return

            try:
                results = self.store.search(q, memory_type=mem_type, limit=limit)
                self.send_json({"query": q, "count": len(results), "results": results})
            except Exception as e:
                self.send_json({"error": str(e)}, 500)

        else:
            self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        """Handle POST requests"""
        parsed = urlparse(self.path)
        path = parsed.path

        # Read body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else "{}"

        try:
            data = json.loads(body)
        except:
            self.send_json({"error": "Invalid JSON"}, 400)
            return

        if path == "/memory/add":
            content = data.get("content")
            mem_type = data.get("type", "task")

            if not content:
                self.send_json({"error": "Missing content"}, 400)
                return

            try:
                memory_id = self.store.add(content, mem_type, data.get("metadata"))
                self.send_json({"status": "ok", "memory_id": memory_id})
            except Exception as e:
                self.send_json({"error": str(e)}, 500)

        elif path == "/memory/learn":
            # Learn from dispatch tasks
            from datetime import datetime, timedelta
            import sqlite3

            hours = data.get("hours", 24)
            db_path = data.get(
                "db_path", str(Path.home() / "Downloads" / "dispatch" / "dispatch.db")
            )

            try:
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row

                cutoff = datetime.now() - timedelta(hours=hours)
                tasks = conn.execute(
                    """
                    SELECT id, status, error, node, duration_seconds
                    FROM tasks 
                    WHERE completed_at > ?
                    AND status IN ('completed', 'failed')
                """,
                    (cutoff.isoformat(),),
                ).fetchall()
                conn.close()

                learned = 0
                for task in tasks:
                    content = f"Task {task['id']}: status={task['status']}"
                    if task["duration_seconds"]:
                        content += f", duration={task['duration_seconds']:.1f}s"
                    if task["error"]:
                        content += f", error={task['error'][:100]}"

                    mem_type = "task" if task["status"] == "completed" else "error"
                    self.store.add(
                        content,
                        mem_type,
                        {"task_id": task["id"], "status": task["status"]},
                    )
                    learned += 1

                self.send_json({"status": "ok", "learned": learned})
            except Exception as e:
                self.send_json({"error": str(e)}, 500)

        else:
            self.send_json({"error": "Not found"}, 404)


def run_server(port=8765):
    """Run the memory API server"""
    server = HTTPServer(("0.0.0.0", port), MemoryHandler)
    print(f"Memory API server running on http://localhost:{port}")
    print(f"Endpoints:")
    print(f"  GET  /health")
    print(f"  GET  /memory/search?q=<query>&type=<type>&limit=<n>")
    print(f"  GET  /memory/stats")
    print(f"  POST /memory/add")
    print(f"  POST /memory/learn")
    server.serve_forever()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Memory API Server")
    parser.add_argument("--port", type=int, default=8765, help="Port to listen on")
    args = parser.parse_args()

    run_server(args.port)
