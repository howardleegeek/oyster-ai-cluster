---
task_id: S81-bulk-publish
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - frontend/src/pages/*.tsx
---
## 目标
批量发布
## 具体改动
- 连接 /api/v2/content/bulk-publish
- 选择多条内容批量发布
