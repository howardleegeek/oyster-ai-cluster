---
task_id: S08-ANALYTICS
project: bluesky-poster
priority: 1
depends_on: []
modifies:
  - bluesky/analytics.py
  - bluesky/__main__.py
executor: glm
---

## 目标
实现数据分析和互动统计功能，追踪帖子表现和账号成长

## 约束
- 本地 SQLite 存储分析数据
- 只统计已发布帖子，不抓取他人数据
- 提供可视化报告（文本格式）

## 具体改动

### bluesky/analytics.py
新增数据分析模块：
1. `Analytics` 类
2. `track_post(post_result)` - 记录已发布帖子
3. `get_post_stats(post_id)` - 单帖统计数据
4. `get_daily_stats(days=7)` - 每日统计数据
5. `get_top_posts(limit=10)` - 表现最好的帖子
6. `get_growth_stats()` - 账号成长统计
7. `generate_report()` - 生成分析报告

### bluesky/__main__.py
新增 CLI 命令：
- `stats` - 整体统计概览
- `stats post <id>` - 单帖详情
- `stats daily` - 每日统计
- `stats top` - Top 10 帖子
- `stats report` - 生成完整报告
- `stats feed` - 分析哪些 Feed 收录了你的帖子

## 验收标准
- [ ] 文件 bluesky/analytics.py 存在且包含 `class Analytics` 定义
- [ ] 文件 bluesky/__main__.py 包含 `analytics` 子命令
- [ ] 验证命令 `python bluesky_poster.py analytics report` 生成报告
- [ ] 验证命令 `python bluesky_poster.py analytics top` 返回 Top 帖子

## 验证命令 (必须执行)
```bash
cd /home/ubuntu/dispatch/bluesky-poster
python3 bluesky_poster.py analytics report 2>&1 | grep -i "report\|post" || echo "FAIL"
python3 bluesky_poster.py analytics top 2>&1 | grep -i "top\|post" || echo "FAIL"
```

## 不要做
- 不抓取他人数据
- 不做第三方平台对接
