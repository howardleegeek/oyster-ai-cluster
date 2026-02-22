---
task_id: S02-ai-enhanced-neuromarketing-data-ingestion
project: ai-enhanced-neuromarketing
priority: 1
depends_on: ["S01-ai-enhanced-neuromarketing-bootstrap"]
modifies: ["backend/data_ingestion.py"]
executor: glm
---
## 目标
实现数据导入功能，从神经营销数据源获取原始数据并存储至数据库

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
