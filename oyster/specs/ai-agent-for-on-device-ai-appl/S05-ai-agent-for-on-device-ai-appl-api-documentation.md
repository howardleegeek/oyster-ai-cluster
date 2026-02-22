---
task_id: S05-ai-agent-for-on-device-ai-appl-api-documentation
project: ai-agent-for-on-device-ai-appl
priority: 2
depends_on: ["S01-ai-agent-for-on-device-ai-appl-bootstrap"]
modifies: ["backend/main.py", "backend/routes/__init__.py", "docs/openapi.yaml"]
executor: glm
---
## 目标
为API端点编写详细的OpenAPI文档，确保易于理解和维护

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
