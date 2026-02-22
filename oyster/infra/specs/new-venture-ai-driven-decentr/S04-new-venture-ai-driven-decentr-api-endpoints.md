---
task_id: S04-new-venture-ai-driven-decentr-api-endpoints
project: new-venture-ai-driven-decentr
priority: 1
depends_on: ["S01-new-venture-ai-driven-decentr-bootstrap"]
modifies: ["backend/main.py", "backend/endpoints.py"]
executor: glm
---
## 目标
开发FastAPI端点，允许前端查询和操作DeFi数据

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
