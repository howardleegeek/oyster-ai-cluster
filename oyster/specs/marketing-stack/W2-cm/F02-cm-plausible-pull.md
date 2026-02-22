---
task_id: F02-cm-plausible-pull
project: marketing-stack
priority: 2
estimated_minutes: 20
depends_on: [B06]
modifies: ["clawmarketing/backend/routers/analytics.py"]
executor: glm
---
## 目标
Add Plausible API data pull to ClawMarketing analytics router, fetching site stats via Plausible Stats API

## 约束
- Add GET /analytics/plausible endpoint
- Use Plausible Stats API with API key from ~/.oyster-keys/
- Fetch pageviews, visitors, bounce rate, top pages
- Return JSON with time-series and aggregates
- Cache results for 5 minutes

## 验收标准
- [ ] GET /analytics/plausible endpoint implemented
- [ ] Fetches data from Plausible Stats API
- [ ] Returns pageviews, visitors, bounce rate, top pages
- [ ] Caching works (5 min TTL)
- [ ] Error handling for API failures
- [ ] pytest tests/backend/routers/test_analytics.py passes

## 不要做
- Don't build custom web analytics
- Don't add real-time tracking
- Don't implement goal tracking yet (E06 handles)
