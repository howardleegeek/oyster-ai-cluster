---
task_id: S77-archive
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - frontend/src/pages/*.tsx
---
## 目标
内容归档
## 具体改动
- 连接 /api/v2/content/{id}/archive
- 归档历史内容
