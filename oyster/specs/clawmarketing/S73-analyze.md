---
task_id: S73-analyze
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - frontend/src/pages/*.tsx
---
## 目标
AI 内容分析
## 具体改动
- 连接 /api/v2/content/{id}/analyze
- 显示质量分数和改进建议
