---
task_id: S076-calendar
project: marketing-stack
priority: 4
estimated_minutes: 20
depends_on: [S074-content]
modifies: ["oyster/social/common/calendars/agentforge-2week.json"]
executor: glm
---
## 目标
Create 2-week social calendar for AgentForge with scheduled posts across platforms, balanced content mix

## 约束
- 14 days, 2-3 posts per day
- Platforms: Twitter, HackerNews (mention), DevTo (mention), LinkedIn, Reddit (r/LangChain)
- Content mix: 40% tutorials/tips, 30% features/releases, 20% community, 10% ecosystem
- Post times: 10am, 2pm, 8pm
- Weekday focus with light weekend

## 验收标准
- [ ] agentforge-2week.json calendar created
- [ ] 30+ posts scheduled over 14 days
- [ ] Content mix matches requirements
- [ ] Developer-friendly, technical tone
- [ ] Platform distribution appropriate
- [ ] Calendar loads into queue system

## 不要做
- No marketing speak
- No closed-source promotions
- No aggressive growth hacking
