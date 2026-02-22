---
task_id: S129-linkedin-ratelimiter
project: clawmarketing
priority: 2
depends_on: ["S125-linkedin-client"]
modifies: ["backend/services/linkedin_rate_limiter.py"]
executor: glm
---
## 目标
实现 LinkedIn 连接请求限流器，遵守每周 100 个限制

## 约束
- 每周 100 个连接请求硬限制
- 按周自动重置计数
- 发送前检查剩余配额
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] pytest tests/test_linkedin_rate_limiter.py 全绿
- [ ] RateLimiter.can_send() 正确判断
- [ ] RateLimiter.record_sent() 正确更新计数
- [ ] 超限时抛出异常阻止发送

## 不要做
- 不动 frontend
- 不留 TODO/FIXME/placeholder
