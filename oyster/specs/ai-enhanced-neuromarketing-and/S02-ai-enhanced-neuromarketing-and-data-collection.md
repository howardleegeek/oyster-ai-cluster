---
task_id: S02-ai-enhanced-neuromarketing-and-data-collection
project: ai-enhanced-neuromarketing-and
priority: 1
depends_on: ["S01-ai-enhanced-neuromarketing-and-bootstrap"]
modifies: ["backend/data_collection.py"]
executor: glm
---
## 目标
实现从社交媒体平台收集用户行为数据的API端点

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
