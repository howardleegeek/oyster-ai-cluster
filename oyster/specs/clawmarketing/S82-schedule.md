---
task_id: S82-schedule
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - frontend/src/pages/*.tsx
---
## 目标
定时发布
## 具体改动
- 连接 /api/v2/content/{id}/schedule
- 选择时间定时发布
