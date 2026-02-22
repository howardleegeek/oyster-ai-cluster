---
task_id: S05-ai-driven-defi-advisor-api-endpoints
project: ai-driven-defi-advisor
priority: 2
depends_on: ["S01-ai-driven-defi-advisor-bootstrap"]
modifies: ["backend/main.py", "backend/endpoints.py"]
executor: glm
---
## 目标
设计和实现API端点，用于前端与后端的数据交互

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
