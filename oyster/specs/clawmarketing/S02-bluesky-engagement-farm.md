---
task_id: S02-bluesky-engagement-farm
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - backend/agents/engagement_farmer.py
---

## 目标

实现 Engagement Farming Engine，编排完整的增长工作流。

## 约束

- **不动 UI/CSS**

## 具体改动

### EngagementFarmer (`backend/agents/engagement_farmer.py`)

```python
class EngagementFarmer:
    """Systematic engagement automation"""
    
    async def run_farming_cycle(self, keywords: list[str], actions_per_keyword: int = 5):
        """Run one farming cycle"""
        pass
    
    async def discover_posts(self, keyword: str, limit: int = 20) -> list[dict]:
        """Discover relevant posts via search"""
        pass
    
    async def engage(self, post: dict, action: str):
        """Engage with post: like, reply, or follow"""
        pass
    
    async def should_reply(self, post: dict) -> bool:
        """AI decision: should we reply?"""
        pass
    
    async def generate_reply_text(self, post: dict) -> str:
        """Generate contextual reply"""
        pass
```

### 工作流

```
1. 搜索关键词 (DePIN, AI Hardware, UBI...)
2. 筛选高质量 posts (有一定互动，非 spam)
3. 点赞 + 关注作者
4. 选择性回复 (AI 判断值得回复的)
5. 记录互动历史
```

## 验收标准

- [ ] 搜索关键词发现 posts
- [ ] 自动点赞
- [ ] AI 判断是否回复
- [ ] 生成上下文相关的回复
- [ ] 记录互动历史

## 不要做

- ❌ 不改 UI
