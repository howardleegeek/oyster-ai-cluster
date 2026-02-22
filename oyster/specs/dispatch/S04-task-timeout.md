---
task_id: S04-task-timeout
project: dispatch
priority: 1
depends_on: []
modifies: ["dispatch/task-wrapper.sh"]
executor: glm
---
## 目标
给 task-wrapper.sh 的 claude 调用加 1 小时超时保护

## 具体改动
文件: `~/Downloads/dispatch/task-wrapper.sh`

找到第 120 行附近的 claude 执行行:
```
timeout 3600 claude -p "$(cat "$SPEC_FILE")" --dangerously-skip-permissions > "$LOG_FILE" 2>&1
```

将所有 `claude -p` 调用前加 `timeout 3600`。

在超时后（EXIT_CODE=124），fallback 循环里加处理：
```bash
if [[ $EXIT_CODE -eq 124 ]]; then
    echo "[$(get_timestamp)] TIMEOUT after 3600s" | tee -a "$LOG_FILE"
    break
fi
```

同时在最终 status.json 写入时，如果 EXIT_CODE=124，status 改为 "timeout"（不是 "failed"）。

## 验收标准
- [ ] `grep -c 'timeout 3600' task-wrapper.sh` 返回大于 0
- [ ] `bash -n task-wrapper.sh` 语法通过
- [ ] status.json 在超时时写 "timeout" 状态

## 不要做
- 不改 fallback 逻辑
- 不改 git commit/push 逻辑
- 不加新依赖
