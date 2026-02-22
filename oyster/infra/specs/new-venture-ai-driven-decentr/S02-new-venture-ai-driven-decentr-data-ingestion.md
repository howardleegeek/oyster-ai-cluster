---
task_id: S02-new-venture-ai-driven-decentr-data-ingestion
project: new-venture-ai-driven-decentr
priority: 1
depends_on: ["S01-new-venture-ai-driven-decentr-bootstrap"]
modifies: ["backend/data_ingestion.py"]
executor: glm
---
## 目标
实现数据抓取模块，从多个DeFi数据源获取实时市场数据

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
