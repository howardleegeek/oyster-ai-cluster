---
task_id: S02-new-ventures-database-setup
project: new-ventures
priority: 1
depends_on: ["S01-new-ventures-bootstrap"]
modifies: ["backend/database.py", "backend/models.py", "backend/config.py"]
executor: glm
---
## 目标
配置项目所需的数据库连接，包括数据库初始化和迁移脚本

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
