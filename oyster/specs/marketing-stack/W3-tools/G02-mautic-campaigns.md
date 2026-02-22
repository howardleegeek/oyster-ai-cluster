---
task_id: G02-mautic-campaigns
project: marketing-stack
priority: 3
estimated_minutes: 30
depends_on: [G01-mautic-deploy]
modifies: ["oyster/social/common/mautic_campaigns/"]
executor: glm
---
## 目标
Configure 4 Mautic email campaigns: welcome series, product launch, re-engagement, newsletter digest

## 约束
- Welcome: 3 emails over 7 days (day 1, 3, 7)
- Product launch: announcement + 3-day follow-up
- Re-engagement: triggered for 30+ days inactive
- Newsletter: weekly digest on Mondays
- Use Mautic API for programmatic setup
- Store campaign templates in mautic_campaigns/

## 验收标准
- [ ] All 4 campaigns created in Mautic
- [ ] Python script to initialize campaigns via API
- [ ] Test contacts receive welcome series correctly
- [ ] Campaigns can be triggered programmatically
- [ ] Documentation in mautic_campaigns/README.md

## 不要做
- No manual UI configuration required
- No hardcoded email content (use templates)
- No sending to real contact lists yet
