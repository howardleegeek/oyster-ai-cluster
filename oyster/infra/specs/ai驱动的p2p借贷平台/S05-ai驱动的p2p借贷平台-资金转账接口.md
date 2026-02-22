---
task_id: S05-ai驱动的p2p借贷平台-资金转账接口
project: ai驱动的p2p借贷平台
priority: 2
depends_on: ["S01-ai驱动的p2p借贷平台-bootstrap"]
modifies: ["backend/payment.py", "backend/database.py", "tests/test_payment.py"]
executor: glm
---
## 目标
集成第三方支付网关，实现借款人和贷款人之间的资金转账功能。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
