---
task_id: S04-ai-agent-for-on-device-ai-appl-database-integration
project: ai-agent-for-on-device-ai-appl
priority: 2
depends_on: ["S01-ai-agent-for-on-device-ai-appl-bootstrap"]
modifies: ["backend/database.py", "backend/models/__init__.py", "backend/crud.py", "tests/test_crud.py"]
executor: glm
---
## 目标
集成数据库（如SQLite或PostgreSQL），并设置ORM模型以支持数据持久化

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
