---
task_id: S09-bridge-daemon-v2
project: dispatch
priority: 1
depends_on: []
modifies: ["dispatch/bridge-daemon.py"]
executor: local
---

# S09-bridge-daemon-v2: Opus↔OpenCode 双向通讯

## 目标
实现可靠的消息队列，让 Opus 和 OpenCode 双向通讯。

## 问题修复
- 轮询间隔：2s → 1s
- 消息持久化：收到消息立即标记 read_at
- 错误处理：异常不崩溃

## 实现
```python
# bridge-daemon.py 功能：
# 1. 每 1s 轮询 bridge.db
# 2. 收到消息自动处理
# 3. 处理结果回复
# 4. 支持 chat/command/ping/spec 类型
```

## 部署
```bash
# 启动
nohup python3 ~/Downloads/dispatch/bridge-daemon.py &

# 测试
BRIDGE_IDENTITY=opus python3 dispatch/bridge.py send opencode ping '{"text":"test"}'
```

## 验收标准
- [ ] Opus 发消息 OpenCode 收到
- [ ] OpenCode 回复 Opus 收到
- [ ] 消息不丢失 (read_at 立即更新)
