---
task_id: S111-calendar
project: marketing-stack
priority: 4
estimated_minutes: 20
depends_on: [S109-content]
modifies: ["oyster/social/common/calendars/getpuffy-2week.json"]
executor: glm
---
## 目标
Create 2-week social calendar for getPuffy with scheduled posts across platforms, balanced content mix

## 约束
- 14 days, 2-3 posts per day
- Platforms: Twitter, Instagram (mention), Pinterest (mention), TikTok (mention)
- Content mix: 40% product/lifestyle, 30% sustainability, 20% styling tips, 10% promo
- Post times: 10am, 2pm, 8pm
- Weekend posts OK (consumer product)

## 验收标准
- [ ] getpuffy-2week.json calendar created
- [ ] 30+ posts scheduled over 14 days
- [ ] Content mix matches requirements
- [ ] Lifestyle/fashion focused
- [ ] Platform distribution appropriate
- [ ] Calendar loads into queue system

## 不要做
- No body image issues
- No unsustainable lifestyle promotion
- No fake sustainability claims
