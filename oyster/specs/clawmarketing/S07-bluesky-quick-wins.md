---
task_id: S07-bluesky-quick-wins
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - backend/agents/hashtag_optimizer.py
  - backend/agents/bluesky_client.py
---

## 目标

快速完善：Hashtag 优化 + Alt 文本增强 + 编辑/删除能力。

## 约束

- **不动 UI/CSS**

## 具体改动

### 1. HashtagOptimizer

```python
class HashtagOptimizer:
    """Optimize hashtags for reach"""
    
    TRENDING_TAGS = {
        "depin": ["#DePIN", "#DePIN.io", "#PhysicalAI"],
        "ai": ["#AI", "#ArtificialIntelligence", "#MachineLearning"],
        "ubi": ["#UBI", "#UniversalBasicIncome", "#FutureOfWork"],
    }
    
    def optimize(self, text: str, topic: str) -> str:
        """Add relevant hashtags"""
        pass
    
    def get_trending(self, topic: str) -> list[str]:
        """Get trending hashtags for topic"""
        pass
```

### 2. Alt Text Enhancement (已有基础，增强)

```python
# 在 image_planner.py 增强
async def generate_alt(self, text: str, template: str, image_data: dict = None) -> str:
    """Generate descriptive alt text"""
    # 更智能的描述，不只是简单重复
    pass
```

### 3. Edit/Delete Post

```python
# 在 bluesky_client.py 添加
async def edit_post(self, uri: str, new_text: str) -> dict:
    """Edit existing post"""
    pass

async def delete_post(self, uri: str) -> bool:
    """Delete post"""
    pass
```

## 验收标准

- [ ] HashtagOptimizer 能添加相关标签
- [ ] Alt 文本更智能
- [ ] 能编辑帖子
- [ ] 能删除帖子

## 不要做

- ❌ 不改 UI
