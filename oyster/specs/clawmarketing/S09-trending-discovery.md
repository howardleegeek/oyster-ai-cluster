---
task_id: S09-trending-discovery
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - backend/agents/trending_discovery.py
---

## 目标

实现 Trending Topic Discovery，监控趋势并建议内容。

## 约束

- **不动 UI/CSS**

## 具体改动

### TrendingDiscovery

```python
class TrendingDiscovery:
    """Monitor feeds for trending topics"""
    
    async def get_trending(self, keywords: list[str] = None) -> list[dict]:
        """Get trending topics"""
        
    async def get_related_topics(self, topic: str) -> list[str]:
        """Get related topics"""
        
    async def suggest_content_angles(self, topic: str) -> list[str]:
        """Suggest content angles for topic"""
        
    async def monitor_feed(self, account_id: int) -> list[dict]:
        """Monitor account feed for trends"""
```

### 功能

- 搜索关键词热度
- 关联话题发现
- 内容角度建议
- Feed 监控

## 验收标准

- [ ] 能获取趋势话题
- [ ] 能建议内容角度
- [ ] 能监控 Feed

## 不要做

- ❌ 不改 UI
