#!/bin/bash
# GLM-5 执行层节点配置脚本
# 用法: bash setup-glm-node.sh <z.ai-api-key>
# 或: bash setup-glm-node.sh  (从环境变量 ZAI_API_KEY 读取)

set -e

KEY="${1:-$ZAI_API_KEY}"
if [ -z "$KEY" ]; then
    echo "ERROR: 需要 z.ai API key"
    echo "用法: bash setup-glm-node.sh <api-key>"
    exit 1
fi

echo "=== GLM-5 Node Setup ==="

# 1. 确保 Node.js 18+
if ! command -v node &>/dev/null || [ "$(node -v | cut -d'.' -f1 | tr -d 'v')" -lt 18 ]; then
    echo "[1/4] Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - 2>/dev/null || true
    sudo apt-get install -y nodejs 2>/dev/null || brew install node 2>/dev/null || true
else
    echo "[1/4] Node.js $(node -v) OK"
fi

# 2. 安装 Claude Code
if ! command -v claude &>/dev/null; then
    echo "[2/4] Installing Claude Code..."
    npm install -g @anthropic-ai/claude-code
else
    echo "[2/4] Claude Code $(claude --version 2>/dev/null) OK"
fi

# 3. 配置 z.ai 环境变量
echo "[3/4] Configuring z.ai GLM-5..."
mkdir -p ~/.claude
cat > ~/.claude/settings.json << SETTINGS
{
    "env": {
        "ANTHROPIC_AUTH_TOKEN": "$KEY",
        "ANTHROPIC_BASE_URL": "https://api.z.ai/api/anthropic",
        "API_TIMEOUT_MS": "3000000"
    }
}
SETTINGS

# 4. 创建 claude-glm alias
SHELL_RC="$HOME/.bashrc"
[ -f "$HOME/.zshrc" ] && SHELL_RC="$HOME/.zshrc"

if ! grep -q "claude-glm" "$SHELL_RC" 2>/dev/null; then
    cat >> "$SHELL_RC" << 'ALIAS'

# GLM-5 执行层 (z.ai Max Plan)
alias claude-glm='claude'
ALIAS
    echo "[4/4] Added claude-glm alias to $SHELL_RC"
else
    echo "[4/4] claude-glm alias already exists"
fi

# 验证
echo ""
echo "=== Verification ==="
echo "Node: $(node -v)"
echo "Claude: $(claude --version 2>/dev/null || echo 'not found')"
echo "Testing z.ai API..."
claude -p "Reply with just: GLM-5 OK" 2>/dev/null && echo "=== GLM-5 Node Ready ===" || echo "=== API Test Failed ==="
