---
task_id: S02-new-venture-ai-powered-decent-initialize-fastapi
project: new-venture-ai-powered-decent
priority: 1
depends_on: ["S01-new-venture-ai-powered-decent-bootstrap"]
modifies: ["backend/main.py", "backend/router/__init__.py"]
executor: glm
---
## 目标
初始化 FastAPI 应用，设置基础路由和中间件。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
