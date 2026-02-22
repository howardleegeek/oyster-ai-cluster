---
task_id: S001-trend-aggregator-core
project: article-pipeline
priority: 0
estimated_minutes: 30
depends_on: []
modifies: ["oyster/social/article-pipeline/trend_aggregator.py", "oyster/social/article-pipeline/__init__.py"]
executor: glm
---

## 目标
Create the trend aggregator core module that fetches and ranks trending topics from multiple sources.

## 约束
- Python 3.11+
- Use httpx for async HTTP calls
- Use pydantic for data models
- Output: `List[TrendItem]` with fields: topic, source, score, velocity, category, discovered_at
- Score normalization: all sources map to 0.0-1.0 scale
- Cache results in SQLite with 30-minute TTL
- Module path: `oyster/social/article-pipeline/trend_aggregator.py`

## 验收标准
- [ ] TrendItem pydantic model with all fields
- [ ] TrendAggregator class with `async def fetch_all() -> List[TrendItem]`
- [ ] SQLite cache with TTL logic
- [ ] Score normalization across sources
- [ ] pytest test_trend_aggregator.py passes

## 不要做
- No UI/frontend code
- No actual API calls yet (use adapter pattern, adapters in separate specs)
- Don't modify any existing files outside this module
