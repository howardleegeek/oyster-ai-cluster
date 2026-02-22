---
task_id: S04-bluesky-analytics
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - backend/services/analytics.py
---

## 目标

实现 Analytics 追踪系统。

## 约束

- **不动 UI/CSS**

## 具体改动

### Analytics (`backend/services/analytics.py`)

```python
class Analytics:
    """Track post performance"""
    
    async def track_post(self, post_uri: str, account_id: int):
        """Track a newly published post"""
        pass
    
    async def refresh_stats(self, post_uri: str):
        """Fetch latest stats from Bluesky"""
        pass
    
    async def get_metrics(self, account_id: int, days: int = 7) -> dict:
        """Get account metrics"""
        pass
    
    async def get_top_posts(self, account_id: int, limit: int = 10) -> list[dict]:
        """Get top performing posts"""
        pass
    
    async def get_best_times(self, account_id: int) -> list[dict]:
        """Analyze best posting times"""
        pass
```

### 追踪指标

- impressions (曝光)
- likes, reposts, replies (互动)
- engagement_rate = (likes + reposts + replies) / impressions
- follower_delta (粉丝增长)
- 账号粒度和帖子粒度

### 定期刷新

- 发布后立即获取初始 stats
- 定时任务刷新历史 post 统计

## 验收标准

- [ ] 发布时自动记录
- [ ] 能获取账号整体指标
- [ ] 能获取 top posts
- [ ] 能分析最佳发布时间

## 不要做

- ❌ 不改 UI
