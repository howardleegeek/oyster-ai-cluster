## 目标
实现热门话题和趋势追踪，为 Web3+AI 硬件科技方向提供内容灵感

## 约束
- 只读追踪趋势，不自动发帖
- 使用官方 AT Protocol API
- 热门标签优先中文/科技方向

## 具体改动

### bluesky/trending.py
新增趋势追踪模块：
1. `Trending` 类
2. `get_trending_tags(limit=20)` - 获取热门标签
3. `search_posts(query, limit=50)` - 搜索帖子
4. `get_tech_trends()` - 获取科技/AI/Web3 相关趋势
5. `get_timeline_trends(limit=50)` - 从时间线提取趋势
6. `suggest_hashtags(content)` - 基于内容推荐标签

### bluesky/__main__.py
新增 CLI 命令：
- `trending tags` - 热门标签
- `trending search <query>` - 搜索帖子
- `trending tech` - 科技趋势
- `trending suggest <text>` - 推荐标签

## 验收标准
- [ ] 文件 bluesky/trending.py 存在且包含 `class Trending` 定义
- [ ] 文件 bluesky/__main__.py 包含 `trending` 子命令
- [ ] 验证命令 `python bluesky_poster.py trending tags` 返回热门标签
- [ ] 验证命令 `python bluesky_poster.py trending suggest "AI"` 返回 #AI 标签

## 验证命令 (必须执行)
```bash
cd /home/ubuntu/dispatch/bluesky-poster
python3 bluesky_poster.py trending tags 2>&1 | grep -i "web3\|ai\|tech" || echo "FAIL"
python3 bluesky_poster.py trending suggest "AI" 2>&1 | grep -i "AI" || echo "FAIL"
```

## 不要做
- 不做自动发帖
- 不改已有功能