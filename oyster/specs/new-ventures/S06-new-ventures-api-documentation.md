---
task_id: S06-new-ventures-api-documentation
project: new-ventures
priority: 2
depends_on: ["S01-new-ventures-bootstrap"]
modifies: ["backend/main.py", "backend/openapi.py"]
executor: glm
---
## 目标
为API生成交互式文档，使用Swagger UI进行展示

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
