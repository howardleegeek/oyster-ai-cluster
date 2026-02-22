---
task_id: S090-email
project: marketing-stack
priority: 4
estimated_minutes: 15
depends_on: [B08-listmonk-deploy]
modifies: ["oyster/products/clawphones/web/src/components/EmailSignup.tsx"]
executor: glm
---
## 目标
Create email signup form for ClawPhones landing page, connect to Listmonk list, welcome email template

## 约束
- React component: EmailSignup.tsx
- POST to Listmonk API
- List name: clawphones-subscribers
- Double opt-in enabled
- Welcome email: design inspiration + discount code
- Source tag: landing_page

## 验收标准
- [ ] EmailSignup.tsx component created
- [ ] Form validates email
- [ ] Success confirmation displayed
- [ ] Subscriber added to Listmonk
- [ ] Welcome email with discount sent
- [ ] Error handling works

## 不要做
- No phone number collection yet
- No immediate order prompts
- No SMS integration
