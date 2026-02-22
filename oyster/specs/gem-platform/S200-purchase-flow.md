---
task_id: S200-purchase-flow
project: gem-platform
priority: 2
depends_on: []
modifies: ["backend/app/routes/pack.py", "backend/app/services/payment.py"]
executor: glm
---
## 目标
实现 pack 购买完整流程：支付网关集成、库存校验、订单创建

## 约束
- 在已有 Flask app 内修改
- 写 pytest 测试
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] pytest tests/test_purchase_flow.py 全绿
- [ ] 库存不足返回 400
- [ ] 购买成功后 pack 关联到用户账户
- [ ] 订单状态追踪

## 不要做
- 不留 TODO/FIXME/placeholder
