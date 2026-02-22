---
task_id: S05-twitter-post-api
project: clawmarketing
priority: 5
depends_on: [S04-create-persona]
modifies: []
executor: local
---

## 目标
实现 Twitter 发推 API

## 具体改动
1. 后端添加 POST /api/v1/tasks/post
2. 调用 TwitterAgent 发推
3. 连接 Mac-2 CDP 浏览器

## 验收标准
- [ ] API 可以接受发推任务
- [ ] 任务加入队列
