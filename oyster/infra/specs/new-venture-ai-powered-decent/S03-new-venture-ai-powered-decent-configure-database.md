---
task_id: S03-new-venture-ai-powered-decent-configure-database
project: new-venture-ai-powered-decent
priority: 1
depends_on: ["S01-new-venture-ai-powered-decent-bootstrap"]
modifies: ["backend/database.py", "backend/models/__init__.py"]
executor: glm
---
## 目标
配置数据库连接和 ORM（使用 SQLAlchemy），定义基础数据模型。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
