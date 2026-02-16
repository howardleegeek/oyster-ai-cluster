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
        direct)  echo "minimax" ;;
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
        MMKEY=$(cat ~/.oyster-keys/minimax-key.txt 2>/dev/null | head -1 | tr -d '\n')
        export ANTHROPIC_AUTH_TOKEN="${MMKEY:-}"
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

    # Extract prompt from spec file (skip YAML front-matter)
    # Use awk to skip content between first two --- markers
    PROMPT=$(awk 'BEGIN{in_body=0} /^---$/{in_body++; next} in_body>=1 && !/^---$/{print}' "$SPEC_FILE" 2>/dev/null | head -500)
    if [[ -z "$PROMPT" ]]; then
        # Fallback: use whole file if no YAML
        PROMPT=$(cat "$SPEC_FILE")
    fi

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

# === Best Practice: Check for TODO/FIXME (禁止糊弄) ===
if [[ $LLM_EXIT_CODE -eq 0 ]]; then
    echo "[$(get_timestamp)] === Checking for TODO/FIXME ==="
    TODO_COUNT=0
    if [[ -d "$REPO_DIR" ]]; then
        TODO_COUNT=$(grep -r -l "TODO\|FIXME\|placeholder\|XXX" "$REPO_DIR" --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" 2>/dev/null | wc -l | tr -d ' ')
    fi

    if [[ "$TODO_COUNT" -gt 0 ]]; then
        echo "[$(get_timestamp)] WARNING: Found $TODO_COUNT files with TODO/FIXME/placeholder"
        echo "TODO_CHECK: WARNING (found $TODO_COUNT files)" >> "$LOG_FILE"
    else
        echo "[$(get_timestamp)] TODO check: PASSED"
    fi

    # === Best Practice: Run tests if available ===
    echo "[$(get_timestamp)] === Running verification tests ==="
    TEST_PASSED=true
    VERIFY_EXIT_CODE=0
    TEST_OUTPUT=""

    if [[ -d "$REPO_DIR" ]]; then
        cd "$REPO_DIR"

        # Python/pytest support
        if [[ -f "$REPO_DIR/requirements.txt" ]] || [[ -f "$REPO_DIR/pyproject.toml" ]]; then
            if [[ -f "$REPO_DIR/.venv/bin/activate" ]]; then
                echo "[$(get_timestamp)] Found Python venv, running pytest..."
                source "$REPO_DIR/.venv/bin/activate"
                if command -v pytest &> /dev/null; then
                    TEST_OUTPUT=$(run_with_timeout "$VERIFY_TIMEOUT_SECS" "$VERIFY_TIMEOUT_KILL_SECS" pytest -v --tb=short 2>&1)
                    TEST_CODE=$?
                    [[ $TEST_CODE -ne 0 ]] && TEST_PASSED=false
                    [[ $VERIFY_EXIT_CODE -eq 0 && $TEST_CODE -ne 0 ]] && VERIFY_EXIT_CODE=$TEST_CODE
                    echo "$TEST_OUTPUT" >> "$LOG_FILE"
                elif [[ -f "$REPO_DIR/Makefile" ]] && grep -q 'test:' "$REPO_DIR/Makefile"; then
                    echo "[$(get_timestamp)] Running: make test"
                    TEST_OUTPUT=$(run_with_timeout "$VERIFY_TIMEOUT_SECS" "$VERIFY_TIMEOUT_KILL_SECS" make test 2>&1)
                    TEST_CODE=$?
                    [[ $TEST_CODE -ne 0 ]] && TEST_PASSED=false
                    [[ $VERIFY_EXIT_CODE -eq 0 && $TEST_CODE -ne 0 ]] && VERIFY_EXIT_CODE=$TEST_CODE
                    echo "$TEST_OUTPUT" >> "$LOG_FILE"
                fi
            elif command -v pytest &> /dev/null; then
                echo "[$(get_timestamp)] Running: pytest"
                TEST_OUTPUT=$(run_with_timeout "$VERIFY_TIMEOUT_SECS" "$VERIFY_TIMEOUT_KILL_SECS" pytest -v --tb=short 2>&1)
                TEST_CODE=$?
                [[ $TEST_CODE -ne 0 ]] && TEST_PASSED=false
                [[ $VERIFY_EXIT_CODE -eq 0 && $TEST_CODE -ne 0 ]] && VERIFY_EXIT_CODE=$TEST_CODE
                echo "$TEST_OUTPUT" >> "$LOG_FILE"
            fi
        fi

        # Node.js support
        if [[ -f "$REPO_DIR/package.json" ]]; then
            if grep -q '"test"' "$REPO_DIR/package.json"; then
                echo "[$(get_timestamp)] Running: npm test"
                TEST_OUTPUT=$(run_with_timeout "$VERIFY_TIMEOUT_SECS" "$VERIFY_TIMEOUT_KILL_SECS" npm test 2>&1)
                TEST_CODE=$?
                [[ $TEST_CODE -ne 0 ]] && TEST_PASSED=false
                [[ $VERIFY_EXIT_CODE -eq 0 && $TEST_CODE -ne 0 ]] && VERIFY_EXIT_CODE=$TEST_CODE
                echo "$TEST_OUTPUT" >> "$LOG_FILE"
            fi
        fi

        # Makefile support
        if [[ -f "$REPO_DIR/Makefile" ]]; then
            if grep -q 'test:' "$REPO_DIR/Makefile"; then
                echo "[$(get_timestamp)] Running: make test"
                TEST_OUTPUT=$(run_with_timeout "$VERIFY_TIMEOUT_SECS" "$VERIFY_TIMEOUT_KILL_SECS" make test 2>&1)
                TEST_CODE=$?
                [[ $TEST_CODE -ne 0 ]] && TEST_PASSED=false
                [[ $VERIFY_EXIT_CODE -eq 0 && $TEST_CODE -ne 0 ]] && VERIFY_EXIT_CODE=$TEST_CODE
                echo "$TEST_OUTPUT" >> "$LOG_FILE"
            fi
        fi

        # run.sh support
        if [[ -f "$REPO_DIR/run.sh" ]]; then
            if grep -q 'test' "$REPO_DIR/run.sh"; then
                echo "[$(get_timestamp)] Running: ./run.sh test"
                TEST_OUTPUT=$(run_with_timeout "$VERIFY_TIMEOUT_SECS" "$VERIFY_TIMEOUT_KILL_SECS" bash ./run.sh test 2>&1)
                TEST_CODE=$?
                [[ $TEST_CODE -ne 0 ]] && TEST_PASSED=false
                [[ $VERIFY_EXIT_CODE -eq 0 && $TEST_CODE -ne 0 ]] && VERIFY_EXIT_CODE=$TEST_CODE
                echo "$TEST_OUTPUT" >> "$LOG_FILE"
            fi
        fi
    fi

    # Best Practice: 测试失败必须标记为 failed
    if [[ "$TEST_PASSED" == "false" ]]; then
        echo "[$(get_timestamp)] ❌ TEST FAILED - marking task as FAILED"
        echo "TEST_RESULT: FAILED" >> "$LOG_FILE"
        if [[ $VERIFY_EXIT_CODE -eq 124 ]]; then
            EXIT_CODE=124
            ERROR_MSG="Verification timeout after ${VERIFY_TIMEOUT_SECS}s"
        else
            EXIT_CODE=1
            ERROR_MSG="Verification tests failed"
        fi
    else
        echo "[$(get_timestamp)] ✅ ALL TESTS PASSED"
        echo "TEST_RESULT: PASSED" >> "$LOG_FILE"
        EXIT_CODE=0
    fi
else
    EXIT_CODE=$LLM_EXIT_CODE
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
