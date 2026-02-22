---
task_id: I-cg-3-content
project: marketing-stack
priority: 4
estimated_minutes: 20
depends_on: [A02-persona-system, D01-templates-create, D02-templates-test]
modifies: ["oyster/social/common/campaigns/clawglasses-launch.json"]
executor: glm
---
## 目标
Create initial content campaign for ClawGlasses: 5 social posts (2 Twitter, 2 Bluesky, 1 LinkedIn) using personas and templates

## 约束
- Use CreativeStoryteller and LifestyleBrand personas
- Templates: product_showcase, style_guide, customer_story
- Topics: custom designs, style personalization, quality craftsmanship
- Queue posts for next 7 days
- Fashion/lifestyle angle

## 验收标准
- [ ] clawglasses-launch.json campaign file created
- [ ] 5 posts generated using templates + personas
- [ ] Posts queued in unified queue
- [ ] Content emphasizes style + personalization
- [ ] Hashtags include #Eyewear #CustomGlasses #Fashion
- [ ] CTAs drive to customization tool

## 不要做
- No prescription discussion
- No medical claims
- No competitor price comparison
