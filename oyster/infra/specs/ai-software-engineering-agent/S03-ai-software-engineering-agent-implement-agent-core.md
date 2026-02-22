---
task_id: S03-ai-software-engineering-agent-implement-agent-core
project: ai-software-engineering-agent
priority: 1
depends_on: ["S01-ai-software-engineering-agent-bootstrap"]
modifies: ["backend/services/agent_service.py", "backend/utils/ai_utils.py"]
executor: glm
---
## 目标
实现AI agent的核心逻辑，包括与AI模型的交互

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
