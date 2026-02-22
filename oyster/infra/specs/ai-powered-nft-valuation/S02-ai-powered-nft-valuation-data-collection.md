---
task_id: S02-ai-powered-nft-valuation-data-collection
project: ai-powered-nft-valuation
priority: 1
depends_on: ["S01-ai-powered-nft-valuation-bootstrap"]
modifies: ["backend/data_collection.py"]
executor: glm
---
## 目标
构建数据收集模块，从NFT市场API获取NFT的基本信息和交易数据

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
