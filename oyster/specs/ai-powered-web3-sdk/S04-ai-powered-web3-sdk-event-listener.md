---
task_id: S04-ai-powered-web3-sdk-event-listener
project: ai-powered-web3-sdk
priority: 2
depends_on: ["S01-ai-powered-web3-sdk-bootstrap"]
modifies: ["backend/events.py", "backend/services/event_listener.py"]
executor: glm
---
## 目标
开发事件监听器，实时监控区块链事件并处理

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
