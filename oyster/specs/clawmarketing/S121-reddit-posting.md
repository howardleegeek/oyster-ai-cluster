---
task_id: S121-reddit-posting
project: clawmarketing
priority: 2
depends_on: ["S120-reddit-client"]
modifies: ["backend/clients/reddit_client.py", "backend/agents/publisher_agent.py"]
executor: glm
---
## 目标
实现 Reddit 发帖功能，支持 self post 和链接帖子

## 约束
- 在 RedditClient 新增 post_to_subreddit(subreddit, title, content, link_url=None)
- title 5-300字符, content 1-40000字符
- 返回帖子 ID 和 URL
- 集成到 Publisher Agent
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] pytest tests/test_reddit_posting.py 全绿
- [ ] post_to_subreddit 正确返回帖子 ID 和 URL
- [ ] Publisher Agent 可调用 Reddit 发帖
- [ ] 参数验证边界条件正常

## 不要做
- 不动 frontend
- 不留 TODO/FIXME/placeholder
