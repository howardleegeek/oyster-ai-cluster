---
task_id: S03-新方向-ai驱动的web3隐私保护-隐私保护算法集成
project: 新方向-ai驱动的web3隐私保护
priority: 1
depends_on: ["S01-新方向-ai驱动的web3隐私保护-bootstrap"]
modifies: ["backend/services/privacy.py"]
executor: glm
---
## 目标
集成AI驱动的隐私保护算法，如差分隐私或同态加密

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
