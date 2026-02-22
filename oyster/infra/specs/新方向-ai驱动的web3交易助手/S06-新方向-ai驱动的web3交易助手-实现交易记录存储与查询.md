---
task_id: S06-新方向-ai驱动的web3交易助手-实现交易记录存储与查询
project: 新方向-ai驱动的web3交易助手
priority: 1
depends_on: ["S01-新方向-ai驱动的web3交易助手-bootstrap"]
modifies: ["backend/transactions.py", "backend/main.py"]
executor: glm
---
## 目标
实现交易记录的存储与查询功能，方便用户查看历史交易。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
