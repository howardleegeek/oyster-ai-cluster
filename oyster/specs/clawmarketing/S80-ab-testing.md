---
task_id: S80-ab-testing
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - frontend/src/pages/*.tsx
---
## 目标
A/B 测试
## 具体改动
- 连接 /api/v2/content/{id}/create-variant
- 创建测试变体
