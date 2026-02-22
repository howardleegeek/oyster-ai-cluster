---
task_id: E11-n8n-welcome-sequence
project: marketing-stack
priority: 2
estimated_minutes: 20
depends_on: [B02, B08]
modifies: ["n8n-workflows/welcome-sequence.json"]
executor: glm
---
## 目标
Create n8n workflow: new Listmonk subscriber → send welcome email day 0 → follow-up day 3 → product intro day 7

## 约束
- Use n8n Webhook trigger for new subscriber
- Use Wait nodes for delays (3 days, 7 days)
- Send 3 emails via Listmonk API
- Track sequence completion
- Allow unsubscribe at any step

## 验收标准
- [ ] Workflow JSON created in n8n-workflows/
- [ ] Webhook receives new subscriber data
- [ ] Sends welcome email immediately
- [ ] Waits 3 days then sends follow-up
- [ ] Waits 4 more days then sends product intro
- [ ] Respects unsubscribe status
- [ ] Import to n8n instance successful

## 不要做
- Don't build email template editor
- Don't add complex segmentation
- Don't implement behavioral triggers yet
