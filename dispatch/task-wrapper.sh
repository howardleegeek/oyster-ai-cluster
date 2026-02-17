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
    # SCP mode: Use project root, not output dir
    # This fixes the "external_directory" permission issue
    GIT_MODE=false
    WORKING_DIR="$HOME/dispatch/$PROJECT"
fi

mkdir -p "$OUTPUT_DIR"

get_timestamp() { date -u +'%Y-%m-%dT%H:%M:%S+00:00'; }

STARTED_AT=$(get_timestamp)
NODE=$(hostname)

cat > "$STATUS_FILE" <<EOF
{"status":"running","pid":$$,"started_at":"$STARTED_AT","node":"$NODE","git_mode":$GIT_MODE}
EOF

echo "[$STARTED_AT] Starting task $TASK_ID on $NODE (PID: $$)"

# Heartbeat
( while true; do get_timestamp > "$HEARTBEAT_FILE"; sleep 10; done ) &
HB_PID=$!
cleanup() { kill "$HB_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

cd "$WORKING_DIR"

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
    echo "$s"
}

# === Rate limit fallback logic ===

is_rate_limit_error() {
    grep -qiE '429|rate_limit|overloaded|quota|too many requests|capacity|permission requested|external_directory|authentication|auth token|invalid api|unauthorized' "$LOG_FILE" 2>/dev/null
}

get_fallback_mode() {
    case "$1" in
        minimax) echo "direct" ;;
        direct)  echo "opencode" ;;
        opencode) echo "" ;;
        zai)     echo "minimax" ;;
        *)       echo "" ;;
    esac
}

configure_mode() {
    local mode="$1"
    if [[ "$mode" == "zai" ]]; then
        [[ -z "${ZAI_API_KEY:-}" ]] && source ~/.oyster-keys/zai-glm.env 2>/dev/null
        export ANTHROPIC_AUTH_TOKEN="${ZAI_API_KEY:-}"
        export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
        export API_TIMEOUT_MS="3000000"
    elif [[ "$mode" == "minimax" ]]; then
        # Load from minimax.env first, fallback to minimax-key.txt
        if [[ -f ~/.oyster-keys/minimax.env ]]; then
            source ~/.oyster-keys/minimax.env 2>/dev/null
            MMKEY="${MINIMAX_API_KEY:-}"
        else
            MMKEY=$(cat ~/.oyster-keys/minimax-key.txt 2>/dev/null | head -1 | tr -d '\n')
        fi
        if [[ -n "$MMKEY" ]]; then
            export ANTHROPIC_AUTH_TOKEN="${MMKEY}"
        fi
        export ANTHROPIC_BASE_URL="https://api.minimax.io/anthropic"
        export API_TIMEOUT_MS="3000000"
    elif [[ "$mode" == "direct" ]]; then
        unset ANTHROPIC_AUTH_TOKEN 2>/dev/null || true
        unset ANTHROPIC_BASE_URL 2>/dev/null || true
    fi
}

CURRENT_MODE="$API_MODE"
MAX_RETRIES=2
ATTEMPT=0

