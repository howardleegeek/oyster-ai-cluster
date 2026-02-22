---
task_id: S04-ai-powered-nft-valuation-feature-engineering
project: ai-powered-nft-valuation
priority: 2
depends_on: ["S01-ai-powered-nft-valuation-bootstrap"]
modifies: ["backend/feature_engineering.py"]
executor: glm
---
## 目标
开发特征工程模块，从收集到的数据中提取用于估值的关键特征

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
