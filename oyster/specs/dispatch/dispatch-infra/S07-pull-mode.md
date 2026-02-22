---
task_id: S07-pull-mode
project: dispatch
priority: 1
depends_on: []
modifies: ["dispatch/dispatch.py", "dispatch/task-poller.py"]
executor: glm
---

# Pull Mode: 节点空闲时主动抢任务

## 目标
让节点空闲时主动从队列拉取任务，而不是等 dispatch 推送。

## 背景
当前 push 模式问题：
- 调度器循环 30s 检查一次，可能延迟
- 节点有空转时间
- 需要 7×24 调度器运行

## 架构

```
节点 (task-poller)          调度器 (dispatch.py)
     |                           |
     |-- poll() ---------------->|
     |<-- returns pending task --|
     |-- claim(task_id) -------->|
     |<-- OK, you're owner ------|
     |-- execute(claude-glm) --->|
     |-- finish() -------------->|
```

## 实现方案

### 1. dispatch.py 新增命令

```bash
# 节点调用
python3 dispatch.py poll <project>     # 获取pending任务（不claim）
python3 dispatch.py claim <task_id>    # 抢占任务
python3 dispatch.py finish <task_id>   # 标记完成
python3 dispatch.py heartbeat <task_id> # 心跳
```

### 2. task-poller.py (常驻节点)

```python
# 每 10s 检查一次
while True:
    tasks = dispatch.poll("dispatch")  # 获取所有 pending
    if tasks:
        task = select_best(tasks)       # 选择最优任务
        dispatch.claim(task.id)        # 抢占
        execute(task)                   # 执行
        dispatch.finish(task.id)        # 标记完成
    else:
        sleep(10)
```

### 3. 任务选择策略

- priority 低的先做
- depends_on 依赖少的先做
- 同一 project 的任务集中处理

### 4. 心跳机制

- 每 30s 发送 heartbeat
- 超时 5 分钟标记为 stale

## 改动文件

| 文件 | 操作 |
|------|------|
| `dispatch/dispatch.py` | 新增 poll/claim/finish/heartbeat 子命令 |
| `dispatch/task-poller.py` | 新建，节点常驻进程 |

## 验收标准

- [ ] `dispatch.py poll dispatch` 返回 pending 任务列表
- [ ] `dispatch.py claim <task_id>` 成功claim后其他节点无法再claim
- [ ] task-poller.py 可以独立运行
- [ ] 节点空闲时自动拉取任务
- [ ] 任务执行后自动标记完成

## 不要做

- 不改现有任务的执行逻辑
- 不删除现有的 push 调度模式
- 不动 nodes.json 和 projects.json
