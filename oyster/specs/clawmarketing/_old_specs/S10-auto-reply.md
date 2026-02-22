---
task_id: S10-auto-reply
project: clawmarketing
priority: 10
depends_on: [S09-schedule-post]
modifies: []
executor: local
---

## 目标
实现自动回复功能

## 具体改动
1. 监听 Mention
2. 自动生成回复
3. 自动回复

## 验收标准
- [ ] 可以自动回复 Mention
