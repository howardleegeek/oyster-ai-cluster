---
task_id: S05-decentralized-ai-compute-marke-payment-integration
project: decentralized-ai-compute-marke
priority: 2
depends_on: ["S01-decentralized-ai-compute-marke-bootstrap"]
modifies: ["backend/payments.py", "backend/models/payment.py", "tests/test_payments.py"]
executor: glm
---
## 目标
集成支付系统，处理用户对AI计算资源的支付和结算

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
