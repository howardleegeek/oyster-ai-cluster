---
task_id: S046-n8n-bluesky
project: marketing-stack
priority: 2
estimated_minutes: 15
depends_on: [B02, D02]
modifies: ["n8n-workflows/bluesky-post.json"]
executor: glm
---
## 目标
Create n8n workflow: webhook receives post request → calls bluesky adapter → logs result

## 约束
- Use n8n Webhook trigger node
- Call bluesky adapter via HTTP Request node
- Log execution results
- Return webhook response with status
- Mirror twitter workflow structure

## 验收标准
- [ ] Workflow JSON created in n8n-workflows/
- [ ] Webhook accepts POST with content
- [ ] Calls bluesky adapter endpoint
- [ ] Logs result with timestamp
- [ ] Returns appropriate status codes
- [ ] Import to n8n instance successful

## 不要做
- Don't duplicate twitter logic exactly
- Don't add platform-specific features yet
- Don't implement content transformation
