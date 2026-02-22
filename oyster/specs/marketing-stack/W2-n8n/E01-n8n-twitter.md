---
task_id: E01-n8n-twitter
project: marketing-stack
priority: 2
estimated_minutes: 15
depends_on: [B02, D01]
modifies: ["n8n-workflows/twitter-post.json"]
executor: glm
---
## 目标
Create n8n workflow: webhook receives post request → calls twitter adapter → logs result

## 约束
- Use n8n Webhook trigger node
- Call twitter adapter via HTTP Request node
- Log success/failure to n8n execution log
- Return status to webhook caller
- Handle errors gracefully

## 验收标准
- [ ] Workflow JSON created in n8n-workflows/
- [ ] Webhook trigger accepts POST with content/media
- [ ] HTTP Request node calls twitter adapter endpoint
- [ ] Logs result with timestamp
- [ ] Returns 200 on success, 500 on failure
- [ ] Import to n8n instance successful

## 不要做
- Don't add complex retry logic (n8n handles this)
- Don't build scheduling (separate workflow)
- Don't add content generation
