---
task_id: S002-trend-adapter-google
project: article-pipeline
priority: 0
estimated_minutes: 25
depends_on: ["S001-trend-aggregator-core"]
modifies: ["oyster/social/article-pipeline/adapters/google_trends.py"]
executor: glm
---

## 目标
Google Trends adapter using pytrends library. Fetches real-time trending searches and rising queries.

## 约束
- Python 3.11+, pytrends library
- Implement `TrendAdapter` protocol from S001
- Methods: `async def fetch_trends(region="US", category="tech") -> List[TrendItem]`
- Rate limit: max 1 request per 60 seconds (Google throttles aggressively)
- Regions: US, CN, global
- Categories: tech, crypto, AI, business
- Map Google's interest score (0-100) to normalized 0.0-1.0

## 验收标准
- [ ] GoogleTrendsAdapter class implementing TrendAdapter protocol
- [ ] fetch_trends returns List[TrendItem] with source="google_trends"
- [ ] Rate limiting with asyncio.Semaphore
- [ ] pytest test passes with mock pytrends response

## 不要做
- No pip install in code (just import, requirements listed)
- Don't touch trend_aggregator.py core
