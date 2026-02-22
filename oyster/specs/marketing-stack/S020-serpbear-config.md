---
task_id: S020-serpbear-config
project: marketing-stack
priority: 1
estimated_minutes: 30
depends_on: ["S019-serpbear-deploy"]
modifies: ["~/.oyster-keys/serpbear/domains.json", "~/.oyster-keys/serpbear/keywords.json"]
executor: glm
---

## 目标
Configure SerpBear with 6 product domains, 50 keywords per domain, and Google Search Console integration

## 约束
- Domains: clawmarketing.com, clawphones.com, worldglasses.com, getpuffy.com, oysterrepublic.com, agentforge.dev
- Keywords per domain: 50 relevant keywords (research using domain + product niche)
- Keyword sources: Google Trends, competitor analysis, product-specific terms
- Search engine: Google (US)
- Tracking frequency: Daily
- Connect Google Search Console API (use ~/.oyster-keys/gcp/service-account.json)
- Save config to ~/.oyster-keys/serpbear/

## 验收标准
- [ ] 6 domains added to SerpBear
- [ ] 50 keywords per domain (300 total)
- [ ] Keywords saved to ~/.oyster-keys/serpbear/keywords.json
- [ ] JSON format: {"domain": ["keyword1", "keyword2", ...]}
- [ ] Google Search Console connected and verified
- [ ] First rank check completed for all keywords
- [ ] Daily tracking schedule configured

## 不要做
- 不要设置 email alerts (后续 n8n 集成)
- 不要创建 custom reports
- 不要添加 competitors (后续)
- 不要修改 docker-compose
