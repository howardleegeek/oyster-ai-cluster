---
task_id: S04-self-improving-ai-agents-with-data-storage
project: self-improving-ai-agents-with-
priority: 2
depends_on: ["S01-self-improving-ai-agents-with--bootstrap"]
modifies: ["backend/models.py", "backend/database.py"]
executor: glm
---
## 目标
设计和实现用于存储自我改进数据的数据库架构。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
