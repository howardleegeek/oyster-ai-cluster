---
task_id: S048-n8n-postiz
project: marketing-stack
priority: 2
estimated_minutes: 15
depends_on: [B02]
modifies: ["n8n-workflows/postiz-schedule.json"]
executor: glm
---
## 目标
Create n8n workflow: content ready webhook → schedule on Postiz → confirm scheduling

## 约束
- Use n8n Webhook trigger for content ready signal
- Call Postiz API to schedule post
- Accept platform, content, schedule_time in webhook
- Return scheduled post ID
- Handle Postiz API authentication

## 验收标准
- [ ] Workflow JSON created in n8n-workflows/
- [ ] Webhook accepts content + scheduling params
- [ ] Schedules post via Postiz API
- [ ] Returns scheduled post ID
- [ ] Logs scheduling confirmation
- [ ] Import to n8n instance successful

## 不要做
- Don't build content calendar UI
- Don't add approval workflow yet
- Don't implement bulk scheduling
