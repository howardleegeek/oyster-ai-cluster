---
task_id: S047-n8n-listmonk
project: marketing-stack
priority: 2
estimated_minutes: 15
depends_on: [B02, B07]
modifies: ["n8n-workflows/listmonk-campaign.json"]
executor: glm
---
## 目标
Create n8n workflow: webhook receives campaign request → calls Listmonk API to send campaign → logs result

## 约束
- Use n8n Webhook trigger node
- Call Listmonk API directly (REST)
- Accept list ID, subject, content in webhook
- Log campaign send status
- Return campaign ID to caller

## 验收标准
- [ ] Workflow JSON created in n8n-workflows/
- [ ] Webhook accepts campaign parameters
- [ ] Creates campaign via Listmonk API
- [ ] Sends campaign to specified list
- [ ] Logs campaign ID and status
- [ ] Import to n8n instance successful

## 不要做
- Don't build template management
- Don't add subscriber sync
- Don't implement A/B testing yet
