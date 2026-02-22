---
task_id: S02-bluesky-queue
project: bluesky-poster
priority: 1
depends_on: []
modifies: ["bluesky/queue.py"]
executor: glm
---

## 目标
实现 SQLite 任务队列，管理发帖/回复 job 的完整生命周期

## 约束
- DB 路径: `~/.bluesky-poster/queue.sqlite3`，自动创建目录
- **写操作用 `BEGIN IMMEDIATE` + `FOR UPDATE SKIP LOCKED` 保证并发安全**
- 使用 aiosqlite (async SQLite)
- job status: queued → in_progress → posted | failed
- 所有方法 async def，强制 kwargs
- **北京时区 (UTC+8) 计算日期**

## Schema
```sql
-- Jobs 表
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    not_before TEXT NOT NULL DEFAULT (datetime('now')),
    text TEXT NOT NULL,
    reply_to_uri TEXT,
    reply_to_cid TEXT,
    image_path TEXT,
    image_alt TEXT,
    expected_handle TEXT NOT NULL,
    dry_run INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'queued',
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    last_error TEXT,
    result_uri TEXT,
    result_url TEXT,
    posted_at TEXT
);

-- 优化索引：支持按账号过滤的并发认领
CREATE INDEX IF NOT EXISTS idx_jobs_claim 
ON jobs(status, expected_handle, not_before) 
WHERE status = 'queued';

-- 已完成job的清理索引
CREATE INDEX IF NOT EXISTS idx_jobs_cleanup 
ON jobs(status, posted_at) 
WHERE status IN ('posted', 'failed');

-- 每日计数表
CREATE TABLE IF NOT EXISTS daily_posts (
    handle TEXT NOT NULL,
    date TEXT NOT NULL,
    post_count INTEGER NOT NULL DEFAULT 0,
    reply_count INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (handle, date)
);
```

## 接口定义
```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Job:
    """任务队列中的 job"""
    id: str
    created_at: str
    not_before: str
    text: str
    reply_to_uri: str | None
    reply_to_cid: str | None
    image_path: str | None
    image_alt: str | None
    expected_handle: str
    dry_run: bool
    status: str
    attempts: int
    max_attempts: int
    last_error: str | None
    result_uri: str | None
    result_url: str | None
    posted_at: str | None


class BlueskyQueue:
    def __init__(self, *, db_path: str | None = None) -> None: ...

    async def init_db(self) -> None:
        """创建表（如不存在）"""

    async def enqueue(
        self, 
        *, 
        text: str, 
        expected_handle: str,
        reply_to_uri: str | None = None, 
        reply_to_cid: str | None = None,
        image_path: str | None = None, 
        image_alt: str | None = None,
        not_before: str | None = None, 
        dry_run: bool = False,
        max_attempts: int = 3
    ) -> str:
        """入队，返回 job_id (UUID)"""

    async def claim_next(self, *, handle: str | None = None) -> Job | None:
        """
        认领下一个 queued job (status→in_progress)，返回 Job 或 None
        
        关键：使用 BEGIN IMMEDIATE + 行级锁保证并发安全
        多个 worker 并发调用时，只有一个能成功认领同一个 job
        """

    async def mark_posted(self, *, job_id: str, uri: str, url: str) -> None: ...
    
    async def mark_failed(self, *, job_id: str, error: str) -> None: ...
    
    async def mark_retry(self, *, job_id: str, error: str, not_before: str) -> None:
        """attempts+1, status→queued, 设置 not_before"""

    async def stats(self, *, handle: str | None = None) -> dict:
        """返回 {queued: N, in_progress: N, posted: N, failed: N}"""

    async def get_daily_count(self, *, handle: str) -> tuple[int, int]:
        """返回 (post_count, reply_count) 今日 (北京时区)"""

    async def increment_daily(self, *, handle: str, is_reply: bool = False) -> None: ...

    async def claim_stale_jobs(self, *, timeout_seconds: int = 300) -> list[str]:
        """
        将超时的 in_progress job 重置为 queued
        
        Args:
            timeout_seconds: 超时秒数（默认 5 分钟）
        
        Returns:
            被重置的 job_id 列表
        """
```

## 验收标准

### 功能测试 (pytest tests/test_queue.py)
- [ ] `pytest tests/test_queue.py -v` 全绿
- [ ] enqueue 返回有效的 UUID string
- [ ] claim_next 只返回 status='queued' 且 not_before <= now 的 job
- [ ] claim_next 返回后 job.status 变为 'in_progress'
- [ ] mark_retry 增加 attempts 并设置 not_before
- [ ] mark_posted 设置 result_uri/result_url/posted_at
- [ ] stats 返回所有状态的正确计数
- [ ] daily_posts 自动按北京日期累计

### 并发安全测试 (tests/test_queue_concurrent.py)
- [ ] 多个 worker 并发 claim 同一个 job，只有一个成功
- [ ] 并发 enqueue + claim 不冲突
- [ ] claim_stale_jobs 正确重置超时 job

### 边界测试 (tests/test_queue_edge.py)
- [ ] not_before 设为未来时间，claim_next 不返回
- [ ] 超出发送次数限制的 job 被标记为 failed
- [ ] 日期跨天后 daily_posts 正确重置计数
- [ ] 空队列调用 claim_next 返回 None

## 不要做
- 不实现 worker 循环 (S03 负责)
- 不调用 BlueskyClient (S01 负责)
- 不实现 engagement_targets 表 (S13 负责)

## SHARED_CONTEXT
见 specs/SHARED_CONTEXT.md
