---
task_id: S088-seo
project: marketing-stack
priority: 4
estimated_minutes: 15
depends_on: [B12-serpbear-deploy]
modifies: ["oyster/infra/serpbear-config/clawphones-keywords.json"]
executor: glm
---
## 目标
Set up SerpBear keyword tracking for ClawPhones with 50 target keywords and verify daily rank tracking runs

## 约束
- Keywords: custom phone cases, personalized phone accessories, AI phone design, etc.
- 50 keywords covering: product features, design keywords, competitor terms
- Track Google rankings
- Daily check schedule
- Alert on rank drops > 5 positions

## 验收标准
- [ ] clawphones-keywords.json created with 50 keywords
- [ ] Keywords added to SerpBear via API
- [ ] Initial rankings captured
- [ ] Daily cron job configured
- [ ] Dashboard shows tracking active

## 不要做
- No paid search tracking
- No product-specific landing pages yet
- No local SEO
