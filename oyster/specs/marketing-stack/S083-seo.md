---
task_id: S083-seo
project: marketing-stack
priority: 4
estimated_minutes: 15
depends_on: [B12-serpbear-deploy]
modifies: ["oyster/infra/serpbear-config/clawmarketing-keywords.json"]
executor: glm
---
## 目标
Set up SerpBear keyword tracking for ClawMarketing with 50 target keywords and verify daily rank tracking runs

## 约束
- Keywords: marketing automation, social media management, content calendar, etc.
- 50 keywords total covering: brand, product features, competitors
- Track Google rankings
- Daily check schedule
- Alert on rank drops > 5 positions

## 验收标准
- [ ] clawmarketing-keywords.json created with 50 keywords
- [ ] Keywords added to SerpBear via API
- [ ] Initial rankings captured
- [ ] Daily cron job configured
- [ ] Can view rankings in SerpBear dashboard

## 不要做
- No paid search tracking
- No backlink monitoring yet
- No competitor rank comparison
