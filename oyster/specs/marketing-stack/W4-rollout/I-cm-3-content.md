---
task_id: I-cm-3-content
project: marketing-stack
priority: 4
estimated_minutes: 20
depends_on: [A02-persona-system, D01-templates-create, D02-templates-test]
modifies: ["oyster/social/common/campaigns/clawmarketing-launch.json"]
executor: glm
---
## 目标
Create initial content campaign for ClawMarketing: 5 social posts (2 Twitter, 2 Bluesky, 1 LinkedIn) using personas and templates, queue via common queue

## 约束
- Use TechInnovator and MarketingMaven personas
- Templates: product_announcement, feature_highlight, use_case
- Content topics: launch announcement, automation benefits, integration features
- Queue posts for next 7 days
- Include relevant hashtags and CTAs

## 验收标准
- [ ] clawmarketing-launch.json campaign file created
- [ ] 5 posts generated using templates + personas
- [ ] Posts queued in unified queue
- [ ] Content diverse (not repetitive)
- [ ] Hashtags and CTAs appropriate
- [ ] Can preview posts before publishing

## 不要做
- No auto-publish yet
- No paid promotion
- No A/B testing variants
