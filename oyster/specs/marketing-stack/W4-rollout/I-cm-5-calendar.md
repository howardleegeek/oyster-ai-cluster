---
task_id: I-cm-5-calendar
project: marketing-stack
priority: 4
estimated_minutes: 20
depends_on: [I-cm-3-content]
modifies: ["oyster/social/common/calendars/clawmarketing-2week.json"]
executor: glm
---
## 目标
Create 2-week social calendar for ClawMarketing with scheduled posts across platforms, balanced content mix

## 约束
- 14 days, 2-3 posts per day
- Platforms: Twitter, Bluesky, LinkedIn
- Content mix: 40% original, 30% engagement, 20% educational, 10% promotional
- Post times: 9am, 1pm, 5pm (optimal engagement)
- No weekend posts unless high-priority

## 验收标准
- [ ] clawmarketing-2week.json calendar created
- [ ] 30+ posts scheduled over 14 days
- [ ] Content mix matches requirements
- [ ] Posts scheduled at optimal times
- [ ] Platform distribution balanced
- [ ] Can load calendar into queue system

## 不要做
- No auto-generate all content (use existing + templates)
- No duplicate posts across platforms
- No off-brand content
