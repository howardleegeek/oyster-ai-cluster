---
task_id: I-af-2-seo
project: marketing-stack
priority: 4
estimated_minutes: 15
depends_on: [B12-serpbear-deploy]
modifies: ["oyster/infra/serpbear-config/agentforge-keywords.json"]
executor: glm
---
## 目标
Set up SerpBear keyword tracking for AgentForge with 50 target keywords and verify daily rank tracking runs

## 约束
- Keywords: AI agent builder, agent framework, LLM agents, autonomous agents, etc.
- 50 keywords covering: agent development, frameworks, LangChain alternatives
- Track Google rankings
- Daily check schedule
- Alert on rank drops > 5 positions

## 验收标准
- [ ] agentforge-keywords.json created with 50 keywords
- [ ] Keywords added to SerpBear via API
- [ ] Initial rankings captured
- [ ] Daily cron job configured
- [ ] Dashboard shows tracking active

## 不要做
- No documentation SEO yet
- No framework comparison SEO
- No tutorial SEO
