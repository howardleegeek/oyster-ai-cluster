---
task_id: S04-new-ventures-api-endpoints
project: new-ventures
priority: 1
depends_on: ["S01-new-ventures-bootstrap"]
modifies: ["backend/main.py", "backend/endpoints.py"]
executor: glm
---
## 目标
创建基本的API端点以支持核心业务逻辑

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
