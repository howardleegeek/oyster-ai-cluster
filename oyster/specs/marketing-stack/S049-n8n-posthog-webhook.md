---
task_id: S049-n8n-posthog-webhook
project: marketing-stack
priority: 2
estimated_minutes: 20
depends_on: [B02, B04]
modifies: ["n8n-workflows/posthog-events.json"]
executor: glm
---
## 目标
Create n8n workflow: PostHog event webhook → process event data → route to CRM/alert/dashboard based on event type

## 约束
- Use n8n Webhook trigger for PostHog events
- Parse PostHog event payload
- Route based on event type (conversion/error/milestone)
- Send to appropriate destination (Twenty CRM/Slack/Directus)
- Log all processed events

## 验收标准
- [ ] Workflow JSON created in n8n-workflows/
- [ ] Webhook receives PostHog events
- [ ] Parses event type and properties
- [ ] Routes conversions to CRM
- [ ] Routes errors to Slack alerts
- [ ] Logs all events to Directus
- [ ] Import to n8n instance successful

## 不要做
- Don't build custom analytics engine
- Don't store events beyond logging
- Don't implement real-time dashboard yet
