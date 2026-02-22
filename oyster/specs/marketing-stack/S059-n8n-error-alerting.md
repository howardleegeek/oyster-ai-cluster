---
task_id: S059-n8n-error-alerting
project: marketing-stack
priority: 2
estimated_minutes: 15
depends_on: [B02]
modifies: ["n8n-workflows/error-router.json"]
executor: glm
---
## 目标
Create n8n workflow: error webhook from any tool → classify severity → alert appropriate channel (Slack/email/PagerDuty)

## 约束
- Use n8n Webhook trigger for error events
- Parse error level (debug/info/warning/error/critical)
- Route based on severity: debug→log, warning→Slack, error→email, critical→PagerDuty
- Include error context and source tool
- Rate limit alerts to avoid spam

## 验收标准
- [ ] Workflow JSON created in n8n-workflows/
- [ ] Webhook accepts error events with level
- [ ] Classifies severity correctly
- [ ] Routes to appropriate channel
- [ ] Includes error context in alerts
- [ ] Rate limits duplicate errors
- [ ] Import to n8n instance successful

## 不要做
- Don't build error tracking system
- Don't add error resolution automation
- Don't implement on-call rotation logic
