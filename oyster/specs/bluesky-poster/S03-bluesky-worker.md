---
task_id: S03-bluesky-worker
project: bluesky-poster
priority: 1
depends_on: ["S01-bluesky-client", "S02-bluesky-queue", "S04-bluesky-rate-limiter"]
modifies: ["bluesky/worker.py"]
executor: glm
---

## 目标
实现 Worker 轮询循环，从队列取任务并执行发帖/回复

## 约束
- 依赖 S01 BlueskyClient, S02 BlueskyQueue, S04 RateLimiter
- 轮询间隔: 可配置 (默认 10s)
- 执行超时: 60s per job
- 重试: 指数退避 (30s, 60s, 120s + random jitter)
- 成功后延迟: RateLimiter.get_delay() (75-240s)
- 账号配置从 accounts.json 读取
- **必须实现优雅退出 (graceful shutdown)**

## 接口定义
```python
from dataclasses import dataclass
from bluesky.queue import BlueskyQueue
from bluesky.client import BlueskyClient

@dataclass
class JobResult:
    """单次 job 执行结果"""
    job_id: str
    success: bool
    uri: str | None = None
    url: str | None = None
    error: str | None = None


class BlueskyWorker:
    def __init__(
        self, 
        *, 
        accounts_path: str = "accounts.json",
        queue: BlueskyQueue | None = None,
        rate_limiter,  # RateLimiter 实例
        poll_interval: float = 10.0
    ) -> None:
        """
        Args:
            accounts_path: accounts.json 路径
            queue: BlueskyQueue 实例 (可选，运行时创建)
            rate_limiter: RateLimiter 实例
            poll_interval: 轮询间隔 (秒)
        """

    async def run(self) -> None:
        """
        主循环: poll → claim → check_cap → execute → mark → delay → repeat
        
        优雅退出:
        - 接收到 stop() 信号时，等待当前 job 完成
        - 最多等待 5 分钟
        """

    async def stop(self) -> None:
        """
        优雅停止：设置停止标志，等待当前 job 完成
        
        使用场景:
        - SIGTERM / SIGINT 信号处理
        - launchd stop 命令
        """

    async def run_once(self) -> JobResult | None:
        """
        处理一个 job，返回 JobResult 或 None (无 job)
        
        Returns:
            JobResult if a job was processed, None if no job available
        """

    async def _execute_job(self, *, job: dict, client: BlueskyClient) -> JobResult:
        """
        执行单个 job: post 或 reply
        
        Args:
            job: Job dict from queue
            client: BlueskyClient 实例
        
        Returns:
            JobResult with success, uri, url, or error
        """

    async def _get_client(self, *, handle: str) -> BlueskyClient:
        """
        获取/缓存已登录的 client
        
        同一 handle 只 login 一次，后续复用缓存
        """

    async def _load_accounts(self) -> dict[str, str]:
        """
        加载 accounts.json
        
        Returns:
            {handle: app_password, ...}
        """
```

## Worker 循环伪代码
```python
async def run(self):
    await self._load_accounts()
    
    while not self._stop_event.is_set():
        try:
            result = await self.run_once()
            
            if result:
                delay = self.rate_limiter.get_delay()
            else:
                delay = self.poll_interval
            
            # 等待 delay 或停止信号
            await asyncio.wait_for(self._stop_event.wait(), timeout=delay)
        
        except Exception as e:
            logger.exception(f"Error in worker loop: {e}")
            await asyncio.sleep(self.poll_interval)

async def run_once(self):
    # 1. 认领 job
    job = await self.queue.claim_next()
    if not job:
        return None
    
    # 2. 检查日上限
    handle = job['expected_handle']
    is_reply = bool(job['reply_to_uri'])
    posts, replies = await self.queue.get_daily_count(handle=handle)
    
    if not self.rate_limiter.check_daily_cap(
        current_posts=posts,
        current_replies=replies,
        is_reply=is_reply
    ):
        # defer 到明天
        tomorrow = self._get_next_midnight()
        await self.queue.mark_retry(job_id=job['id'], error="daily cap", not_before=tomorrow)
        return JobResult(job_id=job['id'], success=False, error="daily cap")
    
    # 3. 获取 client 并执行
    client = await self._get_client(handle=handle)
    try:
        result = await asyncio.wait_for(
            self._execute_job(job=job, client=client),
            timeout=60
        )
    except asyncio.TimeoutError:
        result = JobResult(job_id=job['id'], success=False, error="timeout")
    
    # 4. 处理结果
    if result.success:
        await self.queue.mark_posted(job_id=job['id'], uri=result.uri, url=result.url)
        await self.queue.increment_daily(handle=handle, is_reply=is_reply)
    else:
        await self._handle_failure(job=job, error=result.error)
    
    return result
```

## 验收标准

### 功能测试 (tests/test_worker.py)
- [ ] `pytest tests/test_worker.py -v` 全绿
- [ ] run_once 处理 queued job 并 mark_posted
- [ ] 失败 job 按指数退避重试
- [ ] 超过 max_attempts 的 job mark_failed
- [ ] 日上限触发时 defer 到明天
- [ ] client 缓存: 同一 handle 不重复 login

### 优雅退出测试 (tests/test_worker_shutdown.py)
- [ ] stop() 设置停止标志
- [ ] 当前 job 完成后退出循环
- [ ] stop() 最多等待 5 分钟
- [ ] SIGTERM 信号触发 stop()

### 集成测试 (tests/test_worker_integration.py)
- [ ] 完整流程: enqueue → claim → post → mark_posted
- [ ] 重试流程: failed → retry → success
- [ ] 多账号并发处理

### Mock 策略
```python
# 使用 unittest.mock
@pytest.fixture
def mock_queue():
    queue = AsyncMock(spec=BlueskyQueue)
    queue.claim_next.return_value = test_job
    return queue

@pytest.fixture
def mock_client():
    client = AsyncMock(spec=BlueskyClient)
    client.post.return_value = PostResult(uri="at://...", cid="...", url="https://...")
    return client
```

## 不要做
- 不实现 CLI 命令 (S05 负责)
- 不修改 queue.py (S02 负责)
- 不实现 AI 内容生成 (S06 负责)

## SHARED_CONTEXT
见 specs/SHARED_CONTEXT.md
