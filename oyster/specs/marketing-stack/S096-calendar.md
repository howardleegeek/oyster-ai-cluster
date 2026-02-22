---
task_id: S096-calendar
project: marketing-stack
priority: 4
estimated_minutes: 20
depends_on: [S094-content]
modifies: ["oyster/social/common/calendars/clawvision-2week.json"]
executor: glm
---
## 目标
Create 2-week social calendar for ClawVision with scheduled posts across platforms, balanced content mix

## 约束
- 14 days, 2-3 posts per day
- Platforms: Twitter, HackerNews (mention), DevTo (mention), LinkedIn
- Content mix: 40% tutorials, 30% use cases, 20% API updates, 10% community
- Post times: 10am, 2pm, 6pm
- Developer-focused timing

## 验收标准
- [ ] clawvision-2week.json calendar created
- [ ] 30+ posts scheduled over 14 days
- [ ] Content mix matches requirements
- [ ] Technical but accessible tone
- [ ] Platform distribution appropriate
- [ ] Calendar loads into queue system

## 不要做
- No marketing fluff
- No non-technical hype
- No unverified performance claims
