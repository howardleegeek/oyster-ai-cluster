---
task_id: S02-ai-driven-web3-infrastructure-initialize-fastapi-app
project: ai-driven-web3-infrastructure
priority: 1
depends_on: ["S01-ai-driven-web3-infrastructure-bootstrap"]
modifies: ["backend/main.py"]
executor: glm
---
## 目标
初始化FastAPI应用并设置基础路由

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
