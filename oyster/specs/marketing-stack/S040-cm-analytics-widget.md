---
task_id: S040-cm-analytics-widget
project: marketing-stack
priority: 2
estimated_minutes: 25
depends_on: [F01, F02]
modifies: ["clawmarketing/frontend/src/components/AnalyticsWidget.tsx"]
executor: glm
---
## 目标
Add unified analytics dashboard widget to ClawMarketing frontend - combine PostHog + Plausible data in single chart

## 约束
- Create AnalyticsWidget.tsx component
- Fetch data from F01 and F02 endpoints
- Display combined chart (Chart.js or Recharts)
- Show events (PostHog) + pageviews (Plausible)
- Time range selector (7d/30d/90d)

## 验收标准
- [ ] AnalyticsWidget.tsx component created
- [ ] Fetches PostHog and Plausible data
- [ ] Displays combined time-series chart
- [ ] Time range selector works (7d/30d/90d)
- [ ] Loading and error states handled
- [ ] Component renders in dashboard

## 不要做
- Don't build custom charting library
- Don't add drill-down features yet
- Don't implement export functionality
