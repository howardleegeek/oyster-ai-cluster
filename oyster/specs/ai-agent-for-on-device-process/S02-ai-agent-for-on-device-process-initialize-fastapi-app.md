---
task_id: S02-ai-agent-for-on-device-process-initialize-fastapi-app
project: ai-agent-for-on-device-process
priority: 1
depends_on: ["S01-ai-agent-for-on-device-process-bootstrap"]
modifies: ["backend/main.py"]
executor: glm
---
## 目标
初始化 FastAPI 应用并设置基础路由

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
