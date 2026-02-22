---
task_id: S02-new-ventures-database-setup
project: new-ventures
priority: 1
depends_on: ["S01-new-ventures-bootstrap"]
modifies: ["backend/database.py", "backend/models.py"]
executor: glm
---
## 目标
设置项目所需的数据库连接和基本模型

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
