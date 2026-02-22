## 目标
实现 Bluesky AT Protocol 客户端，支持发帖、获取 feed

## 约束
- 使用 atproto 库
- 参考 twitter_client.py 架构
- 支持 BLUESKY_HANDLE, BLUESKY_APP_PASSWORD 环境变量
- Session 管理（登录/刷新 token）
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] pytest tests/test_bluesky_client.py 全绿
- [ ] Client.post() 可发帖
- [ ] Client.get_feed() 可获取 feed
- [ ] Client.get_user_posts() 可获取用户帖子

## 不要做
- 不动 frontend
- 不留 TODO/FIXME/placeholder