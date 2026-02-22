---
task_id: S04-ai-copilot-for-consumer-defi-w-transaction-handling
project: ai-copilot-for-consumer-defi-w
priority: 1
depends_on: ["S01-ai-copilot-for-consumer-defi-w-bootstrap"]
modifies: ["backend/transaction.py", "backend/main.py", "tests/test_transaction.py"]
executor: glm
---
## 目标
实现交易处理逻辑，包括发送和接收加密货币

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
