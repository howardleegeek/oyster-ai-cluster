---
task_id: S02-新方向-ai驱动的web3隐私保护-数据模型设计
project: 新方向-ai驱动的web3隐私保护
priority: 1
depends_on: ["S01-新方向-ai驱动的web3隐私保护-bootstrap"]
modifies: ["backend/models.py"]
executor: glm
---
## 目标
设计用于存储和管理用户隐私数据的数据模型

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
