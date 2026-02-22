---
task_id: S004-trend-adapter-twitfast
project: article-pipeline
priority: 0
estimated_minutes: 20
depends_on: ["S001-trend-aggregator-core"]
modifies: ["oyster/social/article-pipeline/adapters/twitfast_trends.py"]
executor: glm
---

## 目标
TwitFast adapter that connects to our self-hosted TwitFast trend API service.

## 约束
- Python 3.11+, httpx
- TwitFast service URL from env: TWITFAST_API_URL (default: http://localhost:3100)
- Endpoints (adapter should support):
  - GET /api/trends?region={region} → trending topics
  - GET /api/search?q={query} → tweet search for trend validation
- Map TwitFast response to TrendItem model
- Fallback: if TwitFast is down, return empty list (don't crash pipeline)
- Health check: GET /api/health before fetching

## 验收标准
- [ ] TwitFastAdapter class implementing TrendAdapter protocol
- [ ] Health check before fetch, graceful fallback on failure
- [ ] fetch_trends returns List[TrendItem] with source="twitfast"
- [ ] Configurable via env vars
- [ ] pytest test passes with mock HTTP responses

## 不要做
- Don't implement the TwitFast service itself (Howard's team handles that)
- Don't hardcode URLs
