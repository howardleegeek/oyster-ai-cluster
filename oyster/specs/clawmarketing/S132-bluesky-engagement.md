---
task_id: S132-bluesky-engagement
project: clawmarketing
priority: 2
depends_on: ["S130-bluesky-client"]
modifies: ["backend/engagement/bluesky_engagement.py"]
executor: glm
---
## 目标
实现 Bluesky 互动模块: like, repost, follow

## 约束
- 使用 AT Protocol record 操作
- 支持批量操作
- 操作频率控制
- 返回操作结果状态
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] pytest tests/test_bluesky_engagement.py 全绿
- [ ] like(uri) 正常工作
- [ ] repost(uri) 正常工作
- [ ] follow(did) 正常工作

## 不要做
- 不动 frontend
- 不留 TODO/FIXME/placeholder
