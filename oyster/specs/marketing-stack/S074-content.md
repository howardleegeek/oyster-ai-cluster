---
task_id: S074-content
project: marketing-stack
priority: 4
estimated_minutes: 20
depends_on: [A02-persona-system, D01-templates-create, D02-templates-test]
modifies: ["oyster/social/common/campaigns/agentforge-launch.json"]
executor: glm
---
## 目标
Create initial content campaign for AgentForge: 5 social posts (2 Twitter, 2 Bluesky, 1 LinkedIn) using personas and templates

## 约束
- Use DeveloperAdvocate and TechInnovator personas
- Templates: oss_announcement, tutorial_preview, technical_deep_dive
- Topics: agent framework features, developer experience, open source
- Queue posts for next 7 days
- Developer/OSS audience

## 验收标准
- [ ] agentforge-launch.json campaign file created
- [ ] 5 posts generated using templates + personas
- [ ] Posts queued in unified queue
- [ ] Content emphasizes DX + open source
- [ ] Hashtags include #AIAgents #OpenSource #LLM
- [ ] CTAs drive to GitHub + docs

## 不要做
- No framework wars
- No overpromising features
- No vendor lock-in FUD
