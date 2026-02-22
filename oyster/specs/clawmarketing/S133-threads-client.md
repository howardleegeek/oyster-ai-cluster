---
task_id: S133-threads-client
project: clawmarketing
priority: 2
depends_on: []
modifies: ["backend/clients/threads_client.py"]
executor: glm
---
## 目标
实现 Threads API 客户端 (Meta Graph API)

## 约束
- 使用 Meta Threads API (Graph API)
- 支持 THREADS_ACCESS_TOKEN, THREADS_USER_ID 环境变量
- Token 刷新逻辑
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] pytest tests/test_threads_client.py 全绿
- [ ] Client.post() 可发帖
- [ ] Client.get_feed() 可获取 feed
- [ ] Client.get_user_posts() 可获取用户帖子

## 不要做
- 不动 frontend
- 不留 TODO/FIXME/placeholder
