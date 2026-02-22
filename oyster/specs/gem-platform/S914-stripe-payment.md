---
task_id: S914-stripe-payment
project: gem-platform
priority: 1
depends_on: []
modifies:
  - backend/app/api/payment.py
  - backend/app/services/stripe_service.py
  - lumina/services/paymentApi.ts
executor: glm
---

## Week 2 - Stripe 支付

## 目标
实现 Stripe 信用卡支付

## 功能
1. 创建 Payment Intent
2. Webhook 回调处理
3. 订单对账 (幂等)

## API
POST /api/payment/create-intent
POST /api/payment/webhook

## 验收
- [ ] 支付可完成
- [ ] 幂等处理
