---
task_id: S04-new-ventures-basic-crud-operations
project: new-ventures
priority: 1
depends_on: ["S01-new-ventures-bootstrap"]
modifies: ["backend/crud.py", "backend/routers/main.py", "backend/schemas/main.py", "tests/test_crud.py"]
executor: glm
---
## 目标
为主要数据模型实现基本的CRUD（创建、读取、更新、删除）API端点

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
