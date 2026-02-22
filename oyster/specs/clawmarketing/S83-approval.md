---
task_id: S83-approval
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - frontend/src/pages/*.tsx
---
## 目标
审批工作流
## 具体改动
- 连接 /api/v2/content/{id}/request-approval
- 提交审核 → 审批
