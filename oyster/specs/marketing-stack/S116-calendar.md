---
task_id: S116-calendar
project: marketing-stack
priority: 4
estimated_minutes: 20
depends_on: [S114-content]
modifies: ["oyster/social/common/calendars/worldglasses-2week.json"]
executor: glm
---
## 目标
Create 2-week social calendar for WorldGlasses with scheduled posts across platforms, balanced content mix

## 约束
- 14 days, 2-3 posts per day
- Platforms: Twitter, Bluesky, LinkedIn, HackerNews (mention)
- Content mix: 40% tech features, 30% use cases, 20% industry news, 10% community
- Post times: 9am, 1pm, 7pm
- Weekday focus (B2B/tech audience)

## 验收标准
- [ ] worldglasses-2week.json calendar created
- [ ] 30+ posts scheduled over 14 days
- [ ] Content mix matches requirements
- [ ] Tech-focused messaging
- [ ] Platform distribution appropriate
- [ ] Calendar loads into queue system

## 不要做
- No consumer marketing tone
- No over-hyping vaporware
- No NDA-violating tech details
