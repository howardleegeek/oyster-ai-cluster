---
task_id: E07-n8n-serpbear-alert
project: marketing-stack
priority: 2
estimated_minutes: 15
depends_on: [B02, B12]
modifies: ["n8n-workflows/serpbear-monitor.json"]
executor: glm
---
## 目标
Create n8n workflow: daily cron polls SerpBear API for rank changes → alerts if any keyword drops >5 positions

## 约束
- Use n8n Cron trigger (daily at 9am)
- Poll SerpBear API for all tracked keywords
- Compare against previous day ranks
- Alert via email/Slack if drop >5 positions
- Store rank history in Directus

## 验收标准
- [ ] Workflow JSON created in n8n-workflows/
- [ ] Cron trigger runs daily at 9am
- [ ] Fetches current ranks from SerpBear
- [ ] Compares with previous ranks
- [ ] Sends alert if drop >5 positions
- [ ] Stores rank history
- [ ] Import to n8n instance successful

## 不要做
- Don't build rank tracking from scratch
- Don't add keyword research features
- Don't implement competitor tracking yet
