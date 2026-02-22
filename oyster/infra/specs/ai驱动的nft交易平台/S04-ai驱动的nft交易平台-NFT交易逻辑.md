---
task_id: S04-ai驱动的nft交易平台-NFT交易逻辑
project: ai驱动的nft交易平台
priority: 1
depends_on: ["S01-ai驱动的nft交易平台-bootstrap"]
modifies: ["backend/transaction.py", "backend/main.py", "tests/test_transaction.py"]
executor: glm
---
## 目标
实现NFT的购买、出售和转移功能，包括交易记录和支付集成

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
