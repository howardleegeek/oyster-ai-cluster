---
task_id: S04-ai-sales-startup-api-endpoints
project: ai-sales-startup
priority: 1
depends_on: ["S01-ai-sales-startup-bootstrap"]
modifies: ["backend/endpoints.py", "backend/main.py"]
executor: glm
---
## 目标
创建API端点以支持CRUD操作（客户、联系人、销售机会等）

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
