---
task_id: S06-ai-agent-for-on-device-process-write-unit-tests-for-api-endpoints
project: ai-agent-for-on-device-process
priority: 2
depends_on: ["S01-ai-agent-for-on-device-process-bootstrap"]
modifies: ["tests/test_routes.py", "tests/test_auth.py"]
executor: glm
---
## 目标
为实现的 API 端点编写单元测试，确保功能正确性

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
