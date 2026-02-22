---
task_id: I-pf-3-content
project: marketing-stack
priority: 4
estimated_minutes: 20
depends_on: [A02-persona-system, D01-templates-create, D02-templates-test]
modifies: ["oyster/social/common/campaigns/getpuffy-launch.json"]
executor: glm
---
## 目标
Create initial content campaign for getPuffy: 5 social posts (2 Twitter, 2 Bluesky, 1 LinkedIn) using personas and templates

## 约束
- Use LifestyleBrand and SustainabilityAdvocate personas
- Templates: product_launch, lifestyle_story, sustainability_story
- Topics: premium quality, sustainable materials, winter essentials
- Queue posts for next 7 days
- Lifestyle/fashion angle

## 验收标准
- [ ] getpuffy-launch.json campaign file created
- [ ] 5 posts generated using templates + personas
- [ ] Posts queued in unified queue
- [ ] Content emphasizes quality + sustainability
- [ ] Hashtags include #SustainableFashion #WinterStyle #PufferJacket
- [ ] CTAs drive to product page

## 不要做
- No fast fashion comparison
- No greenwashing claims
- No unrealistic lifestyle imagery
