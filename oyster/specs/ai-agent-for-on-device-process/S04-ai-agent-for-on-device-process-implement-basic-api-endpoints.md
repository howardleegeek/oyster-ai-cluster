---
task_id: S04-ai-agent-for-on-device-process-implement-basic-api-endpoints
project: ai-agent-for-on-device-process
priority: 1
depends_on: ["S01-ai-agent-for-on-device-process-bootstrap"]
modifies: ["backend/main.py", "backend/routes.py"]
executor: glm
---
## 目标
实现基础的 API 端点，包括健康检查和简单的 CRUD 操作

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
