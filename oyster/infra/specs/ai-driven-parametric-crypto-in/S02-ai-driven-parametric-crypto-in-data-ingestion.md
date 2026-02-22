---
task_id: S02-ai-driven-parametric-crypto-in-data-ingestion
project: ai-driven-parametric-crypto-in
priority: 1
depends_on: ["S01-ai-driven-parametric-crypto-in-bootstrap"]
modifies: ["backend/data_ingestion.py"]
executor: glm
---
## 目标
实现数据获取与预处理模块，从加密货币交易所API获取实时市场数据

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
