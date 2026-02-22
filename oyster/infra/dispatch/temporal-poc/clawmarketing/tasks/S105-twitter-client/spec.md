## 目标
实现 Twitter API 客户端基础架构

## 约束
- 基于 httpx 实现异步请求
- Twitter API v2
- 不新建超过 2 个文件
- 写 pytest 测试 (用 mock)

## 验收标准
- [ ] pytest tests/test_twitter_client.py 全绿
- [ ] TwitterClient.get_user_info() 可获取用户信息
- [ ] TwitterClient.get_timeline() 可获取时间线
- [ ] TwitterClient.post_tweet(content) 可发推

## 不要做
- 不动 frontend
- 不改 main.py 的路由结构
- 不留 TODO/FIXME/placeholder