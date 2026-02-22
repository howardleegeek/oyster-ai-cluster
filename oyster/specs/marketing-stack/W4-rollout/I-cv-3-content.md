---
task_id: I-cv-3-content
project: marketing-stack
priority: 4
estimated_minutes: 20
depends_on: [A02-persona-system, D01-templates-create, D02-templates-test]
modifies: ["oyster/social/common/campaigns/clawvision-launch.json"]
executor: glm
---
## 目标
Create initial content campaign for ClawVision: 5 social posts (2 Twitter, 2 Bluesky, 1 LinkedIn) using personas and templates

## 约束
- Use TechInnovator and DeveloperAdvocate personas
- Templates: api_announcement, use_case, technical_demo
- Topics: vision API capabilities, integration ease, real-world applications
- Queue posts for next 7 days
- Developer-focused audience

## 验收标准
- [ ] clawvision-launch.json campaign file created
- [ ] 5 posts generated using templates + personas
- [ ] Posts queued in unified queue
- [ ] Content emphasizes developer experience
- [ ] Hashtags include #ComputerVision #API #AI
- [ ] CTAs drive to API docs/playground

## 不要做
- No pricing discussion yet
- No model comparison
- No accuracy claims without benchmarks
