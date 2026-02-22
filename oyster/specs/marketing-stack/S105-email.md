---
task_id: S105-email
project: marketing-stack
priority: 4
estimated_minutes: 15
depends_on: [B08-listmonk-deploy]
modifies: ["oyster/products/oyster-republic/web/src/components/EmailSignup.tsx"]
executor: glm
---
## 目标
Create email signup form for OysterRepublic landing page, connect to Listmonk list, welcome email template

## 约束
- React component: EmailSignup.tsx
- POST to Listmonk API
- List name: oysterrepublic-citizens
- Double opt-in enabled
- Welcome email: manifesto + community invite
- Source tag: landing_page

## 验收标准
- [ ] EmailSignup.tsx component created
- [ ] Form validates email
- [ ] Success confirmation displayed
- [ ] Subscriber added to Listmonk
- [ ] Welcome email with community links sent
- [ ] Error handling works

## 不要做
- No wallet address collection
- No KYC/identity verification
- No token allocation promises
