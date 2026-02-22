---
task_id: S61-scout-intelligence
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - frontend/src/pages/Scout.tsx
---

## 目标
Scout 情报页面

## 具体改动
- 连接 /api/v2/competitors/
- 连接 /api/v2/trending
- 连接 /api/v2/audience

## 验收标准
- [ ] 显示竞品追踪
- [ ] 显示热门话题
