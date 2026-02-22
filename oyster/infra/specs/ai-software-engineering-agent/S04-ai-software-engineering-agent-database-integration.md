---
task_id: S04-ai-software-engineering-agent-database-integration
project: ai-software-engineering-agent
priority: 2
depends_on: ["S01-ai-software-engineering-agent-bootstrap"]
modifies: ["backend/models/agent_model.py", "backend/database/database.py"]
executor: glm
---
## 目标
集成数据库以存储AI agent的会话数据和用户信息

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
