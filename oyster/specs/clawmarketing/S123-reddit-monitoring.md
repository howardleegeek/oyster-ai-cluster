---
task_id: S123-reddit-monitoring
project: clawmarketing
priority: 2
depends_on: ["S120-reddit-client"]
modifies: ["backend/clients/reddit_client.py", "backend/agents/analyst_agent.py"]
executor: glm
---
## 目标
实现 Subreddit 监控功能，关键词追踪和热门帖子获取

## 约束
- 新增: get_subreddit_posts(subreddit, sort, limit), search_subreddit(subreddit, query), monitor_subreddit(subreddit, keywords, callback)
- monitor 使用后台线程轮询60秒间隔
- 集成到 Analyst Agent
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] pytest tests/test_reddit_monitoring.py 全绿
- [ ] get_subreddit_posts 返回正确格式数据
- [ ] search_subreddit 正确过滤结果
- [ ] monitor 正确检测关键词触发 callback

## 不要做
- 不动 frontend
- 不留 TODO/FIXME/placeholder
