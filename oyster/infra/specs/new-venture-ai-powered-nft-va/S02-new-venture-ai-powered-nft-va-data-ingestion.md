---
task_id: S02-new-venture-ai-powered-nft-va-data-ingestion
project: new-venture-ai-powered-nft-va
priority: 1
depends_on: ["S01-new-venture-ai-powered-nft-va-bootstrap"]
modifies: ["backend/data_ingestion.py", "backend/main.py"]
executor: glm
---
## 目标
实现NFT市场数据的API集成与数据抓取模块

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
