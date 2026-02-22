---
task_id: I-gem-4-email
project: marketing-stack
priority: 4
estimated_minutes: 15
depends_on: [B08-listmonk-deploy]
modifies: ["oyster/products/gem-platform/frontend/src/components/EmailSignup.tsx"]
executor: glm
---
## 目标
Create email signup form for GEM Platform landing page, connect to Listmonk list, welcome email template

## 约束
- React component: EmailSignup.tsx
- POST to Listmonk API
- List name: gem-subscribers
- Double opt-in enabled
- Welcome email: platform overview + demo scheduling link
- Source tag: landing_page

## 验收标准
- [ ] EmailSignup.tsx component created
- [ ] Form validates email
- [ ] Success confirmation displayed
- [ ] Subscriber added to Listmonk
- [ ] Welcome email with demo link sent
- [ ] Error handling works

## 不要做
- No company info collection yet
- No immediate sales outreach
- No trial account creation
