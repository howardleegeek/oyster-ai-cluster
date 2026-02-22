---
task_id: S03-ai-sales-startup-database-modeling
project: ai-sales-startup
priority: 1
depends_on: ["S01-ai-sales-startup-bootstrap"]
modifies: ["backend/models.py", "backend/database.py"]
executor: glm
---
## 目标
设计并实现数据库模型，包括客户、联系人、销售机会等实体

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
