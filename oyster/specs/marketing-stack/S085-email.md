---
task_id: S085-email
project: marketing-stack
priority: 4
estimated_minutes: 15
depends_on: [B08-listmonk-deploy]
modifies: ["oyster/products/clawmarketing/frontend/src/components/EmailSignup.tsx"]
executor: glm
---
## 目标
Create email signup form for ClawMarketing landing page, connect to Listmonk list, welcome email template

## 约束
- React component: EmailSignup.tsx
- POST to Listmonk API /api/subscribers
- List name: clawmarketing-subscribers
- Double opt-in enabled
- Welcome email: product intro + resources link
- Store subscriber source: landing_page

## 验收标准
- [ ] EmailSignup.tsx component created
- [ ] Form validates email format
- [ ] Successful submission shows confirmation
- [ ] Subscriber added to Listmonk list
- [ ] Welcome email sent automatically
- [ ] Error handling for duplicates/failures

## 不要做
- No complex fields (just email + optional name)
- No immediate campaign sending
- No unsubscribe flow yet
