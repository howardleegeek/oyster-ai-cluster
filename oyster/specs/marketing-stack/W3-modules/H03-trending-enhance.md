---
task_id: H03-trending-enhance
project: marketing-stack
priority: 3
estimated_minutes: 25
depends_on: [A07-bluesky-enhance]
modifies: ["oyster/social/bluesky-poster/bluesky/trending.py"]
executor: glm
---
## 目标
Enhance trending.py with cross-platform trend aggregation (Twitter + Bluesky + Reddit), relevance scoring, auto-suggest topics

## 约束
- Aggregate trends from: Twitter API, Bluesky trending, Reddit rising posts
- Score trends by: volume, velocity, relevance to brand personas
- Method: get_relevant_trends(brand_persona) returns ranked list
- Method: suggest_content_topics(trend) returns 3-5 topic ideas
- Cache trends for 1 hour

## 验收标准
- [ ] trending.py enhanced with cross-platform aggregation
- [ ] Trend scoring algorithm implemented
- [ ] get_relevant_trends() works for each persona
- [ ] suggest_content_topics() returns valid ideas
- [ ] Caching reduces API calls
- [ ] pytest tests pass
- [ ] CLI: python -m bluesky.trending --persona <name>

## 不要做
- No auto-posting from trends
- No sentiment analysis (use Obsei)
- No UI visualization
