---
task_id: S078-seo
project: marketing-stack
priority: 4
estimated_minutes: 15
depends_on: [B12-serpbear-deploy]
modifies: ["oyster/infra/serpbear-config/clawglasses-keywords.json"]
executor: glm
---
## 目标
Set up SerpBear keyword tracking for ClawGlasses with 50 target keywords and verify daily rank tracking runs

## 约束
- Keywords: custom eyeglasses, personalized glasses, prescription glasses online, etc.
- 50 keywords covering: product types, customization, online eyewear, competitors
- Track Google rankings
- Daily check schedule
- Alert on rank drops > 5 positions

## 验收标准
- [ ] clawglasses-keywords.json created with 50 keywords
- [ ] Keywords added to SerpBear via API
- [ ] Initial rankings captured
- [ ] Daily cron job configured
- [ ] Dashboard shows tracking active

## 不要做
- No prescription-specific SEO yet
- No local SEO (no physical stores)
- No medical SEO compliance
