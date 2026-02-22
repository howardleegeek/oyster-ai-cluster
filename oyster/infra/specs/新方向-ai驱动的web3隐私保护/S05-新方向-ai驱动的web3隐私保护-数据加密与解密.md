---
task_id: S05-新方向-ai驱动的web3隐私保护-数据加密与解密
project: 新方向-ai驱动的web3隐私保护
priority: 2
depends_on: ["S01-新方向-ai驱动的web3隐私保护-bootstrap"]
modifies: ["backend/security/crypto.py"]
executor: glm
---
## 目标
实现数据在存储和传输过程中的加密与解密功能

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
