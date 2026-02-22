---
task_id: S60-analytics-dashboard
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - frontend/src/pages/Analytics.tsx
---

## 目标
Analytics 页面连接真实 API

## 具体改动
- /api/v2/analytics/summary - 总览数据
- /api/v2/analytics/content - 内容分析
- /api/v2/analytics/campaigns - 战役分析
- /api/v2/trending - 热门话题

## 验收标准
- [ ] 图表显示真实数据
- [ ] 可切换时间范围
