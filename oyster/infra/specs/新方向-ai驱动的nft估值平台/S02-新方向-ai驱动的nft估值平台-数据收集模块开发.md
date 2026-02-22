---
task_id: S02-新方向-ai驱动的nft估值平台-数据收集模块开发
project: 新方向-ai驱动的nft估值平台
priority: 1
depends_on: ["S01-新方向-ai驱动的nft估值平台-bootstrap"]
modifies: ["backend/data_collector.py"]
executor: glm
---
## 目标
开发用于收集NFT相关市场数据的模块，包括价格、交易量、持有人数等。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
