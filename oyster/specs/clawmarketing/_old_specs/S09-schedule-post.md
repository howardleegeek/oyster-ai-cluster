---
task_id: S09-schedule-post
project: clawmarketing
priority: 9
depends_on: [S08-persona-engine]
modifies: []
executor: local
---

## 目标
实现定时发布功能

## 具体改动
1. 添加定时任务功能
2. 设置发布时间
3. 定时执行发推

## 验收标准
- [ ] 可以设置定时发布
- [ ] 到时间自动发推
