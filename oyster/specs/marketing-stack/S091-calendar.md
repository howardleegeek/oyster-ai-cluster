---
task_id: S091-calendar
project: marketing-stack
priority: 4
estimated_minutes: 20
depends_on: [S089-content]
modifies: ["oyster/social/common/calendars/clawphones-2week.json"]
executor: glm
---
## 目标
Create 2-week social calendar for ClawPhones with scheduled posts across platforms, balanced content mix

## 约束
- 14 days, 2-3 posts per day
- Platforms: Twitter, Bluesky, Instagram (mention), LinkedIn
- Content mix: 40% design showcase, 30% customer stories, 20% tips, 10% promo
- Post times: 10am, 2pm, 6pm
- Weekend posts OK (consumer product)

## 验收标准
- [ ] clawphones-2week.json calendar created
- [ ] 30+ posts scheduled over 14 days
- [ ] Content mix matches requirements
- [ ] Visual content emphasized
- [ ] Platform distribution appropriate
- [ ] Calendar loads into queue system

## 不要做
- No duplicate designs across posts
- No generic stock images
- No competitor mentions