set +e
while true; do
    ATTEMPT=$((ATTEMPT + 1))

    # === SPEC STANDARD HEADER ===
    # Load SPEC_STANDARD.md to inject规范 into every task
    SPEC_STANDARD_HEADER=""
    SPEC_STANDARD_PATH="$HOME/dispatch/SPEC_STANDARD.md"
    if [[ -f "$SPEC_STANDARD_PATH" ]]; then
        SPEC_STANDARD_HEADER=$(cat << 'SPECEOF'

════════════════════════════════════════════════════════════════════════════
  OYSTER LABS SPEC EXECUTION STANDARD v2.0
════════════════════════════════════════════════════════════════════════════

你正在执行的任务必须遵循以下规范：

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

【代码质量】
- 函数 < 30 行
- 错误处理具体（不写 except Exception）
- 日志有 context（包含 task_id）

详细规范请参考: ~/dispatch/SPEC_STANDARD.md
════════════════════════════════════════════════════════════════════════════
SPECEOF
)
    fi

    # Extract prompt from spec file (skip YAML front-matter)
    # Use awk to skip content between first two --- markers
    PROMPT=$(awk 'BEGIN{in_body=0} /^---$/{in_body++; next} in_body>=1 && !/^---$/{print}' "$SPEC_FILE" 2>/dev/null | head -500)
    if [[ -z "$PROMPT" ]]; then
        # Fallback: use whole file if no YAML
        PROMPT=$(cat "$SPEC_FILE")
    fi

    # Prepend SPEC STANDARD to prompt
    PROMPT="${SPEC_STANDARD_HEADER}${PROMPT}"

    if [[ "$CURRENT_MODE" == "codex" ]]; then
        echo "[$( get_timestamp)] Executing codex (no fallback)"
        run_with_timeout "$TASK_TIMEOUT_SECS" "$TASK_TIMEOUT_KILL_SECS" \
            codex exec --skip-git-repo-check --full-auto "$PROMPT" --json > "$LOG_FILE" 2>&1
        EXIT_CODE=$?

        if [[ $EXIT_CODE -eq 124 ]]; then
            echo "[$(get_timestamp)] TIMEOUT after ${TASK_TIMEOUT_SECS}s (executor=codex)" | tee -a "$LOG_FILE"
        fi
        break
    fi

    # === OpenCode free MiniMax fallback ===
    if [[ "$CURRENT_MODE" == "opencode" ]]; then
        echo "[$(get_timestamp)] Attempt $ATTEMPT: opencode (free minimax)"
        # Pipe prompt via stdin to opencode run
        run_with_timeout "$TASK_TIMEOUT_SECS" "$TASK_TIMEOUT_KILL_SECS" \
            bash -c "echo \"\$1\" | ~/.opencode/bin/opencode run -m opencode/minimax-m2.5-free" -- "$PROMPT" > "$LOG_FILE" 2>&1
        EXIT_CODE=$?

        if [[ $EXIT_CODE -eq 124 ]]; then
            echo "[$(get_timestamp)] TIMEOUT after ${TASK_TIMEOUT_SECS}s (executor=opencode)" | tee -a "$LOG_FILE"
            break
        fi

        if [[ $EXIT_CODE -eq 0 ]]; then
            break
        fi

        # OpenCode failed - no more fallbacks
        echo "[$(get_timestamp)] OpenCode failed (exit=$EXIT_CODE)" | tee -a "$LOG_FILE"
        break
    fi

    configure_mode "$CURRENT_MODE"
    echo "[$(get_timestamp)] Attempt $ATTEMPT: claude api_mode=$CURRENT_MODE"

    # Use claude CLI with --dangerously-skip-permissions to allow external directory access
    # -p for non-interactive (print mode), --dangerously-skip-permissions to bypass permission checks
    run_with_timeout "$TASK_TIMEOUT_SECS" "$TASK_TIMEOUT_KILL_SECS" \
        claude -p --dangerously-skip-permissions "$PROMPT" > "$LOG_FILE" 2>&1
    EXIT_CODE=$?

    if [[ $EXIT_CODE -eq 124 ]]; then
        echo "[$(get_timestamp)] TIMEOUT after ${TASK_TIMEOUT_SECS}s (api_mode=$CURRENT_MODE)" | tee -a "$LOG_FILE"
        break
    fi

    # Success and no rate limit in output
    if [[ $EXIT_CODE -eq 0 ]] && ! is_rate_limit_error; then
        break
    fi

    # Check if rate limit or API error (including permission denied)
    if is_rate_limit_error; then
        NEXT_MODE=$(get_fallback_mode "$CURRENT_MODE")
        if [[ -z "$NEXT_MODE" ]] || [[ $ATTEMPT -gt $MAX_RETRIES ]]; then
            echo "[$(get_timestamp)] FALLBACK EXHAUSTED after $ATTEMPT attempts" | tee -a "$LOG_FILE"
            break
        fi
        echo "[$(get_timestamp)] API ERROR on $CURRENT_MODE, fallback to $NEXT_MODE (wait 30s)" | tee -a "$LOG_FILE"
        sleep 30
        CURRENT_MODE="$NEXT_MODE"
    elif [[ $EXIT_CODE -ne 0 ]]; then
        # Other errors - try fallback once
        NEXT_MODE=$(get_fallback_mode "$CURRENT_MODE")
        if [[ -n "$NEXT_MODE" ]] && [[ $ATTEMPT -eq 1 ]]; then
            echo "[$(get_timestamp)] ERROR (exit=$EXIT_CODE), trying fallback to $NEXT_MODE (wait 10s)" | tee -a "$LOG_FILE"
            sleep 10
            CURRENT_MODE="$NEXT_MODE"
        else
            echo "[$(get_timestamp)] FAILED (exit=$EXIT_CODE, attempt=$ATTEMPT)" | tee -a "$LOG_FILE"
            break
        fi
    fi
done
set -e

LLM_EXIT_CODE=$EXIT_CODE
ERROR_MSG=""
if [[ $LLM_EXIT_CODE -eq 124 ]]; then
    ERROR_MSG="LLM timeout after ${TASK_TIMEOUT_SECS}s"
elif [[ $LLM_EXIT_CODE -ne 0 ]]; then
    ERROR_MSG="LLM failed (exit=$LLM_EXIT_CODE)"
fi

