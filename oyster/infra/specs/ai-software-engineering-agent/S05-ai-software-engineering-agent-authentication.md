---
task_id: S05-ai-software-engineering-agent-authentication
project: ai-software-engineering-agent
priority: 2
depends_on: ["S01-ai-software-engineering-agent-bootstrap"]
modifies: ["backend/security/authentication.py", "backend/routers/agent_router.py"]
executor: glm
---
## 目标
为API端点实现身份验证和授权机制

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
