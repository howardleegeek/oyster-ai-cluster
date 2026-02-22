---
task_id: I-cv-2-seo
project: marketing-stack
priority: 4
estimated_minutes: 15
depends_on: [B12-serpbear-deploy]
modifies: ["oyster/infra/serpbear-config/clawvision-keywords.json"]
executor: glm
---
## 目标
Set up SerpBear keyword tracking for ClawVision with 50 target keywords and verify daily rank tracking runs

## 约束
- Keywords: AI image analysis, computer vision API, image recognition, visual AI, etc.
- 50 keywords covering: vision AI, API features, use cases, competitors
- Track Google rankings
- Daily check schedule
- Alert on rank drops > 5 positions

## 验收标准
- [ ] clawvision-keywords.json created with 50 keywords
- [ ] Keywords added to SerpBear via API
- [ ] Initial rankings captured
- [ ] Daily cron job configured
- [ ] Dashboard shows tracking active

## 不要做
- No API documentation SEO yet
- No tutorial/guide SEO
- No model-specific SEO
