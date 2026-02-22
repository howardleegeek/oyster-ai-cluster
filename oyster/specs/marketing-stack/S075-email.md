---
task_id: S075-email
project: marketing-stack
priority: 4
estimated_minutes: 15
depends_on: [B08-listmonk-deploy]
modifies: ["oyster/products/agent-forge/web/src/components/EmailSignup.tsx"]
executor: glm
---
## 目标
Create email signup form for AgentForge landing page, connect to Listmonk list, welcome email template

## 约束
- React component: EmailSignup.tsx
- POST to Listmonk API
- List name: agentforge-developers
- Double opt-in enabled
- Welcome email: quickstart guide + GitHub star ask
- Source tag: landing_page

## 验收标准
- [ ] EmailSignup.tsx component created
- [ ] Form validates email
- [ ] Success confirmation displayed
- [ ] Subscriber added to Listmonk
- [ ] Welcome email with quickstart sent
- [ ] Error handling works

## 不要做
- No GitHub OAuth signup
- No immediate contribution asks
- No enterprise sales pitch
