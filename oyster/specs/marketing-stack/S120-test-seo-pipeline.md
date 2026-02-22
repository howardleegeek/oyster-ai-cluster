---
task_id: S120-test-seo-pipeline
project: marketing-stack
priority: 5
estimated_minutes: 15
depends_on: [E07-serpbear-workflow]
modifies: ["oyster/tests/e2e/test_seo_pipeline.py"]
executor: glm
---
## 目标
Test SEO pipeline: SerpBear detects rank drop → n8n alert → content refresh triggered

## 约束
- Simulate rank drop in SerpBear (manual adjustment)
- Verify n8n receives webhook
- Check alert notification sent
- Trigger content refresh workflow
- Validate all steps logged

## 验收标准
- [ ] test_seo_pipeline.py created
- [ ] Rank drop simulated in SerpBear
- [ ] n8n webhook received and processed
- [ ] Alert notification verified (email/Slack)
- [ ] Content refresh workflow triggered
- [ ] pytest test_seo_pipeline.py passes

## 不要做
- No real keyword manipulation
- No actual content publishing
- No production site changes
