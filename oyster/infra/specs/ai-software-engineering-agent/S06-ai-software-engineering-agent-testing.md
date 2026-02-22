---
task_id: S06-ai-software-engineering-agent-testing
project: ai-software-engineering-agent
priority: 3
depends_on: ["S01-ai-software-engineering-agent-bootstrap"]
modifies: ["tests/test_agent_service.py", "tests/test_routers.py"]
executor: glm
---
## 目标
为AI agent编写单元测试和集成测试

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
