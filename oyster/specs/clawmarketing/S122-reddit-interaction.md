---
task_id: S122-reddit-interaction
project: clawmarketing
priority: 2
depends_on: ["S120-reddit-client"]
modifies: ["backend/clients/reddit_client.py"]
executor: glm
---
## 目标
实现 Reddit 评论互动功能，支持回复和投票

## 约束
- 新增: comment(post_id, content), upvote(item_id), downvote(item_id), get_comments(post_id)
- 支持嵌套回复
- 所有互动方法返回操作结果
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] pytest tests/test_reddit_interaction.py 全绿
- [ ] comment 正确返回评论 ID
- [ ] upvote/downvote 正确执行
- [ ] get_comments 返回格式化评论列表

## 不要做
- 不动 frontend
- 不留 TODO/FIXME/placeholder
