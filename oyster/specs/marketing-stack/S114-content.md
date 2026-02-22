---
task_id: S114-content
project: marketing-stack
priority: 4
estimated_minutes: 20
depends_on: [A02-persona-system, D01-templates-create, D02-templates-test]
modifies: ["oyster/social/common/campaigns/worldglasses-launch.json"]
executor: glm
---
## 目标
Create initial content campaign for WorldGlasses: 5 social posts (2 Twitter, 2 Bluesky, 1 LinkedIn) using personas and templates

## 约束
- Use TechInnovator and FutureThinker personas
- Templates: tech_announcement, innovation_story, use_case
- Topics: AR capabilities, spatial computing, real-world applications
- Queue posts for next 7 days
- Tech-focused audience

## 验收标准
- [ ] worldglasses-launch.json campaign file created
- [ ] 5 posts generated using templates + personas
- [ ] Posts queued in unified queue
- [ ] Content emphasizes innovation/tech
- [ ] Hashtags include #AR #SpatialComputing #SmartGlasses
- [ ] CTAs drive to demo signup

## 不要做
- No product comparison yet
- No pricing discussion
- No competitor attacks
