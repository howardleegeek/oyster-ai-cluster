---
task_id: S02-ar-glasses-startup-opportunity-database-setup
project: ar-glasses-startup-opportunity
priority: 1
depends_on: ["S01-ar-glasses-startup-opportunity-bootstrap"]
modifies: ["backend/models.py", "backend/database.py"]
executor: glm
---
## 目标
设置项目数据库并定义初始数据模型

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
