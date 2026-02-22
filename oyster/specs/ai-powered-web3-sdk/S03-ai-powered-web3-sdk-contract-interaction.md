---
task_id: S03-ai-powered-web3-sdk-contract-interaction
project: ai-powered-web3-sdk
priority: 1
depends_on: ["S01-ai-powered-web3-sdk-bootstrap"]
modifies: ["backend/contracts.py", "backend/routes/contracts.py"]
executor: glm
---
## 目标
实现与智能合约的交互功能，包括读取和写入数据

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
