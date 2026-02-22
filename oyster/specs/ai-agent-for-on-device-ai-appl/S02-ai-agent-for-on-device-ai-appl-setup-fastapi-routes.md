---
task_id: S02-ai-agent-for-on-device-ai-appl-setup-fastapi-routes
project: ai-agent-for-on-device-ai-appl
priority: 1
depends_on: ["S01-ai-agent-for-on-device-ai-appl-bootstrap"]
modifies: ["backend/main.py", "backend/routes/__init__.py"]
executor: glm
---
## 目标
设置FastAPI的基本路由结构，包括健康检查和版本信息端点

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
