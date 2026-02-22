---
task_id: S118-retry-ratelimit
project: clawmarketing
priority: 3
depends_on: []
modifies: ["backend/middleware/retry_middleware.py", "backend/utils/rate_limiter.py"]
executor: glm
---
## 目标
实现通用重试机制和 API 限流工具

## 约束
- 指数退避重试
- Token bucket 限流
- 写 pytest 测试

## 验收标准
- [ ] pytest tests/test_retry_and_rate_limit.py 全绿
- [ ] retry_with_backoff(fn, max_retries=3) 正常工作
- [ ] RateLimiter(requests_per_minute=60) 正常限流

## 不要做
- 不动 frontend
- 不留 TODO/FIXME/placeholder
