---
task_id: S13-campaign-builder
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - backend/services/campaign_builder.py
---

## 目标

实现 Campaign Builder，多帖子活动构建器。

## 约束

- **不动 UI/CSS**

##具体改动

### CampaignBuilder

```python
class CampaignBuilder:
    """Define multi-post campaigns"""
    
    async def create_campaign(self, name: str, description: str) -> int:
        """Create campaign"""
        
    async def add_post(self, campaign_id: int, content: str, scheduled_at: datetime = None):
        """Add post to campaign"""
        
    async def add_dependency(self, campaign_id: int, post_id: int, depends_on: int):
        """Add dependency between posts"""
        
    async def execute_campaign(self, campaign_id: int):
        """Execute campaign"""
        
    async def get_campaign_status(self, campaign_id: int) -> dict:
        """Get campaign status"""
```

### 功能

- 创建活动
- 添加帖子
- 设置依赖关系
- 定时执行
- 状态追踪

## 验收标准

- [ ] 能创建活动
- [ ] 能添加帖子
- [ ] 能设置依赖
- [ ] 能执行

## 不要做

- ❌ 不改 UI
