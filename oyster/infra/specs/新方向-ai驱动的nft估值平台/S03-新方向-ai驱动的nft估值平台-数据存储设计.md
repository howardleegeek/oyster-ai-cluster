---
task_id: S03-新方向-ai驱动的nft估值平台-数据存储设计
project: 新方向-ai驱动的nft估值平台
priority: 1
depends_on: ["S01-新方向-ai驱动的nft估值平台-bootstrap"]
modifies: ["backend/models.py", "backend/database.py"]
executor: glm
---
## 目标
设计并实现数据库架构，用于存储收集到的NFT市场数据和估值结果。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
