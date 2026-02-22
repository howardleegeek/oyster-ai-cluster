---
task_id: F10-cm-crm-widget
project: marketing-stack
priority: 2
estimated_minutes: 20
depends_on: [F07]
modifies: ["clawmarketing/frontend/src/components/CRMWidget.tsx"]
executor: glm
---
## 目标
Add CRM pipeline widget to ClawMarketing frontend - show lead funnel from Twenty data

## 约束
- Create CRMWidget.tsx component
- Fetch contacts from accounts endpoint
- Display funnel chart (leads → qualified → customers)
- Show count per stage
- Click to view contacts in stage

## 验收标准
- [ ] CRMWidget.tsx component created
- [ ] Fetches contact data from API
- [ ] Displays funnel chart with stages
- [ ] Shows count per stage
- [ ] Click opens contacts list for stage
- [ ] Component renders in dashboard

## 不要做
- Don't build full CRM UI
- Don't add contact editing yet
- Don't implement custom pipeline stages
