---
task_id: S04-新方向-ai驱动的web3隐私保护-用户身份验证
project: 新方向-ai驱动的web3隐私保护
priority: 2
depends_on: ["S01-新方向-ai驱动的web3隐私保护-bootstrap"]
modifies: ["backend/authentication.py"]
executor: glm
---
## 目标
实现基于Web3身份（如钱包地址）的用户身份验证机制

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
