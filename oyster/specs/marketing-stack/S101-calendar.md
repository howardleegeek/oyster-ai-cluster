---
task_id: S101-calendar
project: marketing-stack
priority: 4
estimated_minutes: 20
depends_on: [S099-content]
modifies: ["oyster/social/common/calendars/gem-2week.json"]
executor: glm
---
## 目标
Create 2-week social calendar for GEM Platform with scheduled posts across platforms, balanced content mix

## 约束
- 14 days, 2-3 posts per day
- Platforms: Twitter, LinkedIn, HackerNews (mention)
- Content mix: 40% platform features, 30% use cases, 20% thought leadership, 10% community
- Post times: 9am, 1pm, 5pm
- Weekday focus (B2B audience)

## 验收标准
- [ ] gem-2week.json calendar created
- [ ] 30+ posts scheduled over 14 days
- [ ] Content mix matches requirements
- [ ] Enterprise/professional tone
- [ ] Platform distribution appropriate
- [ ] Calendar loads into queue system

## 不要做
- No overpromising capabilities
- No buzzword bingo
- No hard sales pitches
