---
task_id: S02-ai-powered-trading-data-ingestion
project: ai-powered-trading
priority: 1
depends_on: ["S01-ai-powered-trading-bootstrap"]
modifies: ["backend/data_ingestion.py", "backend/models.py", "backend/database.py"]
executor: glm
---
## 目标
实现数据获取与处理模块，从指定API获取实时金融数据并存储到数据库

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
