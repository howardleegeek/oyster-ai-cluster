---
task_id: S135-threads-engagement
project: clawmarketing
priority: 2
depends_on: ["S133-threads-client"]
modifies: ["backend/engagement/threads_engagement.py"]
executor: glm
---
## 目标
实现 Threads 互动模块: like, reply, follow

## 约束
- 使用 Graph API endpoints
- 支持批量操作
- 操作频率控制
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] pytest tests/test_threads_engagement.py 全绿
- [ ] like(media_id) 正常工作
- [ ] reply(media_id, text) 正常工作
- [ ] follow(user_id) 正常工作

## 不要做
- 不动 frontend
- 不留 TODO/FIXME/placeholder
