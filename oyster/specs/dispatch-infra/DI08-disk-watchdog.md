---
task_id: DI08-disk-watchdog
project: dispatch-infra
priority: 0
estimated_minutes: 25
depends_on: []
modifies: ["task-wrapper.sh"]
executor: glm
---
## 目标
在 task-wrapper.sh 中添加磁盘空间检查，任务开始前和运行中监控磁盘使用率，超过阈值时自动清理或拒绝执行。

## 技术方案

```bash
# Pre-flight disk check
check_disk_space() {
    local usage=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
    local threshold="${DISK_THRESHOLD:-85}"

    if [ "$usage" -ge 95 ]; then
        echo "[disk] CRITICAL: ${usage}% used, emergency cleanup..."
        # Emergency: clean all completed task repos
        find ~/dispatch/*/tasks/*/repo -maxdepth 0 -type d -mmin +30 -exec rm -rf {} + 2>/dev/null
        find ~/dispatch -name 'node_modules' -type d -exec rm -rf {} + 2>/dev/null
        find ~/dispatch -name '.git' -type d -exec rm -rf {} + 2>/dev/null
        find /tmp -name '*.log' -size +10M -delete 2>/dev/null
        usage=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
        echo "[disk] After cleanup: ${usage}%"
    fi

    if [ "$usage" -ge "$threshold" ]; then
        echo "[disk] WARNING: ${usage}% used (threshold=${threshold}%)"
        # Proactive cleanup of old task dirs
        find ~/dispatch/*/tasks -maxdepth 1 -type d -mmin +120 -exec rm -rf {}/repo {} + 2>/dev/null
    fi

    if [ "$usage" -ge 98 ]; then
        echo "[disk] ABORT: disk too full (${usage}%), refusing to start task"
        exit 1
    fi
}

# Background disk monitor (runs every 60s during task execution)
monitor_disk() {
    while kill -0 $TASK_PID 2>/dev/null; do
        local usage=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
        if [ "$usage" -ge 95 ]; then
            echo "[disk-monitor] CRITICAL: ${usage}%, running emergency cleanup"
            find ~/dispatch/*/tasks/*/repo -maxdepth 0 -type d -mmin +30 -exec rm -rf {} + 2>/dev/null
        fi
        echo "[disk-monitor] ${usage}%" >> "$LOG_FILE"
        sleep 60
    done
}
```

## 约束
- 修改现有 task-wrapper.sh
- 85% 警告，95% 自动清理，98% 拒绝执行
- 阈值可通过 DISK_THRESHOLD 环境变量覆盖
- 不改任务执行逻辑

## 验收标准
- [ ] 任务开始前检查磁盘空间
- [ ] 95%+ 时自动清理旧 repo/node_modules
- [ ] 98%+ 时拒绝启动新任务
- [ ] 运行中每 60s 监控一次
- [ ] 清理日志写入 task.log

## 不要做
- 不删 output/ 目录
- 不改 dispatch-controller.py
- 不改任务执行逻辑
