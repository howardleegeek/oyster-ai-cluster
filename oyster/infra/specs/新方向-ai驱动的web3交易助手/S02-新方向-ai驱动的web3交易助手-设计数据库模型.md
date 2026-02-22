---
task_id: S02-新方向-ai驱动的web3交易助手-设计数据库模型
project: 新方向-ai驱动的web3交易助手
priority: 1
depends_on: ["S01-新方向-ai驱动的web3交易助手-bootstrap"]
modifies: ["backend/models.py"]
executor: glm
---
## 目标
设计用于存储用户数据、交易记录和AI分析结果的数据库模型。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
