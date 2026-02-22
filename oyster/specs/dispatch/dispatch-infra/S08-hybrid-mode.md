---
task_id: S08-hybrid-mode
project: dispatch
priority: 1
depends_on: []
modifies: ["dispatch/task-watcher.py"]
executor: local
---

# Hybrid Mode: Push + File Watcher

## 目标
节点空闲时通过文件监听自动执行任务，不依赖 Mac-1 的 push 调度。

## 架构

```
Mac-1 (controller)              节点 (executor)
     |                                |
     |-- push spec 文件 ------------->|
     |    ~/dispatch/tasks/<id>/      |
     |                                |-- watchdog 监听目录
     |                                |-- 检测到新 spec
     |                                |-- 执行 wrapper
     |                                |-- 写 status.json
     |<-- 读取 status.json -----------|
     |-- check 状态
```

## 实现方案

### 1. task-watcher.py (节点常驻)

```python
# 监听 ~/dispatch/tasks/<project>/ 目录
# 检测到新 spec.md → 执行 wrapper
# 执行完写 status.json

# 目录结构:
# ~/dispatch/tasks/<project>/
#   ├── <task_id>/
#   │   ├── spec.md        # spec 文件
#   │   ├── status.json    # 状态: pending/running/completed/failed
#   │   ├── wrapper.log    # wrapper 输出
#   │   └── result.json    # 执行结果
```

### 2. dispatch.py 改动

- 推送任务时：创建 `<task_id>/spec.md` + `status.json`
- 不再 SSH 执行 wrapper，只等节点自己执行
- 检查状态时：读 `status.json`

### 3. 任务生命周期

```
Mac-1                           节点
  |                               |
  |-- mkdir task_id/             |
  |-- write spec.md              |
  |-- write status.json:pending  |
  |                               |-- watchdog 检测到
  |                               |-- 读 spec.md
  |                               |-- 更新 status.json:running
  |                               |-- 执行 wrapper
  |                               |-- 写 result.json
  |                               |-- 更新 status.json:completed
  |-- 读 status.json:completed   |
  |-- collect 结果               |
```

## 文件清单

| 文件 | 操作 | 描述 |
|------|------|------|
| `dispatch/task-watcher.py` | 新建 | 节点文件监听器 |
| `dispatch/dispatch.py` | 修改 | 推送改为写文件 |

## task-watcher.py 功能

```python
# 每 5s 检查一次目录
# 检测新 spec → 后台执行
# 最多运行 NODE_SLOTS 个并发
# 写 status.json 同步状态
```

## 验收标准

- [ ] 推送 spec 到节点后，节点自动执行
- [ ] 节点执行完写 status.json
- [ ] Mac-1 能读到节点的状态
- [ ] 多任务并发不冲突

## 不要做

- 不改 Guardian 逻辑
- 不动 nodes.json
- 不开新端口
