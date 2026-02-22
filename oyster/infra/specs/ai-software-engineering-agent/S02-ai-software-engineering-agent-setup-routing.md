---
task_id: S02-ai-software-engineering-agent-setup-routing
project: ai-software-engineering-agent
priority: 1
depends_on: ["S01-ai-software-engineering-agent-bootstrap"]
modifies: ["backend/main.py", "backend/routers/agent_router.py"]
executor: glm
---
## 目标
为AI agent设置FastAPI路由以处理传入的API请求

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
