---
task_id: DI04-oom-protection
project: dispatch-infra
priority: 1
estimated_minutes: 30
depends_on: []
modifies: ["task-wrapper.sh"]
executor: glm
---
## 目标
在 task-wrapper.sh 中添加内存限制，防止 opencode 进程被 OOM killer 杀掉

## 技术方案
在 task-wrapper.sh 启动 opencode 之前，添加内存限制：

1. **使用 systemd-run 包装执行**（如果 systemd 可用）:
```bash
if command -v systemd-run &>/dev/null; then
    # Limit to 2GB memory per task
    systemd-run --scope --property=MemoryMax=2G --property=MemorySwapMax=0 \
        opencode run -m "$MODEL" "$SPEC_CONTENT"
else
    # Fallback: use ulimit
    ulimit -v $((2 * 1024 * 1024))  # 2GB virtual memory limit
    opencode run -m "$MODEL" "$SPEC_CONTENT"
fi
```

2. **添加内存监控**:
```bash
# Log memory usage every 30s in background
monitor_memory() {
    while kill -0 $TASK_PID 2>/dev/null; do
        MEM=$(ps -o rss= -p $TASK_PID 2>/dev/null | awk '{printf "%.0fMB", $1/1024}')
        echo "[mem] PID $TASK_PID: $MEM" >> "$LOG_FILE"
        sleep 30
    done
}
```

## 约束
- 修改现有 task-wrapper.sh
- 2GB 内存限制（可通过 MAX_TASK_MEMORY 环境变量覆盖）
- systemd-run 优先，ulimit 兜底
- macOS 节点不用 systemd-run（用 ulimit）
- 不改 opencode 执行参数

## 验收标准
- [ ] Linux 节点上 opencode 进程有 2GB 内存限制
- [ ] macOS 节点上用 ulimit 限制
- [ ] 内存使用定期写入 task.log
- [ ] 超内存时优雅退出而不是被 SIGKILL

## 不要做
- 不改 opencode 二进制
- 不改 dispatch-controller.py
- 不改 worker daemon
