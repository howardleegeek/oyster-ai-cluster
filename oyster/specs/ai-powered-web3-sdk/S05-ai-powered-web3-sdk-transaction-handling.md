---
task_id: S05-ai-powered-web3-sdk-transaction-handling
project: ai-powered-web3-sdk
priority: 1
depends_on: ["S01-ai-powered-web3-sdk-bootstrap"]
modifies: ["backend/transactions.py", "backend/services/transaction_service.py"]
executor: glm
---
## 目标
实现交易处理功能，包括签名、发送和跟踪交易状态

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
