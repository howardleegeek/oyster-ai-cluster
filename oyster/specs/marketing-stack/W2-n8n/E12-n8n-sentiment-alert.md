---
task_id: E12-n8n-sentiment-alert
project: marketing-stack
priority: 2
estimated_minutes: 20
depends_on: [B02]
modifies: ["n8n-workflows/sentiment-monitor.json"]
executor: glm
---
## 目标
Create n8n workflow: Obsei negative sentiment webhook → alert team via Slack/email → draft suggested response

## 约束
- Use n8n Webhook trigger for Obsei sentiment events
- Filter for negative sentiment only
- Send alert to Slack with mention details
- Send email to team with full context
- Use LLM (OpenAI) to draft response suggestion
- Store alerts in Directus

## 验收标准
- [ ] Workflow JSON created in n8n-workflows/
- [ ] Webhook receives Obsei sentiment events
- [ ] Filters negative sentiment (score < -0.3)
- [ ] Sends Slack alert with mention link
- [ ] Sends email with full context
- [ ] Drafts response using LLM
- [ ] Import to n8n instance successful

## 不要做
- Don't build sentiment analysis from scratch
- Don't auto-reply to negative mentions
- Don't implement escalation rules yet
