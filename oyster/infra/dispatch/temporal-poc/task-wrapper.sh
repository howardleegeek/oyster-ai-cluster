#!/usr/bin/env bash
set -euo pipefail

# Task wrapper script - runs on worker nodes (via SSH or locally)
# Usage: bash task-wrapper.sh <project> <task_id> <spec_file> [repo_url] [branch]
# Environment: API_MODE=direct|zai|codex (default: direct)

if [[ $# -lt 3 || $# -gt 5 ]]; then
    echo "ERROR: Expected 3-5 arguments: project, task_id, spec_file, [repo_url], [branch]" >&2
    exit 1
fi

PROJECT="$1"
TASK_ID="$2"
SPEC_FILE="$3"
REPO_URL="${4:-}"
BRANCH="${5:-}"
API_MODE="${API_MODE:-direct}"

TASK_DIR="$HOME/dispatch/$PROJECT/tasks/$TASK_ID"

# Resolve SPEC_FILE to absolute path (worker writes spec.md into TASK_DIR which is cwd at start,
# but we cd to WORKING_DIR later, breaking relative paths)
if [[ "$SPEC_FILE" != /* ]]; then
    SPEC_FILE="$TASK_DIR/$SPEC_FILE"
fi
STATUS_FILE="$TASK_DIR/status.json"
HEARTBEAT_FILE="$TASK_DIR/heartbeat"
OUTPUT_DIR="$TASK_DIR/output"
LOG_FILE="$TASK_DIR/task.log"
REPO_DIR="$TASK_DIR/repo"
GIT_CLONE_LOG="$TASK_DIR/git_clone.log"

mkdir -p "$TASK_DIR"

# Idempotency check
if [[ -f "$STATUS_FILE" ]]; then
    STATUS=$(grep -o '"status":"[^"]*"' "$STATUS_FILE" | cut -d'"' -f4 || echo "")
    if [[ "$STATUS" == "completed" ]]; then
        echo "Task $TASK_ID already completed, skipping"
        exit 0
    fi
fi

# Git mode
if [[ -n "$REPO_URL" ]] && [[ -n "$BRANCH" ]]; then
    echo "Git mode: cloning $REPO_URL branch $BRANCH"
    # Clean stale repo dir from previous failed runs
    [[ -d "$REPO_DIR" ]] && rm -rf "$REPO_DIR"
    git clone --depth=1 --branch "$BRANCH" --single-branch "$REPO_URL" "$REPO_DIR" 2>"$GIT_CLONE_LOG" || {
        echo "Branch $BRANCH not found, creating from main"
        [[ -d "$REPO_DIR" ]] && rm -rf "$REPO_DIR"
        git clone --depth=1 "$REPO_URL" "$REPO_DIR" 2>>"$GIT_CLONE_LOG"
        cd "$REPO_DIR" && git checkout -b "$BRANCH"
    }
    GIT_MODE=true
    WORKING_DIR="$REPO_DIR"
else
    GIT_MODE=false
    WORKING_DIR="$TASK_DIR"
fi

# === SELF-HEALING: Dependency & Environment Check ===
# Ensure critical tools exist, otherwise we fail early with clear error
check_dep() {
    if ! command -v "$1" &>/dev/null; then
        echo "ERROR: Critical dependency '$1' not found on $(hostname). Please install it." >&2
        exit 127
    fi
}
check_dep "git"
check_dep "python3"
# Cross-platform md5 check (Linux: md5sum, macOS: md5)
if ! command -v md5sum &>/dev/null && ! command -v md5 &>/dev/null; then
    echo "ERROR: Neither md5sum nor md5 found." >&2
    exit 127
fi

# Cross-platform command wrappers
portable_md5() {
    if command -v md5sum &>/dev/null; then
        md5sum "$@"
    else
        md5 -r "$@"
    fi
}
portable_sha256() {
    if command -v sha256sum &>/dev/null; then
        sha256sum "$@"
    else
        shasum -a 256 "$@"
    fi
}
export -f portable_md5
export -f portable_sha256


# Ensure opencode is installed (~/.opencode/bin/opencode)
# If missing, try to install it automatically
OPENCODE_BIN="$HOME/.opencode/bin/opencode"
if [[ ! -f "$OPENCODE_BIN" ]]; then
    echo "opencode not found at $OPENCODE_BIN. Attempting auto-install..."
    curl -fsSL https://opencode.sh/install.sh | bash || {
        echo "ERROR: Failed to auto-install opencode. Node $(hostname) is unprovisioned." >&2
        exit 127
    }
fi

mkdir -p "$OUTPUT_DIR"

get_timestamp() { date -u +'%Y-%m-%dT%H:%M:%S+00:00'; }

STARTED_AT=$(get_timestamp)
NODE=$(hostname)

cat > "$STATUS_FILE" <<EOF
{"status":"running","pid":$$,"started_at":"$STARTED_AT","node":"$NODE","git_mode":$GIT_MODE}
EOF

echo "[$STARTED_AT] Starting task $TASK_ID on $NODE (PID: $$)"

# Cleanup — kill LLM process tree on exit (Temporal handles heartbeats externally)
LLM_PID=""
cleanup() {
    # Kill the LLM (opencode) process group to prevent orphans
    if [[ -n "$LLM_PID" ]] && kill -0 "$LLM_PID" 2>/dev/null; then
        kill_tree "$LLM_PID" "TERM" 2>/dev/null || true
        sleep 1
        kill_tree "$LLM_PID" "KILL" 2>/dev/null || true
    fi
    # Clean up JIT .so files to prevent disk bloat
    find /tmp -maxdepth 1 -name "*.so" -user "$(whoami)" -mmin +30 -delete 2>/dev/null || true
}
trap cleanup EXIT INT TERM
# Write initial heartbeat (Temporal activity polls this externally)
get_timestamp > "$HEARTBEAT_FILE"

cd "$WORKING_DIR"

# ╔══════════════════════════════════════════════════════════════╗
# ║  TASK_TYPE 环境分级 (2026-02-22 fix)                        ║
# ║  - backend/tool: 跑 init.sh 精简环境 (32 files OK)          ║
# ║  - frontend: 跳过 init.sh 精简，保留 node_modules/tsconfig  ║
# ║    大模型视线通过 .claudeignore 控制，磁盘环境保持完整         ║
# ╚══════════════════════════════════════════════════════════════╝
TASK_TYPE="${TASK_TYPE:-auto}"

# Auto-detect task type from spec content
if [[ "$TASK_TYPE" == "auto" ]] && [[ -f "$SPEC_FILE" ]]; then
    if grep -qiE 'frontend|react|tsx|jsx|component|ProvidersTab|web-ui|next\.js|vite|tailwind|css|styled|UI' "$SPEC_FILE" 2>/dev/null; then
        TASK_TYPE="frontend"
    elif grep -qiE 'node_modules|package\.json|npm|pnpm|yarn' "$SPEC_FILE" 2>/dev/null; then
        TASK_TYPE="frontend"
    else
        TASK_TYPE="backend"
    fi
fi

echo "[$(get_timestamp)] Task type: $TASK_TYPE"

# ╔══════════════════════════════════════════════════════════════╗
# ║  PROJECT init.sh — 环境初始化 (2026-02-20, graded 2026-02-22)║
# ║  backend: 跑 init.sh (精简 context OK)                      ║
# ║  frontend: 跳过 init.sh 精简, 用 .claudeignore 控制视线      ║
# ╚══════════════════════════════════════════════════════════════╝
INIT_SCRIPT="$WORKING_DIR/init.sh"
if [[ -f "$INIT_SCRIPT" ]]; then
    if [[ "$TASK_TYPE" == "frontend" ]]; then
        echo "[$(get_timestamp)] SKIP init.sh for frontend task (preserving node_modules + tsconfig)"
        # Create .claudeignore / .opencodeignore to limit LLM vision without destroying FS
        IGNORE_FILE="$WORKING_DIR/.opencodeignore"
        if [[ ! -f "$IGNORE_FILE" ]]; then
            cat > "$IGNORE_FILE" <<'IGNOREEOF'
# Auto-generated for frontend tasks: limit LLM context without destroying FS
node_modules/
.next/
dist/
build/
coverage/
*.lock
IGNOREEOF
            echo "[$(get_timestamp)] Created $IGNORE_FILE for frontend context control"
        fi
    else
        echo "[$(get_timestamp)] Running project init.sh (backend task)..."
        chmod +x "$INIT_SCRIPT"
        timeout 120 bash "$INIT_SCRIPT" >> "$LOG_FILE" 2>&1 || {
            echo "[$(get_timestamp)] WARNING: init.sh failed (exit=$?), continuing anyway" | tee -a "$LOG_FILE"
        }
    fi
fi

# ╔══════════════════════════════════════════════════════════════╗
# ║  PROGRESS NARRATIVE — 重试上下文注入 (2026-02-20)            ║
# ║  如果存在之前的 progress.txt，读取注入 prompt               ║
# ╚══════════════════════════════════════════════════════════════╝
PROGRESS_FILE="$TASK_DIR/progress.txt"
PREVIOUS_PROGRESS=""
if [[ -f "$PROGRESS_FILE" ]]; then
    PREVIOUS_PROGRESS=$(tail -50 "$PROGRESS_FILE")
    echo "[$(get_timestamp)] Found previous progress.txt ($(wc -l < "$PROGRESS_FILE") lines)"
fi

# === Pre-LLM snapshot for SCP mode change detection ===
# OpenCode writes directly to project dir (not output/), so we snapshot before LLM runs
PRE_SNAPSHOT="/tmp/pre-snapshot-${TASK_ID}.txt"
find "$WORKING_DIR" -type f \( -name "*.py" -o -name "*.ts" -o -name "*.js" -o -name "*.tsx" -o -name "*.jsx" -o -name "*.sh" -o -name "*.md" \) ! -path "*/node_modules/*" ! -path "*/.git/*" -newer "$STATUS_FILE" -exec perl -e 'print "$ARGV[0] " . (stat($ARGV[0]))[9] . "\n"' {} \; 2>/dev/null | sort > "$PRE_SNAPSHOT" 2>/dev/null || true
# Also capture md5 of existing files for modification detection
find "$WORKING_DIR" -type f \( -name "*.py" -o -name "*.ts" -o -name "*.js" -o -name "*.tsx" -o -name "*.jsx" -o -name "*.json" \) ! -path "*/node_modules/*" ! -path "*/.git/*" -exec bash -c 'command -v md5sum >/dev/null && md5sum "$1" || md5 -r "$1"' _ {} \; 2>/dev/null | sort > "/tmp/pre-md5-${TASK_ID}.txt" 2>/dev/null || true

# === Hard timeouts (global safety net) ===
# Goal: prevent watch / hung commands from eating critical path.
# - TASK_TIMEOUT_SECS: max wall time for the LLM run (claude/codex)
# - VERIFY_TIMEOUT_SECS: max wall time for wrapper verification tests
TASK_TIMEOUT_SECS="${TASK_TIMEOUT_SECS:-7200}"
TASK_TIMEOUT_KILL_SECS="${TASK_TIMEOUT_KILL_SECS:-30}"
VERIFY_TIMEOUT_SECS="${VERIFY_TIMEOUT_SECS:-1200}"
VERIFY_TIMEOUT_KILL_SECS="${VERIFY_TIMEOUT_KILL_SECS:-30}"

# Many test runners disable watch mode when CI is set.
export CI="${CI:-1}"

run_with_timeout() {
    local timeout_secs="$1"
    local kill_secs="$2"
    shift 2

    if command -v timeout >/dev/null 2>&1; then
        timeout -k "${kill_secs}s" "${timeout_secs}s" "$@"
        return $?
    fi

    if command -v gtimeout >/dev/null 2>&1; then
        gtimeout -k "${kill_secs}s" "${timeout_secs}s" "$@"
        return $?
    fi

    # Python fallback: kill the whole process group on timeout
    python3 - "$timeout_secs" "$kill_secs" "$@" <<'PY'
import os
import signal
import subprocess
import sys


def main() -> int:
    if len(sys.argv) < 4:
        sys.stderr.write(
            "usage: run_with_timeout <timeout_secs> <kill_secs> <cmd...>\n"
        )
        return 2

    try:
        timeout_secs = int(sys.argv[1])
        kill_secs = int(sys.argv[2])
    except ValueError:
        sys.stderr.write("invalid timeout/kill seconds\n")
        return 2

    cmd = sys.argv[3:]
    p = subprocess.Popen(cmd, start_new_session=True)
    try:
        return p.wait(timeout=timeout_secs)
    except subprocess.TimeoutExpired:
        # TERM then KILL the whole group
        try:
            os.killpg(p.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass

        try:
            p.wait(timeout=kill_secs)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

        try:
            p.wait(timeout=5)
        except Exception:
            pass
        return 124


if __name__ == "__main__":
    raise SystemExit(main())
PY
}

json_escape() {
    local s="$1"
    s=${s//\\/\\\\}
    s=${s//\"/\\\"}
    s=${s//$'\n'/\\n}
    s=${s//$'\t'/\\t}
    s=${s//$'\r'/\\r}
    s=${s//$'\f'/\\f}
    echo "$s"
}

# ╔══════════════════════════════════════════════════════════════════════╗
# ║  LLM EXECUTION ENGINE v3 — Robust fallback + stall detection      ║
# ║                                                                    ║
# ║  Architecture:                                                     ║
# ║    1. Pre-flight: quick health check on chosen model               ║
# ║    2. Execute: run with stall detection (kill if no output 5min)   ║
# ║    3. Rotate: on any failure, try next model in pool               ║
# ║    4. Escalate: if all free models fail, fall back to claude       ║
# ║    5. Kill clean: always kill entire process tree, not just PID    ║
# ╚══════════════════════════════════════════════════════════════════════╝

# === Free model rotation pool ===
# All available free models via OpenCode. Rotate on failure/timeout/stall.
# Order: most reliable first (based on observed success rates)
# OPENCODE_MODELS env can override (comma-separated)
# All free models first, then fallback chain handles paid escalation
DEFAULT_MODELS="opencode/gpt-5-nano,opencode/glm-5-free,opencode/minimax-m2.5-free,opencode/big-pickle,opencode/trinity-large-preview-free"
IFS=',' read -ra MODEL_POOL <<< "${OPENCODE_MODELS:-$DEFAULT_MODELS}"

# Per-model timeout: 20 min. Free models that don't respond in 20min are dead.
# Total budget across all models: ~100min (5 models x 20min max each)
MODEL_TIMEOUT_SECS="${MODEL_TIMEOUT_SECS:-1200}"
MODEL_TIMEOUT_KILL_SECS="${MODEL_TIMEOUT_KILL_SECS:-15}"

# Stall detection: if log file doesn't grow for 3 min, kill the process.
# This catches the #1 failure mode: opencode connects but model never responds.
STALL_TIMEOUT_SECS="${STALL_TIMEOUT_SECS:-600}"

# Pre-flight health check timeout (seconds)
HEALTH_CHECK_TIMEOUT="${HEALTH_CHECK_TIMEOUT:-30}"

# Paid fallback is always enabled: free → MiniMax API → GLM API → Codex

is_rate_limit_error() {
    # Only check last 20 lines of log (not entire agent output which may contain
    # Web3 code with words like "token", "gateway", "authentication" causing false positives)
    # (2026-02-21 fix: reduced false positive rate)
    tail -20 "$LOG_FILE" 2>/dev/null | grep -qiE '429|rate_limit|overloaded|quota|too many requests|capacity|ECONNREFUSED|ETIMEDOUT|ENOTFOUND'
}

is_empty_response() {
    # Check if log file is tiny (< 100 bytes) = model returned nothing useful
    local size=0
    [[ -f "$LOG_FILE" ]] && size=$(wc -c < "$LOG_FILE" 2>/dev/null || echo 0)
    [[ "$size" -lt 100 ]]
}

# Kill entire process tree rooted at PID (prevents zombie opencode children)
kill_tree() {
    local pid="$1"
    local sig="${2:-TERM}"
    # Get all children first
    local children
    children=$(ps -o pid= --ppid "$pid" 2>/dev/null || pgrep -P "$pid" 2>/dev/null) || true
    for child in $children; do
        kill_tree "$child" "$sig"
    done
    kill -"$sig" "$pid" 2>/dev/null || true
}

# Pre-flight health check: send a tiny prompt and see if model responds in HEALTH_CHECK_TIMEOUT
preflight_check() {
    local model="$1"
    local test_log="/tmp/preflight-${TASK_ID}-$(date +%s).log"

    echo "[$(get_timestamp)] Preflight check: $model"
    timeout "$HEALTH_CHECK_TIMEOUT" bash -c \
        "printf 'reply OK' | ~/.opencode/bin/opencode run -m \"\$1\" 2>&1 | head -5" -- "$model" > "$test_log" 2>&1
    local rc=$?

    if [[ $rc -eq 0 ]] && [[ -s "$test_log" ]]; then
        local resp_size
        resp_size=$(wc -c < "$test_log" 2>/dev/null || echo 0)
        if [[ $resp_size -gt 5 ]]; then
            echo "[$(get_timestamp)] Preflight PASS: $model (${resp_size}B response)"
            rm -f "$test_log"
            return 0
        fi
    fi

    echo "[$(get_timestamp)] Preflight FAIL: $model (rc=$rc)"
    rm -f "$test_log"
    return 1
}

# Run command with stall detection: kills if no new output for STALL_TIMEOUT_SECS
# Uses process group kill to clean up entire tree
run_with_stall_detection() {
    local timeout_secs="$1"
    local stall_secs="$2"
    local log_file="$3"
    shift 3

    # Start the command in a new process group so we can kill the whole tree
    # setsid is Linux-only; on macOS fall back to direct execution
    if command -v setsid &>/dev/null; then
        setsid "$@" > "$log_file" 2>&1 &
    else
        "$@" > "$log_file" 2>&1 &
    fi
    local CMD_PID=$!
    LLM_PID=$CMD_PID  # Export to global for cleanup trap

    local elapsed=0
    local last_size=0
    local stall_elapsed=0
    local initial_wait=60  # give model 60s to start producing output

    while kill -0 "$CMD_PID" 2>/dev/null; do
        sleep 10
        elapsed=$((elapsed + 10))

        # Check wall-clock timeout
        if [[ $elapsed -ge $timeout_secs ]]; then
            echo "[$(get_timestamp)] TIMEOUT after ${elapsed}s (wall clock)" | tee -a "$log_file"
            kill_tree "$CMD_PID" "TERM"; sleep 3; kill_tree "$CMD_PID" "KILL"
            wait "$CMD_PID" 2>/dev/null
            return 124
        fi

        # Check stall (no output growth) — skip during initial warmup
        if [[ $elapsed -gt $initial_wait ]]; then
            local cur_size=0
            if [[ -f "$log_file" ]]; then
                cur_size=$(wc -c < "$log_file" 2>/dev/null || echo 0)
            fi

            if [[ "$cur_size" -eq "$last_size" ]]; then
                stall_elapsed=$((stall_elapsed + 10))
                if [[ $stall_elapsed -ge $stall_secs ]]; then
                    echo "[$(get_timestamp)] STALL DETECTED: no output for ${stall_elapsed}s, killing" | tee -a "$log_file"
                    kill_tree "$CMD_PID" "TERM"; sleep 3; kill_tree "$CMD_PID" "KILL"
                    wait "$CMD_PID" 2>/dev/null
                    return 125  # custom code for stall
                fi
            else
                stall_elapsed=0
                last_size=$cur_size
            fi
        fi
    done

    wait "$CMD_PID"
    return $?
}

# === SPEC STANDARD HEADER ===
SPEC_STANDARD_HEADER=""
SPEC_STANDARD_PATH="$HOME/dispatch/SPEC_STANDARD.md"
if [[ -f "$SPEC_STANDARD_PATH" ]]; then
    SPEC_STANDARD_HEADER=$(cat << 'SPECEOF'

════════════════════════════════════════════════════════════════════════════
  OYSTER LABS SPEC EXECUTION STANDARD v2.0
════════════════════════════════════════════════════════════════════════════

你正在执行的任务必须遵循以下规范：

【最重要】你必须实际写入代码文件！不要只描述你会做什么。
- 你必须使用 write_file / edit_file 工具来创建和修改文件
- 光说"我会创建 X 文件"是不够的，你必须真正创建它
- 如果你只输出文字描述而没有修改任何文件，任务会自动 FAIL

【必须遵守的约束】
- Max 5 files per diff：每次改动最多 5 个文件
- No file deletion：不要删除文件，除非 spec 明确说明
- No rename of public interfaces：不要重命名公开接口
- Must add tests：新功能必须添加测试
- Preserve behavior：保持现有功能不变

【验收标准】
- spec 中定义的验收标准必须全部通过
- 验证命令必须是可执行的（非 watch 模式）
- 不要说"应该可以了"，必须跑测试证明

【禁止】
- 禁止 TODO/FIXME/placeholder 交付
- 禁止硬编码 secret
- 禁止提交 .env 文件
- 禁止只描述代码而不实际写入文件

【代码质量】
- 函数 < 30 行
- 错误处理具体（不写 except Exception）
- 日志有 context（包含 task_id）

详细规范请参考: ~/dispatch/SPEC_STANDARD.md
════════════════════════════════════════════════════════════════════════════
SPECEOF
)
fi

# ╔══════════════════════════════════════════════════════════════╗
# ║  AGENT PROTOCOL — 启动序列 + 执行规则 + 续航横幅             ║
# ║  来源: Anthropic Harness 博客 + agent-foreman + nonstop     ║
# ╚══════════════════════════════════════════════════════════════╝
AGENT_PROTOCOL=""
AGENT_PROTOCOL_PATH="$(dirname "$0")/AGENT_PROTOCOL.md"
if [[ -f "$AGENT_PROTOCOL_PATH" ]]; then
    AGENT_PROTOCOL=$(cat "$AGENT_PROTOCOL_PATH")
fi

# Extract prompt from spec file (skip YAML front-matter)
PROMPT=$(awk '/^---$/{n++; next} n>=2{print}' "$SPEC_FILE" 2>/dev/null | head -500 || true)
if [[ -z "$PROMPT" ]]; then
    PROMPT=$(cat "$SPEC_FILE")
fi

# === Inject CLAUDE.md Memory Context if it exists ===
PROJECT_CLAUDE_MD=""
# We look for it in the root of the sandbox, which the deployer might have synced
if [[ -f "$WORKING_DIR/CLAUDE.md" ]]; then
    PROJECT_CLAUDE_MD=$(cat "$WORKING_DIR/CLAUDE.md")
    echo "[$(get_timestamp)] Injected CLAUDE.md memory to prompt context"
fi

# === 组装完整 prompt: 协议 + CLAUDE历史 + 标准 + 进度上下文 + spec + 提醒 ===
PROGRESS_CONTEXT=""
if [[ -n "$PREVIOUS_PROGRESS" ]]; then
    PROGRESS_CONTEXT="
════════════════════════════════════════════════════════════════════════════
  上次执行的进度记录（仔细阅读，避免重复犯错）
════════════════════════════════════════════════════════════════════════════
${PREVIOUS_PROGRESS}
════════════════════════════════════════════════════════════════════════════
"
fi

PROMPT="${AGENT_PROTOCOL}

${PROJECT_CLAUDE_MD:+"
════════════════════════════════════════════════════════════════════════════
  CRITICAL PROJECT MEMORY (CLAUDE.md)
════════════════════════════════════════════════════════════════════════════
${PROJECT_CLAUDE_MD}
════════════════════════════════════════════════════════════════════════════
"}

${SPEC_STANDARD_HEADER}
${PROGRESS_CONTEXT}
${PROMPT}

【CRITICAL REMINDER】You MUST use apply_patch/write_file/edit_file tools to actually CREATE or MODIFY files. Do NOT just describe changes in text. If you only output text without tool calls, the task will FAIL. Start by reading the relevant files, then immediately write/edit them.

【PATH RULE】Use RELATIVE paths from the project root directory (e.g., 'src/main.py', 'tests/test_main.py'). Do NOT use absolute paths like '/home/user/...' or 'home/user/...'. The working directory is already set to the project root.

【验收标准不可修改】spec 中定义的验收标准是不可变的。你只能实现它们，绝对不能修改、删除或降低验收标准。

════════════════════════════════════════════════════════════════════════════
  不要停下来。不要问问题。做自主决策。继续工作直到所有验收标准通过。
════════════════════════════════════════════════════════════════════════════"

# Grant external_directory permission for OpenCode
export OPENCODE_PERMISSION='{"external_directory":"allow"}'

ATTEMPT=0
EXIT_CODE=1
SUCCEEDED_MODEL=""
CURRENT_MODE="${API_MODE:-opencode}"

set +e

# === Codex mode (paid, no rotation) ===
if [[ "$API_MODE" == "codex" ]]; then
    echo "[$(get_timestamp)] Executing codex (no fallback)"
    EXIT_CODE=0
    run_with_timeout "$TASK_TIMEOUT_SECS" "$TASK_TIMEOUT_KILL_SECS" \
        codex exec --skip-git-repo-check --full-auto "$PROMPT" --json > "$LOG_FILE" 2>&1 \
        || EXIT_CODE=$?
    if [[ $EXIT_CODE -eq 124 ]]; then
        echo "[$(get_timestamp)] TIMEOUT after ${TASK_TIMEOUT_SECS}s (executor=codex)" | tee -a "$LOG_FILE"
    fi

# === OpenCode free model rotation (primary path) ===
elif [[ "$API_MODE" == "opencode" ]]; then
    CURRENT_MODE="opencode"

    # === Full rotation: try ALL models, shuffle starting point per task ===
    # 5 free models, each task starts at a different offset to spread load
    TASK_HASH=$(echo "$TASK_ID" | portable_md5 2>/dev/null | cut -c1-2 || echo "00")
    START_IDX=$(( 16#${TASK_HASH} % ${#MODEL_POOL[@]} ))

    ORDERED_MODELS=()
    for (( i=0; i<${#MODEL_POOL[@]}; i++ )); do
        IDX=$(( (START_IDX + i) % ${#MODEL_POOL[@]} ))
        ORDERED_MODELS+=("${MODEL_POOL[$IDX]}")
    done

    echo "[$(get_timestamp)] Full rotation (start=$START_IDX): ${ORDERED_MODELS[*]}"

    FAILED_MODELS=()

    # Random startup jitter: 0-30s delay to spread API requests across time
    JITTER_SECS=$(( RANDOM % 30 ))
    echo "[$(get_timestamp)] Startup jitter: waiting ${JITTER_SECS}s to spread load"
    sleep "$JITTER_SECS"

    for OC_MODEL in "${ORDERED_MODELS[@]}"; do
        ATTEMPT=$((ATTEMPT + 1))
        OC_MODEL=$(echo "$OC_MODEL" | tr -d ' ')

        # --- Pre-flight DISABLED ---
        # Preflight was consuming rate limit (96 tasks × 5 models = 480 API calls just for health check)
        # Now we skip preflight and let the actual run fail-fast instead
        # if ! preflight_check "$OC_MODEL"; then
        #     echo "[$(get_timestamp)] Skipping $OC_MODEL (preflight failed)" | tee -a "$LOG_FILE"
        #     FAILED_MODELS+=("$OC_MODEL:preflight")
        #     continue
        # fi

        # --- Execute ---
        echo "[$(get_timestamp)] Attempt $ATTEMPT/${#ORDERED_MODELS[@]}: opencode model=$OC_MODEL"

        EXIT_CODE=0
        run_with_stall_detection "$MODEL_TIMEOUT_SECS" "$STALL_TIMEOUT_SECS" "$LOG_FILE" \
            ~/.opencode/bin/opencode run -m "$OC_MODEL" --dir "$WORKING_DIR" "$PROMPT" \
            || EXIT_CODE=$?  # Capture exit code without triggering set -e

        # --- Success check ---
        if [[ $EXIT_CODE -eq 0 ]]; then
            # Verify model actually produced output (not empty success)
            if is_empty_response; then
                echo "[$(get_timestamp)] EMPTY RESPONSE from $OC_MODEL (0 useful bytes)" | tee -a "$LOG_FILE"
                FAILED_MODELS+=("$OC_MODEL:empty")
                EXIT_CODE=1
            elif is_rate_limit_error; then
                echo "[$(get_timestamp)] RATE LIMIT in output from $OC_MODEL" | tee -a "$LOG_FILE"
                FAILED_MODELS+=("$OC_MODEL:ratelimit")
                EXIT_CODE=1
            else
                echo "[$(get_timestamp)] SUCCESS with model=$OC_MODEL (attempt $ATTEMPT)"
                SUCCEEDED_MODEL="$OC_MODEL"
                CURRENT_MODE="opencode:$OC_MODEL"
                break
            fi
        fi

        # --- Failure classification ---
        if [[ $EXIT_CODE -eq 124 ]]; then
            echo "[$(get_timestamp)] TIMEOUT after ${MODEL_TIMEOUT_SECS}s on $OC_MODEL" | tee -a "$LOG_FILE"
            FAILED_MODELS+=("$OC_MODEL:timeout")
        elif [[ $EXIT_CODE -eq 125 ]]; then
            echo "[$(get_timestamp)] STALL on $OC_MODEL (no output for ${STALL_TIMEOUT_SECS}s)" | tee -a "$LOG_FILE"
            FAILED_MODELS+=("$OC_MODEL:stall")
        elif [[ $EXIT_CODE -ne 0 ]]; then
            echo "[$(get_timestamp)] FAILED on $OC_MODEL (exit=$EXIT_CODE)" | tee -a "$LOG_FILE"
            FAILED_MODELS+=("$OC_MODEL:exit$EXIT_CODE")
        fi

        # Wait before rotating: 10-20s random delay to avoid thundering herd
        if [[ $ATTEMPT -lt ${#ORDERED_MODELS[@]} ]]; then
            ROTATE_WAIT=$(( 10 + RANDOM % 10 ))
            echo "[$(get_timestamp)] Rotating to next model (wait ${ROTATE_WAIT}s)... [failed: ${FAILED_MODELS[*]}]" | tee -a "$LOG_FILE"
            sleep "$ROTATE_WAIT"
        fi
    done

    # --- Escalation chain: free failed → paid MiniMax API → paid GLM API → Codex ---
    if [[ $EXIT_CODE -ne 0 ]]; then
        echo "[$(get_timestamp)] ALL FREE MODELS FAILED: ${FAILED_MODELS[*]}" | tee -a "$LOG_FILE"

        # Paid fallback chain (ordered by cost: cheapest first)
        PAID_CHAIN=()

        # 1. MiniMax API (via opencode with MINIMAX_API_KEY env var)
        if [[ -n "${MINIMAX_API_KEY:-}" ]]; then
            PAID_CHAIN+=("minimax")
        fi

        # 2. GLM API (paid, via z.ai proxy)
        if [[ -f ~/.oyster-keys/zai-glm.env ]]; then
            PAID_CHAIN+=("zai")
        fi

        # 3. Codex (paid, most expensive, most reliable)
        if command -v codex &>/dev/null; then
            PAID_CHAIN+=("codex")
        fi

        for PAID_MODE in "${PAID_CHAIN[@]}"; do
            ATTEMPT=$((ATTEMPT + 1))
            echo "[$(get_timestamp)] Escalating to PAID: $PAID_MODE (attempt $ATTEMPT)" | tee -a "$LOG_FILE"

            if [[ "$PAID_MODE" == "minimax" ]]; then
                echo "[$(get_timestamp)] MiniMax M2.5 paid via opencode" | tee -a "$LOG_FILE"
                EXIT_CODE=0
                run_with_stall_detection "$MODEL_TIMEOUT_SECS" "$STALL_TIMEOUT_SECS" "$LOG_FILE" \
                    ~/.opencode/bin/opencode run -m "minimax/MiniMax-M2.5" --dir "$WORKING_DIR" "$PROMPT" \
                    || EXIT_CODE=$?

            elif [[ "$PAID_MODE" == "zai" ]]; then
                source ~/.oyster-keys/zai-glm.env 2>/dev/null
                export ANTHROPIC_AUTH_TOKEN="${ZAI_API_KEY:-}"
                export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"

                EXIT_CODE=0
                run_with_stall_detection "$MODEL_TIMEOUT_SECS" "$STALL_TIMEOUT_SECS" "$LOG_FILE" \
                    claude -p --dangerously-skip-permissions "$PROMPT" \
                    || EXIT_CODE=$?

            elif [[ "$PAID_MODE" == "codex" ]]; then
                unset ANTHROPIC_AUTH_TOKEN 2>/dev/null || true
                unset ANTHROPIC_BASE_URL 2>/dev/null || true

                EXIT_CODE=0
                run_with_stall_detection "$MODEL_TIMEOUT_SECS" "$STALL_TIMEOUT_SECS" "$LOG_FILE" \
                    codex exec --skip-git-repo-check --full-auto "$PROMPT" --json \
                    || EXIT_CODE=$?
            fi

            if [[ $EXIT_CODE -eq 0 ]] && ! is_empty_response && ! is_rate_limit_error; then
                echo "[$(get_timestamp)] SUCCESS with paid=$PAID_MODE (attempt $ATTEMPT)"
                SUCCEEDED_MODEL="paid:$PAID_MODE"
                break
            else
                echo "[$(get_timestamp)] Paid $PAID_MODE also failed (exit=$EXIT_CODE)" | tee -a "$LOG_FILE"
                FAILED_MODELS+=("paid:$PAID_MODE:exit$EXIT_CODE")
                sleep 5
            fi
        done
    fi

    # Log final summary
    if [[ $EXIT_CODE -ne 0 ]]; then
        echo "[$(get_timestamp)] ALL MODELS EXHAUSTED after $ATTEMPT attempts: ${FAILED_MODELS[*]}" | tee -a "$LOG_FILE"
    fi

# === Claude direct / MiniMax API mode (legacy) ===
else
    CURRENT_MODE="$API_MODE"
    MAX_RETRIES=2
    while true; do
        ATTEMPT=$((ATTEMPT + 1))

        if [[ "$CURRENT_MODE" == "minimax" ]]; then
            if [[ -f ~/.oyster-keys/minimax.env ]]; then
                source ~/.oyster-keys/minimax.env 2>/dev/null
                MMKEY="${MINIMAX_API_KEY:-}"
            else
                MMKEY=$(cat ~/.oyster-keys/minimax-key.txt 2>/dev/null | head -1 | tr -d '\n')
            fi
            [[ -n "$MMKEY" ]] && export ANTHROPIC_AUTH_TOKEN="${MMKEY}"
            export ANTHROPIC_BASE_URL="https://api.minimax.io/anthropic"
        elif [[ "$CURRENT_MODE" == "zai" ]]; then
            [[ -z "${ZAI_API_KEY:-}" ]] && source ~/.oyster-keys/zai-glm.env 2>/dev/null
            export ANTHROPIC_AUTH_TOKEN="${ZAI_API_KEY:-}"
            export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
        elif [[ "$CURRENT_MODE" == "direct" ]]; then
            unset ANTHROPIC_AUTH_TOKEN 2>/dev/null || true
            unset ANTHROPIC_BASE_URL 2>/dev/null || true
        fi

        echo "[$(get_timestamp)] Attempt $ATTEMPT: claude api_mode=$CURRENT_MODE"
        EXIT_CODE=0
        run_with_stall_detection "$MODEL_TIMEOUT_SECS" "$STALL_TIMEOUT_SECS" "$LOG_FILE" \
            claude -p --dangerously-skip-permissions "$PROMPT" \
            || EXIT_CODE=$?

        if [[ $EXIT_CODE -eq 124 ]] || [[ $EXIT_CODE -eq 125 ]]; then
            echo "[$(get_timestamp)] TIMEOUT/STALL on $CURRENT_MODE" | tee -a "$LOG_FILE"
            break
        fi

        if [[ $EXIT_CODE -eq 0 ]] && ! is_rate_limit_error && ! is_empty_response; then
            break
        fi

        if [[ $ATTEMPT -ge $MAX_RETRIES ]]; then
            echo "[$(get_timestamp)] FALLBACK EXHAUSTED after $ATTEMPT attempts" | tee -a "$LOG_FILE"
            break
        fi
        echo "[$(get_timestamp)] ERROR on $CURRENT_MODE (exit=$EXIT_CODE), retrying (wait 10s)" | tee -a "$LOG_FILE"
        sleep 10
    done
fi
# DO NOT re-enable set -e here — grep/sed in STRUCTURED RESULT parsing
# will fail with pipefail when patterns don't match, killing the script
# before git push. This was the root cause of code never being pushed.
# (2026-02-21 fix: Opus)

LLM_EXIT_CODE=$EXIT_CODE
ERROR_MSG=""
if [[ $LLM_EXIT_CODE -eq 124 ]]; then
    ERROR_MSG="LLM timeout after ${TASK_TIMEOUT_SECS}s"
elif [[ $LLM_EXIT_CODE -ne 0 ]]; then
    ERROR_MSG="LLM failed (exit=$LLM_EXIT_CODE)"
fi

# ╔══════════════════════════════════════════════════════════════╗
# ║  PROGRESS NARRATIVE — 保存进度日志 (2026-02-20)              ║
# ║  无论成功失败，都记录 agent 做了什么，给下次重试用            ║
# ╚══════════════════════════════════════════════════════════════╝
{
    echo "════════════════════════════════════════"
    echo "时间: $(get_timestamp)"
    echo "节点: $NODE"
    echo "尝试: $ATTEMPT"
    echo "LLM退出码: $LLM_EXIT_CODE"
    echo "API模式: $CURRENT_MODE"
    if [[ -n "$ERROR_MSG" ]]; then
        echo "错误: $ERROR_MSG"
    fi
    # 提取 agent 输出的最后 30 行有意义内容（跳过工具调用元数据）
    if [[ -f "$LOG_FILE" ]]; then
        echo "--- agent 输出摘要 ---"
        grep -v '^\[Tool\|^{"\|^$' "$LOG_FILE" 2>/dev/null | tail -30
        echo "--- 摘要结束 ---"
    fi
    echo "════════════════════════════════════════"
} >> "$PROGRESS_FILE"

# ╔══════════════════════════════════════════════════════════════╗
# ║  STRUCTURED RESULT — 解析 agent 的结构化结果块               ║
# ║  格式: ---TASK RESULT--- ... ---END TASK RESULT---           ║
# ╚══════════════════════════════════════════════════════════════╝
TASK_RESULT_FILE="$TASK_DIR/task_result.json"
if [[ -f "$LOG_FILE" ]]; then
    # 提取 ---TASK RESULT--- 到 ---END TASK RESULT--- 之间的内容
    RESULT_BLOCK=$(sed -n '/---TASK RESULT---/,/---END TASK RESULT---/p' "$LOG_FILE" 2>/dev/null | head -20)
    if [[ -n "$RESULT_BLOCK" ]]; then
        echo "[$(get_timestamp)] Found structured TASK RESULT block"
        # 解析 key: value 行 (|| true prevents pipefail from killing script)
        RESULT_STATUS=$(echo "$RESULT_BLOCK" | grep '^status:' | head -1 | sed 's/^status: *//' || true)
        RESULT_SUMMARY=$(echo "$RESULT_BLOCK" | grep '^summary:' | head -1 | sed 's/^summary: *//' || true)
        RESULT_FILES=$(echo "$RESULT_BLOCK" | grep '^files_modified:' | head -1 | sed 's/^files_modified: *//' || true)
        RESULT_TESTS=$(echo "$RESULT_BLOCK" | grep '^tests_passed:' | head -1 | sed 's/^tests_passed: *//' || true)
        RESULT_ISSUES=$(echo "$RESULT_BLOCK" | grep '^issues:' | head -1 | sed 's/^issues: *//' || true)

        RESULT_SUMMARY_ESC=$(json_escape "${RESULT_SUMMARY:-}")
        RESULT_FILES_ESC=$(json_escape "${RESULT_FILES:-}")
        RESULT_ISSUES_ESC=$(json_escape "${RESULT_ISSUES:-}")

        cat > "$TASK_RESULT_FILE" <<RESULTEOF
{"agent_status":"${RESULT_STATUS:-unknown}","summary":"${RESULT_SUMMARY_ESC}","files_modified":"${RESULT_FILES_ESC}","tests_passed":"${RESULT_TESTS:-unknown}","issues":"${RESULT_ISSUES_ESC}"}
RESULTEOF
        echo "[$(get_timestamp)] TASK RESULT: status=${RESULT_STATUS:-unknown} tests=${RESULT_TESTS:-unknown}"
    else
        echo "[$(get_timestamp)] No structured TASK RESULT block found in agent output"
    fi
fi

# === Git commit/push ===
if [[ "$GIT_MODE" == true ]] && [[ $LLM_EXIT_CODE -eq 0 ]]; then
    cd "$REPO_DIR"
    GIT_STATUS_LOG="$TASK_DIR/git_changes.log"
    git status --porcelain > "$GIT_STATUS_LOG"
    FILES_CHANGED=$(grep -c . "$GIT_STATUS_LOG" 2>/dev/null || echo "0")
    GIT_PUSH_LOG="$TASK_DIR/git_push.log"

    if [[ -s "$GIT_STATUS_LOG" ]]; then
        # CRITICAL FIX: restore files deleted by init.sh before staging
        # init.sh strips web-ui/ etc for LLM context reduction, but git add -A
        # would stage those deletions, poisoning the branch with 100K+ line removals
        git restore -- web-ui/ desktop/ demo/ schemas/ runner/ repo/ docs/ tests/ templates/ .github/ 2>/dev/null || true
        git checkout -- web-ui/ desktop/ demo/ schemas/ runner/ repo/ docs/ tests/ templates/ .github/ 2>/dev/null || true
        git add -A
        git commit -m "task/${TASK_ID}: auto-commit from $(hostname)"
        git push origin "$BRANCH" 2>"$GIT_PUSH_LOG"
        GIT_PUSH_OK=$?
    else
        echo "No changes to commit" > "$GIT_PUSH_LOG"
        GIT_PUSH_OK=0
        FILES_CHANGED=0
    fi
fi

# ╔══════════════════════════════════════════════════════════════╗
# ║  QUALITY GATES — 假完成在这里死  (2026-02-16 v2)           ║
# ║  Gate 1: 最小时间 (< 45s = 假完成)                         ║
# ║  Gate 2: 实际代码变更 (0 changes = 没干活)                  ║
# ║  Gate 3: TODO/FIXME 检查 (有 = 糊弄)                       ║
# ║  Gate 4: 跑测试 (git + SCP 都跑)                           ║
# ╚══════════════════════════════════════════════════════════════╝

# Determine scan directory: works for BOTH git and SCP modes
SCAN_DIR=""
if [[ -d "$REPO_DIR" ]] && [[ "$GIT_MODE" == true ]]; then
    SCAN_DIR="$REPO_DIR"
else
    SCAN_DIR="$WORKING_DIR"
fi

# === GATE 1: Minimum duration (anti-fake-completion) ===
if [[ $LLM_EXIT_CODE -eq 0 ]]; then
    END_EPOCH=$(date +%s)
    # Cross-platform epoch from STARTED_AT (must handle both GNU date and BSD date)
    if date -d "2000-01-01" +%s >/dev/null 2>&1; then
        # GNU date (Linux) — understands ISO8601 directly
        START_EPOCH=$(date -d "$STARTED_AT" +%s 2>/dev/null || echo "$END_EPOCH")
    else
        # BSD date (macOS) — use Python with explicit UTC to avoid local-tz offset
        START_EPOCH=$(python3 -c "
from datetime import datetime, timezone
s = '$STARTED_AT'.replace('+00:00','').rstrip('Z')
dt = datetime.fromisoformat(s).replace(tzinfo=timezone.utc)
print(int(dt.timestamp()))
" 2>/dev/null || echo "$END_EPOCH")
    fi
    DURATION=$((END_EPOCH - START_EPOCH))
    MIN_DURATION="${MIN_TASK_DURATION:-10}"

    if [[ $DURATION -lt $MIN_DURATION ]]; then
        echo "[$(get_timestamp)] GATE 1 FAIL: Too fast (${DURATION}s < ${MIN_DURATION}s)"
        echo "QUALITY_GATE_1: FAILED - too fast (${DURATION}s)" >> "$LOG_FILE"
        EXIT_CODE=1
        ERROR_MSG="Gate 1: too fast (${DURATION}s < ${MIN_DURATION}s)"
    else
        echo "[$(get_timestamp)] GATE 1 PASS: Duration ${DURATION}s"
    fi
fi

# === GATE 2: Actual code changes produced ===
if [[ $LLM_EXIT_CODE -eq 0 ]] && [[ ${EXIT_CODE:-0} -eq 0 ]]; then
    echo "[$(get_timestamp)] === Gate 2: Checking code changes ==="
    CHANGED_FILES=0

    if [[ -d "$SCAN_DIR/.git" ]]; then
        # Check uncommitted + staged + untracked
        CHANGED_FILES=$(cd "$SCAN_DIR" && (git diff --name-only 2>/dev/null; git diff --cached --name-only 2>/dev/null; git ls-files --others --exclude-standard 2>/dev/null) | sort -u | wc -l | tr -d ' ')
        # Also check committed changes (LLM may have already committed)
        if [[ "$GIT_MODE" == true ]] && [[ ${CHANGED_FILES:-0} -eq 0 ]]; then
            # Count files changed in commits made since clone (depth=1 means 1 initial commit)
            GIT_COMMITTED=$(cd "$SCAN_DIR" && git log --oneline --format='' --stat 2>/dev/null | grep -c 'file' ) || GIT_COMMITTED=0
            # Simpler: count new commits beyond the initial clone commit
            GIT_NEW_COMMITS=$(cd "$SCAN_DIR" && git rev-list --count HEAD 2>/dev/null) || GIT_NEW_COMMITS=1
            if [[ ${GIT_NEW_COMMITS:-1} -gt 1 ]]; then
                # There are commits beyond the original — count changed files in those commits
                CHANGED_FILES=$(cd "$SCAN_DIR" && git diff --name-only HEAD~$((GIT_NEW_COMMITS - 1))..HEAD 2>/dev/null | wc -l | tr -d ' ') || CHANGED_FILES=0
                echo "[$(get_timestamp)] Gate 2: found $CHANGED_FILES files in $((GIT_NEW_COMMITS - 1)) new commit(s)"
            fi
        fi
    fi

    OUTPUT_FILES=0
    if [[ -d "$OUTPUT_DIR" ]]; then
        OUTPUT_FILES=$(find "$OUTPUT_DIR" -type f \( -name "*.py" -o -name "*.ts" -o -name "*.js" -o -name "*.tsx" -o -name "*.jsx" -o -name "*.md" -o -name "*.sh" \) 2>/dev/null | wc -l | tr -d ' ')
    fi

    # Check project directory for modifications (SCP/OpenCode mode)
    PROJECT_CHANGES=0
    # Method 1: MD5 comparison (catches modifications to existing files)
    if [[ -f "/tmp/pre-md5-${TASK_ID}.txt" ]]; then
        find "$WORKING_DIR" -type f \( -name "*.py" -o -name "*.ts" -o -name "*.js" -o -name "*.tsx" -o -name "*.jsx" -o -name "*.json" \) ! -path "*/node_modules/*" ! -path "*/.git/*" -exec bash -c 'command -v md5sum >/dev/null && md5sum "$1" || md5 -r "$1"' _ {} \; 2>/dev/null | sort > "/tmp/post-md5-${TASK_ID}.txt" 2>/dev/null || true
        PROJECT_CHANGES=$(diff "/tmp/pre-md5-${TASK_ID}.txt" "/tmp/post-md5-${TASK_ID}.txt" 2>/dev/null | grep -c '^[<>]') || PROJECT_CHANGES=0
        rm -f "/tmp/pre-md5-${TASK_ID}.txt" "/tmp/post-md5-${TASK_ID}.txt" "/tmp/pre-snapshot-${TASK_ID}.txt" 2>/dev/null
    fi
    # Method 2: Check for files newer than status.json (catches newly created files)
    if [[ $PROJECT_CHANGES -eq 0 ]] && [[ -f "$STATUS_FILE" ]]; then
        NEW_FILES=$(find "$WORKING_DIR" -type f \( -name "*.py" -o -name "*.ts" -o -name "*.js" -o -name "*.tsx" -o -name "*.jsx" -o -name "*.json" -o -name "*.sh" \) -newer "$STATUS_FILE" ! -path "*/tasks/*" ! -path "*/node_modules/*" ! -path "*/.git/*" 2>/dev/null | wc -l | tr -d ' ')
        if [[ ${NEW_FILES:-0} -gt 0 ]]; then
            echo "[$(get_timestamp)] Gate 2: Found $NEW_FILES new files via timestamp check"
            PROJECT_CHANGES=$NEW_FILES
        fi
    fi

    # Rescue check: opencode sometimes writes to nested relative paths (e.g., home/user/...)
    # Move those files to the correct location
    NESTED_HOME="$WORKING_DIR/home"
    if [[ -d "$NESTED_HOME" ]] && [[ $OUTPUT_FILES -eq 0 ]] && [[ $CHANGED_FILES -eq 0 ]] && [[ $PROJECT_CHANGES -eq 0 ]]; then
        echo "[$(get_timestamp)] RESCUE: Found nested home/ directory, relocating files..."
        # Find the deepest project-named directory and copy files back
        NESTED_PROJECT=$(find "$NESTED_HOME" -type d -name "$PROJECT" 2>/dev/null | head -1)
        if [[ -n "$NESTED_PROJECT" ]]; then
            cp -rn "$NESTED_PROJECT"/* "$WORKING_DIR/" 2>/dev/null || true
            rm -rf "$NESTED_HOME" 2>/dev/null || true
            echo "[$(get_timestamp)] RESCUE: Relocated files from $NESTED_PROJECT to $WORKING_DIR"
            # Re-check for changes
            if [[ -f "/tmp/post-md5-${TASK_ID}.txt" ]]; then
                find "$WORKING_DIR" -type f \( -name "*.py" -o -name "*.ts" -o -name "*.js" -o -name "*.tsx" -o -name "*.jsx" \) -exec bash -c 'command -v md5sum >/dev/null && md5sum "$1" || md5 -r "$1"' _ {} \; 2>/dev/null | sort > "/tmp/post-md5-${TASK_ID}-rescue.txt" 2>/dev/null || true
                PROJECT_CHANGES=$(diff "/tmp/pre-md5-${TASK_ID}.txt" "/tmp/post-md5-${TASK_ID}-rescue.txt" 2>/dev/null | grep -c '^[<>]') || PROJECT_CHANGES=0
            else
                PROJECT_CHANGES=$(find "$WORKING_DIR" -type f \( -name "*.py" -o -name "*.ts" -o -name "*.js" \) -newer "$STATUS_FILE" 2>/dev/null | wc -l | tr -d ' ')
            fi
        fi
    fi

    TOTAL_CHANGES=$((CHANGED_FILES + OUTPUT_FILES + PROJECT_CHANGES))

    if [[ $TOTAL_CHANGES -eq 0 ]]; then
        # STRICT: No changes = FAIL. LLM must produce code.
        # Previous "bypass" let empty outputs through if target files pre-existed.
        echo "[$(get_timestamp)] GATE 2 FAIL: No code changes (git=$CHANGED_FILES output=$OUTPUT_FILES project=$PROJECT_CHANGES)"
        echo "QUALITY_GATE_2: FAILED - no changes" >> "$LOG_FILE"
        EXIT_CODE=1
        ERROR_MSG="Gate 2: no code changes produced"
    else
        echo "[$(get_timestamp)] GATE 2 PASS: git=$CHANGED_FILES output=$OUTPUT_FILES project=$PROJECT_CHANGES"
    fi
fi

# === GATE 3: TODO/FIXME/placeholder check — ONLY in changed files ===
# Previous version scanned entire $SCAN_DIR which caught pre-existing TODOs.
# Now we only check files touched during this task run.
if [[ $LLM_EXIT_CODE -eq 0 ]] && [[ ${EXIT_CODE:-0} -eq 0 ]]; then
    echo "[$(get_timestamp)] === Gate 3: TODO/FIXME check (changed files only) ==="
    TODO_COUNT=0

    # Collect changed files (git mode: git diff; SCP mode: find newer than STATUS_FILE)
    CHANGED_FILE_LIST="/tmp/gate3-changed-${TASK_ID}.txt"
    : > "$CHANGED_FILE_LIST"

    if [[ -d "$SCAN_DIR/.git" ]]; then
        # Git mode: only check files changed by the LLM
        (cd "$SCAN_DIR" && git diff --name-only 2>/dev/null; git diff --cached --name-only 2>/dev/null; git ls-files --others --exclude-standard 2>/dev/null) | sort -u | while read -r f; do
            echo "$SCAN_DIR/$f"
        done >> "$CHANGED_FILE_LIST" 2>/dev/null
    else
        # SCP mode: files newer than STATUS_FILE
        find "$SCAN_DIR" -type f \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) -newer "$STATUS_FILE" 2>/dev/null >> "$CHANGED_FILE_LIST" || true
    fi

    if [[ -d "$OUTPUT_DIR" ]]; then
        find "$OUTPUT_DIR" -type f \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) 2>/dev/null >> "$CHANGED_FILE_LIST" || true
    fi

    if [[ -s "$CHANGED_FILE_LIST" ]]; then
        TODO_COUNT=$(grep -l 'TODO\|FIXME\|placeholder\|XXX' $(cat "$CHANGED_FILE_LIST") 2>/dev/null | wc -l | tr -d ' ') || TODO_COUNT=0
    fi
    rm -f "$CHANGED_FILE_LIST" 2>/dev/null

    if [[ "$TODO_COUNT" -gt 0 ]]; then
        echo "[$(get_timestamp)] GATE 3 FAIL: $TODO_COUNT changed files with TODO/FIXME"
        echo "QUALITY_GATE_3: FAILED - $TODO_COUNT files" >> "$LOG_FILE"
        EXIT_CODE=1
        ERROR_MSG="Gate 3: $TODO_COUNT changed files contain TODO/FIXME"
    else
        echo "[$(get_timestamp)] GATE 3 PASS: clean"
    fi
fi

# === GATE 4: Run tests (works for BOTH git and SCP modes) ===
if [[ $LLM_EXIT_CODE -eq 0 ]] && [[ ${EXIT_CODE:-0} -eq 0 ]]; then
    echo "[$(get_timestamp)] === Gate 4: Running tests ==="
    TEST_PASSED=true
    VERIFY_EXIT_CODE=0
    TEST_OUTPUT=""

    if [[ -d "$SCAN_DIR" ]]; then
        cd "$SCAN_DIR"

        # Python/pytest
        if [[ -f "$SCAN_DIR/requirements.txt" ]] || [[ -f "$SCAN_DIR/pyproject.toml" ]] || [[ -f "$SCAN_DIR/setup.py" ]]; then
            if [[ -f "$SCAN_DIR/.venv/bin/activate" ]]; then
                source "$SCAN_DIR/.venv/bin/activate"
            fi
            if command -v pytest &> /dev/null; then
                echo "[$(get_timestamp)] Running: pytest"
                TEST_OUTPUT=$(run_with_timeout "$VERIFY_TIMEOUT_SECS" "$VERIFY_TIMEOUT_KILL_SECS" pytest -v --tb=short 2>&1)
                TEST_CODE=$?
                [[ $TEST_CODE -ne 0 ]] && TEST_PASSED=false
                [[ $VERIFY_EXIT_CODE -eq 0 && $TEST_CODE -ne 0 ]] && VERIFY_EXIT_CODE=$TEST_CODE
                echo "$TEST_OUTPUT" >> "$LOG_FILE"
            fi
        fi

        # Node.js
        if [[ -f "$SCAN_DIR/package.json" ]]; then
            if grep -q '"test"' "$SCAN_DIR/package.json"; then
                echo "[$(get_timestamp)] Running: npm test"
                TEST_OUTPUT=$(run_with_timeout "$VERIFY_TIMEOUT_SECS" "$VERIFY_TIMEOUT_KILL_SECS" npm test 2>&1)
                TEST_CODE=$?
                [[ $TEST_CODE -ne 0 ]] && TEST_PASSED=false
                [[ $VERIFY_EXIT_CODE -eq 0 && $TEST_CODE -ne 0 ]] && VERIFY_EXIT_CODE=$TEST_CODE
                echo "$TEST_OUTPUT" >> "$LOG_FILE"
            fi
        fi

        # Makefile
        if [[ -f "$SCAN_DIR/Makefile" ]] && grep -q 'test:' "$SCAN_DIR/Makefile"; then
            echo "[$(get_timestamp)] Running: make test"
            TEST_OUTPUT=$(run_with_timeout "$VERIFY_TIMEOUT_SECS" "$VERIFY_TIMEOUT_KILL_SECS" make test 2>&1)
            TEST_CODE=$?
            [[ $TEST_CODE -ne 0 ]] && TEST_PASSED=false
            [[ $VERIFY_EXIT_CODE -eq 0 && $TEST_CODE -ne 0 ]] && VERIFY_EXIT_CODE=$TEST_CODE
            echo "$TEST_OUTPUT" >> "$LOG_FILE"
        fi

        # run.sh
        if [[ -x "$SCAN_DIR/run.sh" ]] && grep -q 'test' "$SCAN_DIR/run.sh"; then
            echo "[$(get_timestamp)] Running: ./run.sh test"
            TEST_OUTPUT=$(run_with_timeout "$VERIFY_TIMEOUT_SECS" "$VERIFY_TIMEOUT_KILL_SECS" bash ./run.sh test 2>&1)
            TEST_CODE=$?
            [[ $TEST_CODE -ne 0 ]] && TEST_PASSED=false
            [[ $VERIFY_EXIT_CODE -eq 0 && $TEST_CODE -ne 0 ]] && VERIFY_EXIT_CODE=$TEST_CODE
            echo "$TEST_OUTPUT" >> "$LOG_FILE"
        fi
    fi

    if [[ "$TEST_PASSED" == "false" ]]; then
        echo "[$(get_timestamp)] GATE 4 FAIL: tests failed"
        echo "QUALITY_GATE_4: FAILED" >> "$LOG_FILE"
        if [[ $VERIFY_EXIT_CODE -eq 124 ]]; then
            EXIT_CODE=124
            ERROR_MSG="Gate 4: test timeout (${VERIFY_TIMEOUT_SECS}s)"
        else
            EXIT_CODE=1
            ERROR_MSG="Gate 4: tests failed"
        fi
    else
        echo "[$(get_timestamp)] GATE 4 PASS: all tests green"
        echo "QUALITY_GATE_4: PASSED" >> "$LOG_FILE"
        EXIT_CODE=0
    fi
else
    EXIT_CODE=${EXIT_CODE:-$LLM_EXIT_CODE}
fi

# ╔══════════════════════════════════════════════════════════════╗
# ║  ARTIFACT HASH — 防假完成的终极武器 (v3 self-healing)       ║
# ║  git diff → sha256 → 写入 status.json                      ║
# ║  没有 hash 的 completed = 假完成                            ║
# ╚══════════════════════════════════════════════════════════════╝
ARTIFACT_HASH=""
LOC_ADDED=0
LOC_REMOVED=0
ARTIFACT_FILES_CHANGED=0
PATCH_FILE="$TASK_DIR/artifact.patch"

if [[ $EXIT_CODE -eq 0 ]]; then
    echo "[$(get_timestamp)] === Generating artifact hash ==="

    if [[ -d "$SCAN_DIR/.git" ]]; then
        # Git mode: diff against HEAD~1 (our commit) or initial state
        cd "$SCAN_DIR"
        git diff HEAD~1 HEAD > "$PATCH_FILE" 2>/dev/null || \
            git diff --cached > "$PATCH_FILE" 2>/dev/null || \
            git diff > "$PATCH_FILE" 2>/dev/null || true

        if [[ -s "$PATCH_FILE" ]]; then
            ARTIFACT_HASH=$(portable_sha256 "$PATCH_FILE" | cut -d' ' -f1)
            LOC_ADDED=$(grep -c '^+[^+]' "$PATCH_FILE" 2>/dev/null || echo 0)
            LOC_REMOVED=$(grep -c '^-[^-]' "$PATCH_FILE" 2>/dev/null || echo 0)
            ARTIFACT_FILES_CHANGED=$(grep -c '^diff --git' "$PATCH_FILE" 2>/dev/null || echo 0)
        fi
    else
        # SCP mode: diff against pre-snapshot using md5 comparison
        if [[ -f "/tmp/post-md5-${TASK_ID}.txt" ]]; then
            diff "/tmp/pre-md5-${TASK_ID}.txt" "/tmp/post-md5-${TASK_ID}.txt" 2>/dev/null > "$PATCH_FILE" || true
        fi

        # Also find all files newer than STATUS_FILE as our "patch"
        if [[ ! -s "$PATCH_FILE" ]]; then
            find "$WORKING_DIR" -type f \( -name "*.py" -o -name "*.ts" -o -name "*.js" -o -name "*.tsx" -o -name "*.jsx" -o -name "*.sh" \) -newer "$STATUS_FILE" 2>/dev/null | while read -r f; do
                echo "=== $f ==="
                cat "$f" 2>/dev/null
            done > "$PATCH_FILE" 2>/dev/null || true
        fi

        if [[ -s "$PATCH_FILE" ]]; then
            ARTIFACT_HASH=$(portable_sha256 "$PATCH_FILE" | cut -d' ' -f1)
            ARTIFACT_FILES_CHANGED=$(grep -c '^=== ' "$PATCH_FILE" 2>/dev/null || echo 0)
            LOC_ADDED=$(wc -l < "$PATCH_FILE" 2>/dev/null || echo 0)
        fi
    fi

    if [[ -n "$ARTIFACT_HASH" ]]; then
        echo "[$(get_timestamp)] ARTIFACT: hash=$ARTIFACT_HASH files=$ARTIFACT_FILES_CHANGED +$LOC_ADDED -$LOC_REMOVED"
    else
        echo "[$(get_timestamp)] ARTIFACT: WARNING no hash generated (no changes detected)"
    fi
fi

# === Write final status ===
COMPLETED_AT=$(get_timestamp)
FINAL_STATUS="completed"
[[ $EXIT_CODE -ne 0 ]] && FINAL_STATUS="failed"

ERROR_ESCAPED=$(json_escape "$ERROR_MSG")

if [[ "$GIT_MODE" == true ]]; then
    GIT_PUSH_OK_BOOL="false"
    [[ ${GIT_PUSH_OK:-1} -eq 0 ]] && GIT_PUSH_OK_BOOL="true"
    cat > "$STATUS_FILE" <<EOF
{"status":"$FINAL_STATUS","pid":$$,"started_at":"$STARTED_AT","completed_at":"$COMPLETED_AT","node":"$NODE","exit_code":$EXIT_CODE,"git_mode":true,"git_branch":"$BRANCH","git_push_ok":$GIT_PUSH_OK_BOOL,"files_changed":${FILES_CHANGED:-0},"api_mode":"$CURRENT_MODE","attempts":$ATTEMPT,"error":"$ERROR_ESCAPED","artifact_hash":"$ARTIFACT_HASH","loc_added":$LOC_ADDED,"loc_removed":$LOC_REMOVED,"artifact_files_changed":$ARTIFACT_FILES_CHANGED}
EOF
else
    cat > "$STATUS_FILE" <<EOF
{"status":"$FINAL_STATUS","pid":$$,"started_at":"$STARTED_AT","completed_at":"$COMPLETED_AT","node":"$NODE","exit_code":$EXIT_CODE,"git_mode":false,"api_mode":"$CURRENT_MODE","attempts":$ATTEMPT,"error":"$ERROR_ESCAPED","artifact_hash":"$ARTIFACT_HASH","loc_added":$LOC_ADDED,"loc_removed":$LOC_REMOVED,"artifact_files_changed":$ARTIFACT_FILES_CHANGED}
EOF
fi

echo "[$COMPLETED_AT] Task $TASK_ID $FINAL_STATUS (exit=$EXIT_CODE, mode=$CURRENT_MODE, attempts=$ATTEMPT, artifact=$ARTIFACT_HASH)"
exit $EXIT_CODE
