---
task_id: S75-reshare
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - frontend/src/pages/*.tsx
---
## 目标
快速转发
## 具体改动
- 连接 /api/v2/content/{id}/reshare
- 一键转发高热度内容
