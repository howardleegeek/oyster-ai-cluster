---
task_id: S03-ai-driven-trustless-off-chain-ai-verification-module
project: ai-driven-trustless-off-chain
priority: 1
depends_on: ["S01-ai-driven-trustless-off-chain-bootstrap"]
modifies: ["backend/verification.py", "backend/models.py"]
executor: glm
---
## 目标
开发AI驱动的验证模块以验证获取的数据

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
