---
task_id: I-or-2-seo
project: marketing-stack
priority: 4
estimated_minutes: 15
depends_on: [B12-serpbear-deploy]
modifies: ["oyster/infra/serpbear-config/oysterrepublic-keywords.json"]
executor: glm
---
## 目标
Set up SerpBear keyword tracking for OysterRepublic with 50 target keywords and verify daily rank tracking runs

## 约束
- Keywords: digital nation, cyber sovereignty, virtual citizenship, decentralized governance, etc.
- 50 keywords covering: Web3 concepts, governance, community, crypto
- Track Google rankings
- Daily check schedule
- Alert on rank drops > 5 positions

## 验收标准
- [ ] oysterrepublic-keywords.json created with 50 keywords
- [ ] Keywords added to SerpBear via API
- [ ] Initial rankings captured
- [ ] Daily cron job configured
- [ ] Dashboard shows tracking active

## 不要做
- No crypto-specific SEO yet
- No governance docs SEO
- No whitepaper SEO
