#!/usr/bin/env python3
"""Simple Agent Daemon"""

import os
import socket
import json
import requests
import signal
import sys

SOCKET_PATH = "/tmp/agent-daemon.sock"

API_KEY = os.environ.get("MINIMAX_API_KEY", "")
API_URL = "https://api.minimax.io/v1/text/chatcompletion_v2"
MODEL = "MiniMax-M2.5"


def handle_request(prompt: str) -> str:
    """处理请求"""
    if not API_KEY:
        return json.dumps({"error": "No API key"})

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        if resp.status_code != 200:
            return json.dumps(
                {"error": f"API error: {resp.status_code}", "detail": resp.text[:200]}
            )

        data = resp.json()
        if "choices" in data and len(data["choices"]) > 0:
            return json.dumps({"result": data["choices"][0]["message"]["content"]})
        return json.dumps({"data": data})
    except Exception as e:
        return json.dumps({"error": str(e)})


print("[Daemon] Starting...")
if os.path.exists(SOCKET_PATH):
    os.remove(SOCKET_PATH)

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(SOCKET_PATH)
server.listen(5)
print(f"[Daemon] Listening on {SOCKET_PATH}")


def cleanup(signum, frame):
    print("[Daemon] Shutting down...")
    server.close()
    sys.exit(0)


signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

while True:
    try:
        client, _ = server.accept()
        try:
            data = client.recv(4096)
            if data:
                req = json.loads(data.decode())
                prompt = req.get("prompt", "hello")
                result = handle_request(prompt)
                client.send(result.encode())
        finally:
            client.close()
    except Exception as e:
        print(f"Error: {e}")
