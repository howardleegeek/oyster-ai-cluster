---
task_id: S05-new-venture-ai-powered-decent-dao-core-logic
project: new-venture-ai-powered-decent
priority: 2
depends_on: ["S01-new-venture-ai-powered-decent-bootstrap"]
modifies: ["backend/router/dao.py", "backend/services/dao.py", "backend/models/dao.py"]
executor: glm
---
## 目标
开发 DAO 的核心逻辑，包括提案创建、投票机制和结果计算。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
