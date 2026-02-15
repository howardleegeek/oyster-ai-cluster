#!/bin/bash
# install-agent-daemon.sh - 部署 Agent Daemon 到节点

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DAEMON_SCRIPT="$SCRIPT_DIR/agent-daemon.py"
SOCKET_PATH="/tmp/agent-daemon.sock"

echo "=== Agent Daemon Installer ==="

# 1. 安装依赖
echo "[1/4] Installing dependencies..."
pip3 install aiohttp --quiet 2>/dev/null || pip install aiohttp --quiet 2>/dev/null

# 2. 复制 daemon 脚本
echo "[2/4] Copying agent-daemon.py..."
DAEMON_DIR="$HOME/.agent-daemon"
mkdir -p "$DAEMON_DIR"
cp "$DAEMON_SCRIPT" "$DAEMON_DIR/"

# 3. 配置启动（使用 tmux 或后台）
echo "[3/4] Starting daemon..."

# 杀掉旧进程
pkill -f "agent-daemon.py" 2>/dev/null || true
sleep 1

# 启动新进程
nohup python3 "$DAEMON_DIR/agent-daemon.py" > /tmp/agent-daemon.log 2>&1 &
echo "  Started in background (PID: $!)"

# 4. 等待 socket 就绪
echo "[4/4] Waiting for daemon..."
for i in {1..30}; do
    if [ -S "$SOCKET_PATH" ]; then
        echo "  Socket ready!"
        break
    fi
    sleep 1
    echo -n "."
done
echo ""

# 验证
if [ -S "$SOCKET_PATH" ]; then
    echo "✓ Agent Daemon installed successfully"
    echo "  Socket: $SOCKET_PATH"
    echo "  Log: /tmp/agent-daemon.log"
    echo ""
    echo "To check logs: tail -f /tmp/agent-daemon.log"
else
    echo "✗ Failed to start daemon"
    echo "Check logs: cat /tmp/agent-daemon.log"
    exit 1
fi
