---
task_id: S84-campaign-stats
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - frontend/src/pages/*.tsx
---
## 目标
战役统计
## 具体改动
- 连接 /api/v2/campaigns/{id}/stats
- 显示战役详细统计
