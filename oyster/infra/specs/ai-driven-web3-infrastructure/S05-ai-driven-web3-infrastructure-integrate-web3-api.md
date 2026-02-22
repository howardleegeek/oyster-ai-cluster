---
task_id: S05-ai-driven-web3-infrastructure-integrate-web3-api
project: ai-driven-web3-infrastructure
priority: 2
depends_on: ["S01-ai-driven-web3-infrastructure-bootstrap"]
modifies: ["backend/web3_api.py", "backend/main.py"]
executor: glm
---
## 目标
集成Web3 API以支持区块链交互

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
