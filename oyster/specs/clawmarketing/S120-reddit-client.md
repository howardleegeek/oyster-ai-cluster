---
task_id: S120-reddit-client
project: clawmarketing
priority: 2
depends_on: []
modifies: ["backend/clients/reddit_client.py"]
executor: glm
---
## 目标
实现 Reddit API 客户端基础类，支持 OAuth 认证和基础 API 调用

## 约束
- 使用 praw 库（Reddit API 包装）
- 参考 backend/clients/twitter_client.py 的代码风格
- 支持环境变量: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
- 实现 Context Manager 模式
- 所有 API 调用添加重试机制（3次指数退避）
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] pytest tests/test_reddit_client.py 全绿
- [ ] RedditClient 可正常实例化并认证
- [ ] 支持 with RedditClient() as client 语法
- [ ] 环境变量缺失时抛出 ConfigValidationError

## 不要做
- 不动 frontend
- 不留 TODO/FIXME/placeholder
