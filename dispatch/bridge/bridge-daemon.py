#!/usr/bin/env python3
"""
Bridge Daemon - Opus<->OpenCode 双向可靠通讯
每 2 秒轮询 bridge.db，收到消息自动执行
"""

import os
import sys
import json
import time
import sqlite3
import subprocess
import signal
from pathlib import Path
from datetime import datetime
import threading

# 配置
BRIDGE_DB = Path.home() / "Downloads" / "dispatch" / "bridge.db"
LOG_FILE = Path.home() / "Downloads" / "dispatch" / "bridge-daemon.log"
PID_FILE = Path.home() / "Downloads" / "dispatch" / "bridge-daemon.pid"
POLL_INTERVAL = 1  # 1 second for faster response


def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def get_db():
    conn = sqlite3.connect(BRIDGE_DB, timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn


def recv(identity: str):
    """接收消息"""
    conn = get_db()
    try:
        msg = conn.execute(
            """
            SELECT * FROM messages
            WHERE recipient = ? AND read_at IS NULL
            ORDER by id ASC LIMIT 1
        """,
            (identity,),
        ).fetchone()

        if msg:
            # 标记为已读
            conn.execute(
                "UPDATE messages SET read_at = ? WHERE id = ?", (time.time(), msg["id"])
            )
            conn.commit()

        conn.close()
        return dict(msg) if msg else None
    except Exception as e:
        log(f"Recv error: {e}")
        conn.close()
        return None


def send(
    sender: str, recipient: str, msg_type: str, payload: dict, reply_to: int = None
):
    """发送消息"""
    conn = get_db()
    try:
        conn.execute(
            """
            INSERT INTO messages (sender, recipient, msg_type, payload, reply_to)
            VALUES (?, ?, ?, ?, ?)
        """,
            (sender, recipient, msg_type, json.dumps(payload), reply_to),
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        log(f"Send error: {e}")
        conn.close()
        return False


def handle_chat(msg: dict):
    """处理 chat 消息 - 执行 OpenCode 命令"""
    text = msg.get("payload", {})
    if isinstance(text, str):
        try:
            text = json.loads(text)
        except:
            pass

    if isinstance(text, dict):
        text = text.get("text", str(text))

    log(f"Executing chat: {text[:100]}...")

    try:
        result = subprocess.run(
            ["opencode", "run", text], capture_output=True, text=True, timeout=300
        )

        # 回复结果
        send(
            "opencode",
            msg["sender"],
            "result",
            {
                "original": text[:200],
                "stdout": result.stdout[:2000],
                "stderr": result.stderr[:500],
                "exit_code": result.returncode,
            },
            reply_to=msg["id"],
        )

        return result.returncode == 0
    except subprocess.TimeoutExpired:
        send(
            "opencode",
            msg["sender"],
            "error",
            {"error": "Timeout after 300s"},
            reply_to=msg["id"],
        )
        return False
    except Exception as e:
        send(
            "opencode",
            msg["sender"],
            "error",
            {"error": str(e)[:500]},
            reply_to=msg["id"],
        )
        return False


def handle_command(msg: dict):
    """处理 command 消息"""
    payload = msg.get("payload", {})
    action = payload.get("action", "")

    log(f"Handling command: {action}")

    result = {"action": action, "status": "ok"}

    if action == "check_status":
        result["running_tasks"] = 4
    elif action == "ping":
        result["pong"] = True
    else:
        result["status"] = "unknown_action"

    send("opencode", msg["sender"], "result", result, reply_to=msg["id"])


def handle_ping(msg: dict):
    """处理 ping - 自动回复 pong"""
    log("Received ping, sending pong")
    send("opencode", msg["sender"], "pong", {"ts": time.time()}, reply_to=msg["id"])


def dispatch_message(msg: dict):
    """根据消息类型分发处理"""
    msg_type = msg.get("msg_type", "")

    if msg_type == "chat":
        return handle_chat(msg)
    elif msg_type == "command":
        return handle_command(msg)
    elif msg_type == "ping":
        return handle_ping(msg)
    elif msg_type == "spec":
        # 处理 spec 消息
        return True
    else:
        log(f"Unknown msg_type: {msg_type}")
        return False


def main_loop():
    """主循环"""
    identity = "opencode"
    processed_ids = set()  # Track processed message IDs to prevent loops

    log(f"Bridge daemon started, identity={identity}, poll_interval={POLL_INTERVAL}s")

    while RUNNING:
        try:
            msg = recv(identity)
            if msg:
                msg_id = msg.get("id")

                # Skip if already processed (anti-loop)
                if msg_id in processed_ids:
                    log(f"Skipping already processed message {msg_id}")
                    continue

                # Mark as processed
                processed_ids.add(msg_id)

                # Limit processed set size
                if len(processed_ids) > 1000:
                    processed_ids = set(list(processed_ids)[-500:])

                log(f"Received: {msg['msg_type']} from {msg['sender']}")

                # Add timeout to message handling
                dispatch_message(msg)
            else:
                time.sleep(POLL_INTERVAL)
        except Exception as e:
            log(f"Main loop error: {e}")
            time.sleep(POLL_INTERVAL)


def signal_handler(signum, frame):
    global RUNNING
    log("Received signal, stopping...")
    RUNNING = False


RUNNING = True


def main():
    global RUNNING

    # 写 PID 文件
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    log("Bridge daemon starting...")

    main_loop()

    # 清理
    if PID_FILE.exists():
        PID_FILE.unlink()

    log("Bridge daemon stopped")


if __name__ == "__main__":
    main()
