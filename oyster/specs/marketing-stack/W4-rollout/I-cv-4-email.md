---
task_id: I-cv-4-email
project: marketing-stack
priority: 4
estimated_minutes: 15
depends_on: [B08-listmonk-deploy]
modifies: ["oyster/products/clawvision/web/src/components/EmailSignup.tsx"]
executor: glm
---
## 目标
Create email signup form for ClawVision landing page, connect to Listmonk list, welcome email template

## 约束
- React component: EmailSignup.tsx
- POST to Listmonk API
- List name: clawvision-developers
- Double opt-in enabled
- Welcome email: API quickstart + free credits info
- Source tag: landing_page

## 验收标准
- [ ] EmailSignup.tsx component created
- [ ] Form validates email
- [ ] Success confirmation displayed
- [ ] Subscriber added to Listmonk
- [ ] Welcome email with API key instructions sent
- [ ] Error handling works

## 不要做
- No API key generation in email
- No immediate upsell
- No company info required
