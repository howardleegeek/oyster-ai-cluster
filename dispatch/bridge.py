#!/usr/bin/env python3
"""
Opus <-> OpenCode 实时消息桥梁
SQLite 消息队列，双向轮询。

用法:
  # Python API
  from bridge import Bridge
  b = Bridge("opus")
  b.send("opencode", "chat", {"text": "帮我检查状态"})
  msgs = b.recv()

  # CLI
  BRIDGE_IDENTITY=opus python3 bridge.py send opencode chat '{"text":"hello"}'
  BRIDGE_IDENTITY=opencode python3 bridge.py recv
  python3 bridge.py listen
  python3 bridge.py ping opencode
  python3 bridge.py cleanup
"""
import sqlite3
import json
import os
import sys
import time

DEFAULT_DB_PATH = os.path.expanduser("~/Downloads/dispatch/bridge.db")
POLL_INTERVAL = 0.5


class Bridge:
    def __init__(self, identity: str, db_path: str = DEFAULT_DB_PATH):
        self.identity = identity
        self.db_path = db_path
        self._ensure_db()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = self._get_conn()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts REAL NOT NULL DEFAULT (strftime('%s','now')),
                    sender TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    msg_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    read_at REAL,
                    reply_to INTEGER
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_unread ON messages(recipient, read_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_reply ON messages(reply_to)")
            conn.commit()
        finally:
            conn.close()

    def send(self, recipient: str, msg_type: str, payload: dict, reply_to: int = None) -> int:
        conn = self._get_conn()
        try:
            cur = conn.execute(
                "INSERT INTO messages (sender, recipient, msg_type, payload, reply_to) VALUES (?,?,?,?,?)",
                (self.identity, recipient, msg_type, json.dumps(payload, ensure_ascii=False), reply_to)
            )
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def recv(self, timeout: float = 0, mark_read: bool = True) -> list[dict]:
        start = time.time()
        while True:
            conn = self._get_conn()
            try:
                rows = conn.execute(
                    "SELECT * FROM messages WHERE recipient=? AND read_at IS NULL ORDER BY ts ASC",
                    (self.identity,)
                ).fetchall()
                messages = []
                for r in rows:
                    m = dict(r)
                    m['payload'] = json.loads(m['payload'])
                    messages.append(m)
                if mark_read and messages:
                    ids = [m['id'] for m in messages]
                    conn.execute(
                        f"UPDATE messages SET read_at=strftime('%s','now') WHERE id IN ({','.join('?'*len(ids))})",
                        ids
                    )
                    conn.commit()
                if messages or timeout <= 0:
                    return messages
            finally:
                conn.close()
            if time.time() - start >= timeout:
                return []
            time.sleep(POLL_INTERVAL)

    def recv_one(self, timeout: float = 30) -> dict | None:
        msgs = self.recv(timeout=timeout, mark_read=True)
        return msgs[0] if msgs else None

    def request(self, recipient: str, msg_type: str, payload: dict, timeout: float = 60) -> dict | None:
        msg_id = self.send(recipient, msg_type, payload)
        start = time.time()
        while True:
            conn = self._get_conn()
            try:
                row = conn.execute(
                    "SELECT * FROM messages WHERE sender=? AND reply_to=? ORDER BY ts ASC LIMIT 1",
                    (recipient, msg_id)
                ).fetchone()
                if row:
                    m = dict(row)
                    m['payload'] = json.loads(m['payload'])
                    # mark read
                    conn.execute("UPDATE messages SET read_at=strftime('%s','now') WHERE id=?", (m['id'],))
                    conn.commit()
                    return m
            finally:
                conn.close()
            if time.time() - start >= timeout:
                return None
            time.sleep(POLL_INTERVAL)

    def ping(self, recipient: str, timeout: float = 5) -> bool:
        msg_id = self.send(recipient, 'ping', {})
        start = time.time()
        while True:
            conn = self._get_conn()
            try:
                row = conn.execute(
                    "SELECT id FROM messages WHERE sender=? AND reply_to=?",
                    (recipient, msg_id)
                ).fetchone()
                if row:
                    return True
            finally:
                conn.close()
            if time.time() - start >= timeout:
                return False
            time.sleep(POLL_INTERVAL)

    def cleanup(self, days: int = 7) -> int:
        conn = self._get_conn()
        try:
            cutoff = time.time() - days * 86400
            cur = conn.execute("DELETE FROM messages WHERE ts < ?", (cutoff,))
            conn.commit()
            return cur.rowcount
        finally:
            conn.close()


def main():
    if len(sys.argv) < 2:
        print("Usage: bridge.py <command> [args]")
        print("  send <recipient> <msg_type> <payload_json>")
        print("  recv")
        print("  ping <recipient>")
        print("  listen")
        print("  cleanup [days]")
        print("Set BRIDGE_IDENTITY env to 'opus' or 'opencode'")
        sys.exit(1)

    identity = os.environ.get('BRIDGE_IDENTITY', 'opus')
    bridge = Bridge(identity)
    cmd = sys.argv[1]

    if cmd == 'send':
        if len(sys.argv) < 5:
            print("Usage: bridge.py send <recipient> <msg_type> <payload_json>")
            sys.exit(1)
        msg_id = bridge.send(sys.argv[2], sys.argv[3], json.loads(sys.argv[4]))
        print(msg_id)

    elif cmd == 'recv':
        for msg in bridge.recv():
            print(json.dumps(msg, ensure_ascii=False))

    elif cmd == 'ping':
        if len(sys.argv) < 3:
            print("Usage: bridge.py ping <recipient>")
            sys.exit(1)
        t = float(sys.argv[3]) if len(sys.argv) > 3 else 5
        print('true' if bridge.ping(sys.argv[2], t) else 'false')

    elif cmd == 'listen':
        print(f"[{identity}] Listening... (Ctrl+C to stop)")
        try:
            while True:
                for msg in bridge.recv(timeout=1):
                    ts = time.strftime('%H:%M:%S', time.localtime(msg['ts']))
                    print(f"[{ts}] {msg['sender']} -> {msg['msg_type']}: {json.dumps(msg['payload'], ensure_ascii=False)}")
        except KeyboardInterrupt:
            print("\nStopped")

    elif cmd == 'cleanup':
        d = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        print(f"Deleted {bridge.cleanup(d)} messages")

    else:
        print(f"Unknown: {cmd}")
        sys.exit(1)


if __name__ == '__main__':
    main()
