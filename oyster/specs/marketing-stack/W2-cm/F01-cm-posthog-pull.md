---
task_id: F01-cm-posthog-pull
project: marketing-stack
priority: 2
estimated_minutes: 20
depends_on: [B04]
modifies: ["clawmarketing/backend/routers/analytics.py"]
executor: glm
---
## 目标
Add PostHog API data pull to ClawMarketing analytics router, fetching project metrics via PostHog REST API

## 约束
- Add GET /analytics/posthog endpoint
- Use PostHog REST API with API key from ~/.oyster-keys/
- Fetch event counts, conversion rates, user counts
- Return JSON with time-series data
- Cache results for 5 minutes

## 验收标准
- [ ] GET /analytics/posthog endpoint implemented
- [ ] Fetches data from PostHog REST API
- [ ] Returns events, conversions, users metrics
- [ ] Caching works (5 min TTL)
- [ ] Error handling for API failures
- [ ] pytest tests/backend/routers/test_analytics.py passes

## 不要做
- Don't build custom event tracking
- Don't add visualization (frontend only)
- Don't implement user segmentation yet
