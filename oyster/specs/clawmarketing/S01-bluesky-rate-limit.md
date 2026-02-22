---
task_id: S01-bluesky-rate-limit
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - backend/agents/bluesky_client.py
  - backend/agents/bluesky_cdp_client.py
---

## 目标

实现 Rate Limiting 和 Retry Logic，保护账号不被封。

## 约束

- **不动 UI/CSS**

## 具体改动

### RateLimiter (`backend/agents/rate_limiter.py`)

```python
class RateLimiter:
    """Rate limiting with exponential backoff"""
    
    # Bluesky rate limits
    LIMITS = {
        "post": {"max": 300, "window": 3600},      # 300 posts/hour
        "like": {"max": 1000, "window": 3600},     # 1000 likes/hour
        "follow": {"max": 200, "window": 3600},     # 200 follows/hour
        "search": {"max": 100, "window": 3600},
    }
    
    def __init__(self):
        self.counters = {}  # {action: [(timestamp, count)]}
    
    async def acquire(self, action: str) -> bool:
        """Acquire rate limit slot, returns True if allowed"""
        pass
    
    async def wait_if_needed(self, action: str):
        """Wait if rate limit would be exceeded"""
        pass
    
    async def exponential_backoff(self, attempt: int) -> float:
        """Calculate backoff: 1s, 2s, 4s, 8s..."""
        return min(2 ** attempt, 60)
```

### Retry Logic

```python
async def with_retry(func, max_retries=3):
    """Decorator for retry with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if "429" in str(e):  # Rate limited
                await asyncio.sleep(await rate_limiter.exponential_backoff(attempt))
            elif attempt == max_retries - 1:
                raise
```

## 验收标准

- [ ] RateLimiter 跟踪每个 action 的使用量
- [ ] 超过限制自动等待
- [ ] 429 错误自动重试
- [ ] 指数退避

## 不要做

- ❌ 不改 UI
