---
task_id: S03-competitor-gap-driven-data-storage
project: competitor-gap-driven
priority: 1
depends_on: ["S01-competitor-gap-driven-bootstrap"]
modifies: ["backend/models.py", "backend/database.py"]
executor: glm
---
## 目标
设计并实现用于存储竞争对手产品数据的数据库模型

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
