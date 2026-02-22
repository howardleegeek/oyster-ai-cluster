---
task_id: S039-cm-twenty-sync
project: marketing-stack
priority: 2
estimated_minutes: 25
depends_on: [B10]
modifies: ["clawmarketing/backend/routers/accounts.py"]
executor: glm
---
## 目标
Add Twenty CRM sync to ClawMarketing accounts router - bidirectional contact sync via Twenty GraphQL API

## 约束
- Add POST /accounts/sync/twenty endpoint
- Use Twenty GraphQL API for queries and mutations
- Sync contacts bidirectionally (CM ↔ Twenty)
- Match by email to avoid duplicates
- Update modified_at timestamps
- Return sync summary (created/updated counts)

## 验收标准
- [ ] POST /accounts/sync/twenty endpoint implemented
- [ ] Queries Twenty for contacts via GraphQL
- [ ] Creates/updates contacts in both systems
- [ ] Matches by email to avoid duplicates
- [ ] Returns sync summary
- [ ] pytest tests/backend/routers/test_accounts.py passes

## 不要做
- Don't build full CRM features in CM
- Don't add conflict resolution yet
- Don't implement field mapping configuration
