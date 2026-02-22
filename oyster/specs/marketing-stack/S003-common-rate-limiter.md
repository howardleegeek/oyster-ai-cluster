---
task_id: S003-common-rate-limiter
project: marketing-stack
priority: 1
estimated_minutes: 20
depends_on: ["S001-common-directory"]
modifies: ["oyster/social/common/rate_limiter.py"]
executor: glm
---

## 目标
Parameterize rate limiter from bluesky-poster for multi-platform use

## 约束
- Copy from oyster/social/bluesky-poster/bluesky/rate_limiter.py
- Constructor takes config dict: {timezone, daily_post_cap, daily_reply_cap, min_delay, max_delay, peak_hours}
- Default timezone="Asia/Shanghai"
- Keep all existing rate limiting logic

## 验收标准
- [ ] oyster/social/common/rate_limiter.py exists
- [ ] RateLimiter.__init__(config: dict) accepts parameterized config
- [ ] Defaults match current bluesky-poster behavior
- [ ] can_post() and can_reply() work with new config
- [ ] pytest tests verify different platform configs don't interfere
- [ ] Existing bluesky behavior unchanged with default config

## 不要做
- Don't add new rate limiting strategies
- Don't change core algorithm
- Don't add Redis/external storage
