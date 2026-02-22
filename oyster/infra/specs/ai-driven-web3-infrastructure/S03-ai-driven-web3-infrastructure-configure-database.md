---
task_id: S03-ai-driven-web3-infrastructure-configure-database
project: ai-driven-web3-infrastructure
priority: 1
depends_on: ["S01-ai-driven-web3-infrastructure-bootstrap"]
modifies: ["backend/database.py", "backend/models.py"]
executor: glm
---
## 目标
配置数据库连接并设置ORM模型

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
