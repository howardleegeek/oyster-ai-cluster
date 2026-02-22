---
task_id: I-cg-4-email
project: marketing-stack
priority: 4
estimated_minutes: 15
depends_on: [B08-listmonk-deploy]
modifies: ["oyster/products/clawglasses/web/src/components/EmailSignup.tsx"]
executor: glm
---
## 目标
Create email signup form for ClawGlasses landing page, connect to Listmonk list, welcome email template

## 约束
- React component: EmailSignup.tsx
- POST to Listmonk API
- List name: clawglasses-subscribers
- Double opt-in enabled
- Welcome email: style guide + first-order discount
- Source tag: landing_page

## 验收标准
- [ ] EmailSignup.tsx component created
- [ ] Form validates email
- [ ] Success confirmation displayed
- [ ] Subscriber added to Listmonk
- [ ] Welcome email with discount sent
- [ ] Error handling works

## 不要做
- No prescription upload in signup
- No insurance integration
- No complex form fields
