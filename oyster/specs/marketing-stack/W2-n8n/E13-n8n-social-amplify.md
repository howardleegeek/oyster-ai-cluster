---
task_id: E13-n8n-social-amplify
project: marketing-stack
priority: 2
estimated_minutes: 25
depends_on: [B02, D01, D02, D03, D04]
modifies: ["n8n-workflows/social-amplify.json"]
executor: glm
---
## 目标
Create n8n workflow: new content published webhook → repost across all platforms (Twitter, Bluesky, LinkedIn, Discord)

## 约束
- Use n8n Webhook trigger for content published
- Call all platform adapters in parallel
- Adapt content format per platform (character limits, etc.)
- Log results per platform
- Continue even if one platform fails
- Return summary of successes/failures

## 验收标准
- [ ] Workflow JSON created in n8n-workflows/
- [ ] Webhook accepts content + metadata
- [ ] Calls Twitter, Bluesky, LinkedIn, Discord adapters
- [ ] Adapts content format per platform
- [ ] Runs platform posts in parallel
- [ ] Logs results per platform
- [ ] Returns summary status
- [ ] Import to n8n instance successful

## 不要做
- Don't build content transformation engine
- Don't add platform-specific optimizations
- Don't implement retry logic beyond n8n defaults
