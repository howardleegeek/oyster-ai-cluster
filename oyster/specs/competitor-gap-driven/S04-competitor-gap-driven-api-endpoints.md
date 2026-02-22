---
task_id: S04-competitor-gap-driven-api-endpoints
project: competitor-gap-driven
priority: 1
depends_on: ["S01-competitor-gap-driven-bootstrap"]
modifies: ["backend/main.py", "backend/endpoints.py"]
executor: glm
---
## 目标
为竞争对手产品数据创建CRUD API端点

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
