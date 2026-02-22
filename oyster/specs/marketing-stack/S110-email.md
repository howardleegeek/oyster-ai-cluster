---
task_id: S110-email
project: marketing-stack
priority: 4
estimated_minutes: 15
depends_on: [B08-listmonk-deploy]
modifies: ["oyster/products/getpuffy/web/src/components/EmailSignup.tsx"]
executor: glm
---
## 目标
Create email signup form for getPuffy landing page, connect to Listmonk list, welcome email template

## 约束
- React component: EmailSignup.tsx
- POST to Listmonk API
- List name: getpuffy-subscribers
- Double opt-in enabled
- Welcome email: brand story + launch discount code
- Source tag: landing_page

## 验收标准
- [ ] EmailSignup.tsx component created
- [ ] Form validates email
- [ ] Success confirmation displayed
- [ ] Subscriber added to Listmonk
- [ ] Welcome email with discount sent
- [ ] Error handling works

## 不要做
- No size/preference collection yet
- No immediate upsell
- No SMS signup
