#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# Oyster Labs Agent Worker Bootstrap
# 用法: curl -sL <URL> | bash -s -- --name node-3 --slots 8 --mode glm
# 或者: bash bootstrap.sh --name node-3 --slots 8 --mode glm
#
# 模式: glm | minimax | codex | hybrid (默认 hybrid = glm+minimax)
# 跑完后这台机器就是一个即插即用的 agent worker
# ============================================================

NODE_NAME=""
SLOTS=8
MODE="hybrid"
CONTROLLER_IP=""  # Mac-1 IP, 用于注册

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --name)    NODE_NAME="$2"; shift 2 ;;
        --slots)   SLOTS="$2"; shift 2 ;;
        --mode)    MODE="$2"; shift 2 ;;
        --controller) CONTROLLER_IP="$2"; shift 2 ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

if [[ -z "$NODE_NAME" ]]; then
    echo "ERROR: --name required (e.g. --name node-3)"
    exit 1
fi

log() { echo "[$(date -u +'%H:%M:%S')] $1"; }

log "=== Oyster Labs Agent Worker Bootstrap ==="
log "Node: $NODE_NAME | Slots: $SLOTS | Mode: $MODE"

# ---- 1. System deps ----
log "Step 1/6: System dependencies"
if command -v apt-get &>/dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y -qq git python3 python3-pip python3-venv curl jq
elif command -v brew &>/dev/null; then
    brew install jq python3 || true
fi

# ---- 2. Node.js (if not present) ----
log "Step 2/6: Node.js"
if ! command -v node &>/dev/null || [[ "$(node -v | cut -d. -f1 | tr -d v)" -lt 20 ]]; then
    curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - 2>/dev/null
    sudo apt-get install -y -qq nodejs 2>/dev/null || true
fi
log "Node.js: $(node -v 2>/dev/null || echo 'N/A')"

# ---- 3. Claude Code (if not present) ----
log "Step 3/6: Claude Code"
if ! command -v claude &>/dev/null; then
    npm install -g @anthropic-ai/claude-code 2>/dev/null || sudo npm install -g @anthropic-ai/claude-code
fi
log "Claude: $(claude --version 2>/dev/null || echo 'N/A')"

# ---- 4. API Keys ----
log "Step 4/6: API configuration"

# 创建 key 目录
mkdir -p ~/.oyster-keys

# GLM (z.ai) 配置
if [[ "$MODE" == "glm" || "$MODE" == "hybrid" ]]; then
    if [[ ! -f ~/.oyster-keys/zai.key ]]; then
        log ">>> 需要 z.ai API key, 请输入:"
        read -r ZAI_KEY
        echo "$ZAI_KEY" > ~/.oyster-keys/zai.key
        chmod 600 ~/.oyster-keys/zai.key
    fi
    ZAI_KEY=$(cat ~/.oyster-keys/zai.key)

    # 写入 bashrc (幂等)
    grep -q 'ZAI_API_KEY' ~/.bashrc 2>/dev/null || cat >> ~/.bashrc <<'GLMEOF'

# --- Oyster GLM Config ---
export ZAI_API_KEY=$(cat ~/.oyster-keys/zai.key 2>/dev/null)
export ZAI_BASE_URL=https://api.z.ai/api/paas/v4
alias claude-glm='ANTHROPIC_AUTH_TOKEN=$ZAI_API_KEY ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic claude'
GLMEOF
    log "GLM (z.ai): configured"
fi

# MiniMax 配置
if [[ "$MODE" == "minimax" || "$MODE" == "hybrid" ]]; then
    if [[ ! -f ~/.oyster-keys/minimax.key ]]; then
        log ">>> 需要 MiniMax API key, 请输入:"
        read -r MM_KEY
        echo "$MM_KEY" > ~/.oyster-keys/minimax.key
        chmod 600 ~/.oyster-keys/minimax.key
    fi

    grep -q 'MINIMAX_API_KEY' ~/.bashrc 2>/dev/null || cat >> ~/.bashrc <<'MMEOF'

# --- Oyster MiniMax Config ---
export MINIMAX_API_KEY=$(cat ~/.oyster-keys/minimax.key 2>/dev/null)
MMEOF
    log "MiniMax: configured"
fi

