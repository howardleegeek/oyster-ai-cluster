---
task_id: S098-seo
project: marketing-stack
priority: 4
estimated_minutes: 15
depends_on: [B12-serpbear-deploy]
modifies: ["oyster/infra/serpbear-config/gem-keywords.json"]
executor: glm
---
## 目标
Set up SerpBear keyword tracking for GEM Platform with 50 target keywords and verify daily rank tracking runs

## 约束
- Keywords: AI agents platform, workflow automation, enterprise AI, multi-agent systems, etc.
- 50 keywords covering: platform features, AI categories, competitor terms
- Track Google rankings
- Daily check schedule
- Alert on rank drops > 5 positions

## 验收标准
- [ ] gem-keywords.json created with 50 keywords
- [ ] Keywords added to SerpBear via API
- [ ] Initial rankings captured
- [ ] Daily cron job configured
- [ ] Dashboard shows tracking active

## 不要做
- No enterprise-specific SEO yet
- No technical documentation SEO
- No API reference SEO
