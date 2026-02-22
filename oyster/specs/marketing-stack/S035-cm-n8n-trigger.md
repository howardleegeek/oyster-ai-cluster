---
task_id: S035-cm-n8n-trigger
project: marketing-stack
priority: 2
estimated_minutes: 15
depends_on: [B02]
modifies: ["clawmarketing/backend/routers/campaigns.py"]
executor: glm
---
## 目标
Add n8n webhook trigger to ClawMarketing campaign router - when campaign launches, POST to n8n webhook

## 约束
- Add POST /campaigns/{id}/launch endpoint
- Trigger n8n webhook with campaign data
- Use n8n webhook URL from config
- Include campaign content, platforms, schedule
- Return launch status

## 验收标准
- [ ] POST /campaigns/{id}/launch endpoint implemented
- [ ] POSTs to n8n webhook on launch
- [ ] Sends campaign content, platforms, schedule
- [ ] Returns launch status
- [ ] Error handling for webhook failures
- [ ] pytest tests/backend/routers/test_campaigns.py passes

## 不要做
- Don't build campaign scheduler (n8n handles)
- Don't add approval workflow yet
- Don't implement platform posting directly
