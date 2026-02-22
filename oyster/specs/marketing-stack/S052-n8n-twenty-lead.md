---
task_id: S052-n8n-twenty-lead
project: marketing-stack
priority: 2
estimated_minutes: 15
depends_on: [B02, B10]
modifies: ["n8n-workflows/twenty-lead-sync.json"]
executor: glm
---
## 目标
Create n8n workflow: new lead data webhook → create or update contact in Twenty CRM via GraphQL

## 约束
- Use n8n Webhook trigger for new leads
- Call Twenty GraphQL API to create/update
- Match contacts by email to avoid duplicates
- Update existing contacts with new data
- Return created/updated contact ID

## 验收标准
- [ ] Workflow JSON created in n8n-workflows/
- [ ] Webhook accepts lead data (name, email, source)
- [ ] Queries Twenty for existing contact by email
- [ ] Creates new contact if not exists
- [ ] Updates existing contact if found
- [ ] Returns contact ID
- [ ] Import to n8n instance successful

## 不要做
- Don't build lead scoring logic
- Don't add enrichment services yet
- Don't implement duplicate detection beyond email
