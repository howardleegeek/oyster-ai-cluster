---
task_id: S03-bluesky-scheduler
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - backend/services/content_scheduler.py
---

## 目标

实现 Content Calendar 和 Scheduling 系统。

## 约束

- **不动 UI/CSS**

## 具体改动

### ContentScheduler (`backend/services/content_scheduler.py`)

```python
class ContentScheduler:
    """Queue-based content scheduler"""
    
    async def schedule(self, content: str, account_id: int, scheduled_time: datetime):
        """Schedule content for future posting"""
        pass
    
    async def get_queue(self, account_id: int) -> list[dict]:
        """Get pending queue for account"""
        pass
    
    async def process_queue(self, account_id: int):
        """Process due items from queue"""
        pass
    
    async def find_optimal_time(self, account_id: int) -> datetime:
        """Find best posting time based on historical data"""
        pass
```

### ContentItem 状态机

```
draft → scheduled → publishing → published
                   → failed → retry
                   → pending_review (if approval enabled)
```

### 功能

- 时区感知 (自动转换用户时区)
- 最佳时间检测 (基于历史数据)
- 冲突检测 (同一账号短时间多 post)
- 重试机制

## 验收标准

- [ ] 能添加内容到调度队列
- [ ] 能按时间自动发布
- [ ] 能检测最佳发布时间
- [ ] 失败自动重试

## 不要做

- ❌ 不改 UI
