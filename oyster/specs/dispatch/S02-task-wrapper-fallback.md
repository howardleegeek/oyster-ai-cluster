---
task_id: S02-task-wrapper-fallback
project: dispatch
priority: 1
depends_on: []
modifies: ["dispatch/task-wrapper.sh"]
executor: glm
---

# task-wrapper.sh API Fallback

## 目标
claude 调用失败时，检查是否限流错误，自动切换 API provider 重试。

## 当前逻辑 (task-wrapper.sh 行 145-153)
```bash
set +e
if [[ "$API_MODE" == "codex" ]]; then
    cd "$WORKING_DIR" && codex exec --skip-git-repo-check --full-auto "$(cat "$SPEC_FILE")" --json > "$LOG_FILE" 2>&1
else
    $CLAUDE_CMD -p "$(cat "$SPEC_FILE")" --dangerously-skip-permissions > "$LOG_FILE" 2>&1
fi
EXIT_CODE=$?
set -e
```

## 改动

### 1. 新增限流检测函数
```bash
is_rate_limit_error() {
    local log_file="$1"
    grep -qiE '(429|rate_limit|overloaded|capacity|quota)' "$log_file" 2>/dev/null
}
```

### 2. 新增 API mode 切换函数
```bash
get_fallback_mode() {
    case "$1" in
        direct) echo "zai" ;;
        zai) echo "direct" ;;
        *) echo "" ;;
    esac
}
```

### 3. 替换执行逻辑 (行 145-153)

用重试循环替换原来的单次调用：

```bash
MAX_RETRIES=2
retry_count=0
CURRENT_API_MODE="$API_MODE"

set +e
while true; do
    echo "[$( get_timestamp )] Attempt $((retry_count + 1))/$((MAX_RETRIES + 1)), API_MODE=$CURRENT_API_MODE" >> "$LOG_FILE"

    # 设置 claude 命令
    if [[ "$CURRENT_API_MODE" == "zai" ]]; then
        if [[ -n "${ZAI_API_KEY:-}" ]]; then
            export ANTHROPIC_AUTH_TOKEN="$ZAI_API_KEY"
            export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
        fi
        CLAUDE_CMD="claude"
    elif [[ "$CURRENT_API_MODE" == "direct" ]]; then
        unset ANTHROPIC_AUTH_TOKEN ANTHROPIC_BASE_URL 2>/dev/null || true
        CLAUDE_CMD="claude"
    fi

    if [[ "$CURRENT_API_MODE" == "codex" ]]; then
        cd "$WORKING_DIR" && codex exec --skip-git-repo-check --full-auto "$(cat "$SPEC_FILE")" --json > "$LOG_FILE" 2>&1
        EXIT_CODE=$?
    else
        $CLAUDE_CMD -p "$(cat "$SPEC_FILE")" --dangerously-skip-permissions > "$LOG_FILE" 2>&1
        EXIT_CODE=$?
    fi

    # 成功 → 跳出
    if [[ $EXIT_CODE -eq 0 ]]; then
        break
    fi

    # codex 不做 fallback
    if [[ "$CURRENT_API_MODE" == "codex" ]]; then
        break
    fi

    # 检查是否限流
    if is_rate_limit_error "$LOG_FILE" && [[ $retry_count -lt $MAX_RETRIES ]]; then
        NEXT_MODE=$(get_fallback_mode "$CURRENT_API_MODE")
        if [[ -z "$NEXT_MODE" ]]; then
            break
        fi
        echo "[$( get_timestamp )] Rate limit detected, switching $CURRENT_API_MODE → $NEXT_MODE, waiting 30s..." >> "$LOG_FILE"
        sleep 30
        CURRENT_API_MODE="$NEXT_MODE"
        retry_count=$((retry_count + 1))
    else
        # 非限流错误，不重试
        break
    fi
done
set -e
```

### 注意事项
- LOG_FILE 在重试时会被覆盖（`>` 不是 `>>`），因为 claude 输出很长，追加会导致文件巨大。重试信息写在覆盖前的 echo 行。
- 如果实际 task-wrapper.sh 中 LOG_FILE 用的是追加模式，则保持追加。
- ZAI_API_KEY 环境变量在 zai 模式下必须存在（已有检查逻辑在上方）。

## 约束
- 不动 git 模式逻辑（行 45-64, 155-176）
- 不动 status.json 写入格式（行 78-98, 181-end）
- 不改参数签名
- 不改 heartbeat 逻辑
- 纯 bash，不加依赖

## 验收标准
- [ ] 正常调用成功时不触发 fallback
- [ ] 模拟 429 错误（LOG_FILE 包含 429）时自动切换 API mode
- [ ] 最多重试 2 次
- [ ] codex 模式失败不重试
- [ ] 非限流错误不重试
