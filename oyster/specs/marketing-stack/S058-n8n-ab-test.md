---
task_id: S058-n8n-ab-test
project: marketing-stack
priority: 2
estimated_minutes: 20
depends_on: [B02, B04]
modifies: ["n8n-workflows/ab-test-automation.json"]
executor: glm
---
## 目标
Create n8n workflow: A/B test results from PostHog → determine winner based on metrics → auto-scale winner variant

## 约束
- Use n8n Webhook trigger for test completion
- Query PostHog for variant metrics
- Compare conversion rates with statistical significance
- Declare winner if p-value < 0.05
- Update config to scale winner to 100%
- Send notification with results

## 验收标准
- [ ] Workflow JSON created in n8n-workflows/
- [ ] Webhook receives test completion signal
- [ ] Fetches metrics from PostHog for variants
- [ ] Calculates statistical significance
- [ ] Declares winner if significant
- [ ] Updates variant allocation
- [ ] Sends notification with results
- [ ] Import to n8n instance successful

## 不要做
- Don't build statistical testing from scratch (use library)
- Don't auto-deploy code changes
- Don't implement multivariate testing yet
