---
task_id: S07-pull-mode-v2
project: dispatch
priority: 1
depends_on: []
modifies: ["dispatch/dispatch.py"]
executor: local
---

# S07-pull-mode-v2: Pull 模式实现

## 目标
实现节点主动拉取任务的机制，配合 push 模式形成混合调度。

## 已有实现
- `dispatch.py poll` - 获取 pending 任务
- `dispatch.py claim` - 抢占任务
- `dispatch.py finish` - 标记完成
- `dispatch.py heartbeat` - 发送心跳

## 验证
```bash
# 测试 poll
python3 dispatch.py poll dispatch

# 测试 claim
python3 dispatch.py claim S07-test

# 测试 finish
python3 dispatch.py finish S07-test --status completed
```

## 验收标准
- [ ] poll 返回 pending 任务列表
- [ ] claim 原子抢占
- [ ] finish 更新状态
- [ ] heartbeat 更新心跳时间
