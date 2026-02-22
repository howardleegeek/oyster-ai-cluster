---
task_id: S037-cm-n8n-scheduler
project: marketing-stack
priority: 2
estimated_minutes: 15
depends_on: [B02]
modifies: ["clawmarketing/backend/routers/scheduler.py"]
executor: glm
---
## 目标
Add n8n workflow trigger to ClawMarketing scheduler router - scheduled items POST to n8n for execution

## 约束
- Add POST /scheduler/items/{id}/trigger endpoint
- POST to n8n webhook with item data
- Include content, platform, schedule_time
- Return trigger status
- Log trigger events

## 验收标准
- [ ] POST /scheduler/items/{id}/trigger endpoint implemented
- [ ] POSTs to n8n webhook
- [ ] Sends item content, platform, schedule_time
- [ ] Returns trigger status
- [ ] Logs trigger events
- [ ] pytest tests/backend/routers/test_scheduler.py passes

## 不要做
- Don't build scheduler engine (n8n handles)
- Don't add recurring schedules yet
- Don't implement time zone conversion
