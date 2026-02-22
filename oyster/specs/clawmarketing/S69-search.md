---
task_id: S69-search
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - frontend/src/pages/*.tsx
---
## 目标
内容搜索功能
## 具体改动
- 连接 /api/v2/content/search?q=xxx
- 搜索框 → 实时搜索
