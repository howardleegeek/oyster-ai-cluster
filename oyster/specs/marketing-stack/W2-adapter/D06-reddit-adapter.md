---
task_id: D06-reddit-adapter
project: marketing-stack
priority: 2
estimated_minutes: 25
depends_on: [A01]
modifies: ["oyster/social/reddit/adapter.py"]
executor: glm
---
## 目标
Create oyster/social/reddit/adapter.py implementing PlatformAdapter Protocol using PRAW (Python Reddit API Wrapper)

## 约束
- Use PRAW library for Reddit API access
- post() submits to specified subreddit
- reply() adds comment to post
- search() performs subreddit search
- Handle Reddit OAuth2 authentication
- Store credentials in ~/.oyster-keys/

## 验收标准
- [ ] adapter.py implements PlatformAdapter Protocol
- [ ] post() submits posts to subreddits
- [ ] reply() adds comments to posts
- [ ] search() finds relevant posts in subreddits
- [ ] OAuth2 authentication works
- [ ] pytest tests/social/reddit/test_adapter.py passes

## 不要做
- Don't build karma farming features
- Don't add subreddit discovery
- Don't implement vote manipulation
