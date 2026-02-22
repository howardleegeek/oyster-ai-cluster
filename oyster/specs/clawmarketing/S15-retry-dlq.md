---
task_id: S15-retry-dlq
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - backend/services/retry_handler.py
---

## 目标

实现 Retry + Dead Letter Queue + 基础 Dashboard API。

## 约束

- **不动 UI/CSS**

##具体改动

### RetryHandler

```python
class RetryHandler:
    """Failed post retry with DLQ"""
    
    async def handle_failure(self, task_id: int, error: str):
        """Handle failure, schedule retry"""
        
    async def retry(self, task_id: int):
        """Manual retry"""
        
    async def move_to_dlq(self, task_id: int, reason: str):
        """Move to dead letter queue"""
        
    async def get_failed(self, account_id: int = None) -> list[dict]:
        """Get failed tasks"""
        
    async def get_dlq(self) -> list[dict]:
        """Get dead letter queue"""
```

### Dashboard API (JSON 输出)

```python
async def get_dashboard_stats() -> dict:
    """Get dashboard stats"""
    return {
        "accounts": [...],
        "pending_posts": ...,
        "failed_posts": ...,
        "recent_activity": [...],
        "health_status": {...}
    }
```

### 功能

- 指数退避重试
- 手动重试
- DLQ 存储
- Dashboard 统计 API

## 验收标准

- [ ] 失败自动重试
- [ ] 手动重试
- [ ] DLQ
- [ ] Dashboard API

## 不要做

- ❌ 不改 UI
