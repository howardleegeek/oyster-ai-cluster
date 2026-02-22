---
task_id: S03-ai-powered-nft-valuation-data-storage
project: ai-powered-nft-valuation
priority: 1
depends_on: ["S01-ai-powered-nft-valuation-bootstrap"]
modifies: ["backend/models.py", "backend/database.py"]
executor: glm
---
## 目标
设计并实现数据库模型，用于存储收集到的NFT数据和估值结果

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
