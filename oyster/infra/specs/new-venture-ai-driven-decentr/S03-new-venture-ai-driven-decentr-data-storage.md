---
task_id: S03-new-venture-ai-driven-decentr-data-storage
project: new-venture-ai-driven-decentr
priority: 1
depends_on: ["S01-new-venture-ai-driven-decentr-bootstrap"]
modifies: ["backend/models.py", "backend/database.py"]
executor: glm
---
## 目标
设计并实现数据库模型，用于存储和检索抓取的DeFi数据

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
