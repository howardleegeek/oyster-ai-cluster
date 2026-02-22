---
task_id: I-wg-2-seo
project: marketing-stack
priority: 4
estimated_minutes: 15
depends_on: [B12-serpbear-deploy]
modifies: ["oyster/infra/serpbear-config/worldglasses-keywords.json"]
executor: glm
---
## 目标
Set up SerpBear keyword tracking for WorldGlasses with 50 target keywords and verify daily rank tracking runs

## 约束
- Keywords: AR glasses, smart glasses, wearable AR, spatial computing, etc.
- 50 keywords covering: tech category, features, competitors (Orion, Ray-Ban Meta)
- Track Google rankings
- Daily check schedule
- Alert on rank drops > 5 positions

## 验收标准
- [ ] worldglasses-keywords.json created with 50 keywords
- [ ] Keywords added to SerpBear via API
- [ ] Initial rankings captured
- [ ] Daily cron job configured
- [ ] Dashboard shows tracking active

## 不要做
- No product comparison pages yet
- No tech spec SEO
- No video SEO
