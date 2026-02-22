---
task_id: S02-competitor-gap-driven-data-collection
project: competitor-gap-driven
priority: 1
depends_on: ["S01-competitor-gap-driven-bootstrap"]
modifies: ["backend/data_collection.py"]
executor: glm
---
## 目标
实现从竞争对手网站抓取产品数据的脚本

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
