---
task_id: S04-新方向-ai驱动的web3交易助手-集成Web3交易接口
project: 新方向-ai驱动的web3交易助手
priority: 2
depends_on: ["S01-新方向-ai驱动的web3交易助手-bootstrap"]
modifies: ["backend/web3.py", "backend/main.py"]
executor: glm
---
## 目标
集成Web3交易接口，支持用户进行区块链交易操作。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