# === Git commit/push ===
if [[ "$GIT_MODE" == true ]] && [[ $LLM_EXIT_CODE -eq 0 ]]; then
    cd "$REPO_DIR"
    GIT_STATUS_LOG="$TASK_DIR/git_changes.log"
    git status --porcelain > "$GIT_STATUS_LOG"
    FILES_CHANGED=$(grep -c . "$GIT_STATUS_LOG" 2>/dev/null || echo "0")
    GIT_PUSH_LOG="$TASK_DIR/git_push.log"

    if [[ -s "$GIT_STATUS_LOG" ]]; then
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
    # Cross-platform epoch from STARTED_AT
    if date -d "2000-01-01" +%s >/dev/null 2>&1; then
        START_EPOCH=$(date -d "$STARTED_AT" +%s 2>/dev/null || echo "$END_EPOCH")
    else
        START_EPOCH=$(python3 -c "from datetime import datetime; print(int(datetime.fromisoformat('$STARTED_AT'.replace('+00:00','+00:00').rstrip('Z')).timestamp()))" 2>/dev/null || echo "$END_EPOCH")
    fi
    DURATION=$((END_EPOCH - START_EPOCH))
    MIN_DURATION="${MIN_TASK_DURATION:-45}"

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
        CHANGED_FILES=$(cd "$SCAN_DIR" && (git diff --name-only 2>/dev/null; git diff --cached --name-only 2>/dev/null; git ls-files --others --exclude-standard 2>/dev/null) | sort -u | wc -l | tr -d ' ')
    fi

    OUTPUT_FILES=0
    if [[ -d "$OUTPUT_DIR" ]]; then
        OUTPUT_FILES=$(find "$OUTPUT_DIR" -type f \( -name "*.py" -o -name "*.ts" -o -name "*.js" -o -name "*.tsx" -o -name "*.jsx" -o -name "*.md" -o -name "*.sh" \) 2>/dev/null | wc -l | tr -d ' ')
    fi

    TOTAL_CHANGES=$((CHANGED_FILES + OUTPUT_FILES))

    if [[ $TOTAL_CHANGES -eq 0 ]]; then
        echo "[$(get_timestamp)] GATE 2 FAIL: No code changes (git=$CHANGED_FILES output=$OUTPUT_FILES)"
        echo "QUALITY_GATE_2: FAILED - no changes" >> "$LOG_FILE"
        EXIT_CODE=1
        ERROR_MSG="Gate 2: no code changes produced"
    else
        echo "[$(get_timestamp)] GATE 2 PASS: git=$CHANGED_FILES output=$OUTPUT_FILES"
    fi
fi

# === GATE 3: TODO/FIXME/placeholder check (covers git + SCP) ===
if [[ $LLM_EXIT_CODE -eq 0 ]] && [[ ${EXIT_CODE:-0} -eq 0 ]]; then
    echo "[$(get_timestamp)] === Gate 3: TODO/FIXME check ==="
    TODO_COUNT=0

    if [[ -d "$SCAN_DIR" ]]; then
        TODO_COUNT=$(grep -r -l 'TODO\|FIXME\|placeholder\|XXX' "$SCAN_DIR" --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" 2>/dev/null | wc -l | tr -d ' ')
    fi
    if [[ -d "$OUTPUT_DIR" ]]; then
        OUTPUT_TODO=$(grep -r -l 'TODO\|FIXME\|placeholder\|XXX' "$OUTPUT_DIR" --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" 2>/dev/null | wc -l | tr -d ' ')
        TODO_COUNT=$((TODO_COUNT + OUTPUT_TODO))
    fi

    if [[ "$TODO_COUNT" -gt 0 ]]; then
        echo "[$(get_timestamp)] GATE 3 FAIL: $TODO_COUNT files with TODO/FIXME"
        echo "QUALITY_GATE_3: FAILED - $TODO_COUNT files" >> "$LOG_FILE"
        EXIT_CODE=1
        ERROR_MSG="Gate 3: $TODO_COUNT files contain TODO/FIXME"
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

# === Write final status ===
COMPLETED_AT=$(get_timestamp)
FINAL_STATUS="completed"
[[ $EXIT_CODE -ne 0 ]] && FINAL_STATUS="failed"

ERROR_ESCAPED=$(json_escape "$ERROR_MSG")

if [[ "$GIT_MODE" == true ]]; then
    GIT_PUSH_OK_BOOL="true"
    [[ ${GIT_PUSH_OK:-0} -ne 0 ]] && GIT_PUSH_OK_BOOL="false"
    cat > "$STATUS_FILE" <<EOF
{"status":"$FINAL_STATUS","pid":$$,"started_at":"$STARTED_AT","completed_at":"$COMPLETED_AT","node":"$NODE","exit_code":$EXIT_CODE,"git_mode":true,"git_branch":"$BRANCH","git_push_ok":$GIT_PUSH_OK_BOOL,"files_changed":${FILES_CHANGED:-0},"api_mode":"$CURRENT_MODE","attempts":$ATTEMPT,"error":"$ERROR_ESCAPED"}
EOF
else
    cat > "$STATUS_FILE" <<EOF
{"status":"$FINAL_STATUS","pid":$$,"started_at":"$STARTED_AT","completed_at":"$COMPLETED_AT","node":"$NODE","exit_code":$EXIT_CODE,"git_mode":false,"api_mode":"$CURRENT_MODE","attempts":$ATTEMPT,"error":"$ERROR_ESCAPED"}
EOF
fi

echo "[$COMPLETED_AT] Task $TASK_ID $FINAL_STATUS (exit=$EXIT_CODE, mode=$CURRENT_MODE, attempts=$ATTEMPT)"
exit $EXIT_CODE
