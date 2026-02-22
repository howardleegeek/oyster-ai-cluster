---
task_id: S04-ai驱动的p2p借贷平台-贷款匹配算法
project: ai驱动的p2p借贷平台
priority: 2
depends_on: ["S01-ai驱动的p2p借贷平台-bootstrap"]
modifies: ["backend/matching.py", "backend/ai_model.py", "tests/test_matching.py"]
executor: glm
---
## 目标
实现基于AI的贷款匹配算法，将借款请求与合适的贷款人进行匹配。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
