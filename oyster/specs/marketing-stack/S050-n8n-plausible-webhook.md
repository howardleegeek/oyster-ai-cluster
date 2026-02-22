---
task_id: S050-n8n-plausible-webhook
project: marketing-stack
priority: 2
estimated_minutes: 15
depends_on: [B02, B06]
modifies: ["n8n-workflows/plausible-goals.json"]
executor: glm
---
## 目标
Create n8n workflow: Plausible goal completion webhook → process goal data → trigger action based on goal type

## 约束
- Use n8n Webhook trigger for Plausible goals
- Parse goal name and properties
- Trigger actions (send thank you email, update CRM, alert team)
- Log goal completions
- Handle multiple goal types

## 验收标准
- [ ] Workflow JSON created in n8n-workflows/
- [ ] Webhook receives Plausible goal events
- [ ] Parses goal type and visitor data
- [ ] Triggers appropriate action per goal
- [ ] Logs goals to tracking system
- [ ] Import to n8n instance successful

## 不要做
- Don't build goal configuration UI
- Don't add complex attribution logic
- Don't implement funnel analysis yet
