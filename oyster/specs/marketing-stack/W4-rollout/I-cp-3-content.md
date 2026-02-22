---
task_id: I-cp-3-content
project: marketing-stack
priority: 4
estimated_minutes: 20
depends_on: [A02-persona-system, D01-templates-create, D02-templates-test]
modifies: ["oyster/social/common/campaigns/clawphones-launch.json"]
executor: glm
---
## 目标
Create initial content campaign for ClawPhones: 5 social posts (2 Twitter, 2 Bluesky, 1 LinkedIn) using personas and templates

## 约束
- Use CreativeStoryteller and TechInnovator personas
- Templates: product_showcase, customer_story, design_inspiration
- Topics: AI customization, unique designs, personalization benefits
- Queue posts for next 7 days
- Visual-focused content (mention images)

## 验收标准
- [ ] clawphones-launch.json campaign file created
- [ ] 5 posts generated using templates + personas
- [ ] Posts queued in unified queue
- [ ] Content emphasizes visual/design aspect
- [ ] Hashtags include #CustomPhoneCases #AIDesign
- [ ] CTAs drive to product page

## 不要做
- No actual image generation yet
- No influencer outreach
- No user-generated content
