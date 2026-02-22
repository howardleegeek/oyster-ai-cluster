---
task_id: U04
title: "dispatch.py modifies 冲突检测"
depends_on: []
modifies: ["dispatch/dispatch.py"]
executor: glm
---

## 目标
dispatch 调度时检查 modifies 交集，有冲突的任务串行执行。

## 学到的
文章要求：PATCH 带 baseRevision，不匹配返回 409。
我们的问题：32 个 agent 并行改同一项目，rsync basename 冲突、同文件互踩。dispatch.py 有 file_locks 表但 exclusive 默认 false。

## 改动

### dispatch.py schedule_tasks 函数
在分配任务前加冲突检测：

```python
def has_file_conflict(task, running_tasks):
    """检查 task 的 modifies 是否与正在运行的任务有交集"""
    task_files = set(task.get('modifies', []))
    if not task_files:
        return False
    for running in running_tasks:
        running_files = set(running.get('modifies', []))
        if task_files & running_files:  # 交集非空
            return True
    return False

# 在 schedule 循环中:
if has_file_conflict(task, currently_running):
    log(f"⚠️ {task['id']} conflicts with running task, deferring")
    continue  # 跳过，下个周期再试
```

### collect 时 diff 检查
collect 拉回文件后，对比 Mac-1 本地版本：
- 如果同一文件被两个任务改了 → 报警 + 不自动合并
- 人工介入或选择后到的版本

## 验收标准
- [ ] 两个任务 modifies 有交集时，后一个不会被并行调度
- [ ] collect 时检测到同文件被多个任务修改 → 报警
