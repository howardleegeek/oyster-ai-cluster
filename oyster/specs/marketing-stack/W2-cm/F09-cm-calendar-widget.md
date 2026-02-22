---
task_id: F09-cm-calendar-widget
project: marketing-stack
priority: 2
estimated_minutes: 20
depends_on: [F05]
modifies: ["clawmarketing/frontend/src/components/CalendarWidget.tsx"]
executor: glm
---
## 目标
Add social calendar widget to ClawMarketing frontend - show scheduled posts across all platforms

## 约束
- Create CalendarWidget.tsx component
- Fetch scheduled items from scheduler endpoint
- Display calendar view (FullCalendar or react-big-calendar)
- Color-code by platform
- Click to view/edit scheduled item

## 验收标准
- [ ] CalendarWidget.tsx component created
- [ ] Fetches scheduled items from API
- [ ] Displays calendar with scheduled posts
- [ ] Color-coded by platform
- [ ] Click opens item detail modal
- [ ] Component renders in dashboard

## 不要做
- Don't build calendar library from scratch
- Don't add drag-and-drop rescheduling yet
- Don't implement bulk scheduling UI
