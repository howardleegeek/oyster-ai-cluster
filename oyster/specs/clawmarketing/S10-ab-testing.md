---
task_id: S10-ab-testing
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - backend/services/ab_testing.py
---

## 目标

实现 Content A/B Testing，自动生成变体并追踪效果。

## 约束

- **不动 UI/CSS**

##具体改动

### ABTesting

```python
class ABTesting:
    """Auto-generate variants, track metrics, promote winners"""
    
    async def create_variants(self, content: str, num_variants: int = 3) -> list[dict]:
        """Generate content variants"""
        
    async def track_variant(self, variant_id: int, post_uri: str):
        """Track variant performance"""
        
    async def get_winner(self, experiment_id: int) -> dict:
        """Get winning variant"""
        
    async def promote_winner(self, experiment_id: int):
        """Promote winner to main channel"""
```

### 功能

- 自动生成 2-4 个变体
- 追踪每个变体的互动
- 统计显著性分析
- 自动推广最优

## 验收标准

- [ ] 能生成变体
- [ ] 能追踪效果
- [ ] 能选出最优

## 不要做

- ❌ 不改 UI
