---
task_id: S05-FEED-DISCOVERER
project: bluesky-poster
priority: 1
depends_on: []
modifies:
  - bluesky/feed_discovery.py
  - bluesky/__main__.py
executor: glm
---

## 目标
为 Web3+AI 硬件科技方向自动发现和推荐热门自定义 Feed

## 约束
- 只做发现和推荐，不自动关注
- 不存储任何第三方数据
- 使用官方 AT Protocol API

## 具体改动

### bluesky/feed_discovery.py
新增 Feed 发现器模块：
1. `FeedDiscovery` 类
2. 搜索功能：按关键词（Web3, AI, Tech, Crypto, Hardware）搜索热门 Feed
3. 推荐功能：基于 Web3+AI 硬件方向的热门 Feed 列表
4. `discover_tech_feeds()` - 发现科技相关 Feed
5. `get_feed_info(uri)` - 获取单个 Feed 详情

### bluesky/__main__.py
新增 CLI 命令：
- `feeds search <keyword>` - 搜索 Feed
- `feeds recommend` - 获取推荐列表
- `feeds info <feed-uri>` - 查看 Feed 详情

## 验收标准
- [ ] 文件 bluesky/feed_discovery.py 存在且包含 `class FeedDiscovery` 定义
- [ ] 文件 bluesky/__main__.py 包含 `feeds` 子命令
- [ ] 验证命令 `python bluesky_poster.py feeds recommend` 返回 Tech/AI/Web3 相关 Feed
- [ ] 验证命令 `python bluesky_poster.py feeds search AI` 返回搜索结果

## 验证命令 (必须执行)
```bash
cd /home/ubuntu/dispatch/bluesky-poster
python3 bluesky_poster.py feeds recommend 2>&1 | grep -i "tech\|ai\|web3" || echo "FAIL: no tech feeds"
python3 bluesky_poster.py feeds search AI 2>&1 | grep -i "AI" || echo "FAIL: search failed"
```

## 不要做
- 不做自动关注/互关
- 不改已有的 post/queue/worker 功能
