---
task_id: S04-ai-driven-parametric-crypto-in-policy-management
project: ai-driven-parametric-crypto-in
priority: 1
depends_on: ["S01-ai-driven-parametric-crypto-in-bootstrap"]
modifies: ["backend/policy_management.py", "tests/test_policy_management.py"]
executor: glm
---
## 目标
实现保险策略管理接口，包括创建、更新和查询保险策略

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
