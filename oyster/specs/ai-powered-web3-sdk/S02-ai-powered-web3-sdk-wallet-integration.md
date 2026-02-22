---
task_id: S02-ai-powered-web3-sdk-wallet-integration
project: ai-powered-web3-sdk
priority: 1
depends_on: ["S01-ai-powered-web3-sdk-bootstrap"]
modifies: ["backend/wallet.py", "backend/routes/web3.py"]
executor: glm
---
## 目标
集成Web3钱包功能，支持用户连接和断开钱包

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
