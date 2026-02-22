---
task_id: S108-seo
project: marketing-stack
priority: 4
estimated_minutes: 15
depends_on: [B12-serpbear-deploy]
modifies: ["oyster/infra/serpbear-config/getpuffy-keywords.json"]
executor: glm
---
## 目标
Set up SerpBear keyword tracking for getPuffy with 50 target keywords and verify daily rank tracking runs

## 约束
- Keywords: premium jackets, winter coats, sustainable outerwear, puffer jackets, etc.
- 50 keywords covering: product types, materials, sustainability, competitors
- Track Google rankings
- Daily check schedule
- Alert on rank drops > 5 positions

## 验收标准
- [ ] getpuffy-keywords.json created with 50 keywords
- [ ] Keywords added to SerpBear via API
- [ ] Initial rankings captured
- [ ] Daily cron job configured
- [ ] Dashboard shows tracking active

## 不要做
- No seasonal keyword rotation yet
- No product-specific landing pages
- No local SEO