# Codex 配置
if [[ "$MODE" == "codex" || "$MODE" == "hybrid" ]]; then
    if command -v codex &>/dev/null; then
        log "Codex: already installed"
    else
        log "Codex: skipped (install manually if needed)"
    fi
fi

# ---- 5. Dispatch worker 目录结构 ----
log "Step 5/6: Worker directory setup"
mkdir -p ~/dispatch
mkdir -p ~/agent-worker

# 下载 task-wrapper.sh (从 controller 或 hardcode)
cat > ~/agent-worker/task-wrapper.sh <<'WRAPPEREOF'
#!/usr/bin/env bash
set -euo pipefail
# Minimal task wrapper - receives spec, runs agent, reports status
PROJECT="$1"
TASK_ID="$2"
SPEC_FILE="$3"
API_MODE="${API_MODE:-direct}"

TASK_DIR="$HOME/dispatch/$PROJECT/tasks/$TASK_ID"
STATUS_FILE="$TASK_DIR/status.json"
LOG_FILE="$TASK_DIR/task.log"
OUTPUT_DIR="$TASK_DIR/output"

mkdir -p "$TASK_DIR" "$OUTPUT_DIR"

get_timestamp() { date -u +'%Y-%m-%dT%H:%M:%S+00:00'; }
STARTED_AT=$(get_timestamp)
NODE=$(hostname)

# Status: running
cat > "$STATUS_FILE" <<EOF
{"status":"running","pid":$$,"started_at":"$STARTED_AT","node":"$NODE"}
EOF

# Heartbeat
( while true; do get_timestamp > "$TASK_DIR/heartbeat"; sleep 10; done ) &
HB_PID=$!
trap 'kill $HB_PID 2>/dev/null || true' EXIT

# Execute
cd "$OUTPUT_DIR"
set +e
if [[ "$API_MODE" == "zai" ]]; then
    export ANTHROPIC_AUTH_TOKEN=$(cat ~/.oyster-keys/zai.key 2>/dev/null)
    export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
fi
claude -p "$(cat "$SPEC_FILE")" --dangerously-skip-permissions > "$LOG_FILE" 2>&1
EXIT_CODE=$?
set -e

COMPLETED_AT=$(get_timestamp)
if [[ $EXIT_CODE -eq 0 ]]; then
    STATUS="completed"
else
    STATUS="failed"
fi

cat > "$STATUS_FILE" <<EOF
{"status":"$STATUS","pid":$$,"started_at":"$STARTED_AT","completed_at":"$COMPLETED_AT","node":"$NODE","exit_code":$EXIT_CODE}
EOF
exit $EXIT_CODE
WRAPPEREOF
chmod +x ~/agent-worker/task-wrapper.sh

# ---- 6. 注册到集群 ----
log "Step 6/6: Worker registration"

# 生成 node 注册信息
cat > ~/agent-worker/node-info.json <<EOF
{
    "name": "$NODE_NAME",
    "hostname": "$(hostname)",
    "slots": $SLOTS,
    "mode": "$MODE",
    "ip": "$(curl -s ifconfig.me 2>/dev/null || echo 'unknown')",
    "zone": "$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/zone -H 'Metadata-Flavor: Google' 2>/dev/null | awk -F/ '{print $NF}' || echo 'local')",
    "bootstrapped_at": "$(date -u +'%Y-%m-%dT%H:%M:%SZ')",
    "claude_version": "$(claude --version 2>/dev/null || echo 'unknown')",
    "node_version": "$(node -v 2>/dev/null || echo 'unknown')",
    "python_version": "$(python3 --version 2>/dev/null | awk '{print $2}' || echo 'unknown')"
}
EOF

log ""
log "=== Bootstrap Complete ==="
log "Node info: ~/agent-worker/node-info.json"
log ""
log "To use this worker:"
log "  bash ~/agent-worker/task-wrapper.sh <project> <task_id> <spec_file>"
log ""
log "To add to dispatch nodes.json on controller (Mac-1):"
log "  Name: $NODE_NAME"
log "  SSH:  gcloud compute ssh $NODE_NAME --zone=<zone> --command"
log "  Slots: $SLOTS"
log "  Mode: $MODE"
log ""
cat ~/agent-worker/node-info.json
