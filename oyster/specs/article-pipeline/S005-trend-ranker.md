---
task_id: S005-trend-ranker
project: article-pipeline
priority: 0
estimated_minutes: 25
depends_on: ["S001-trend-aggregator-core"]
modifies: ["oyster/social/article-pipeline/trend_ranker.py"]
executor: glm
---

## 目标
Rank and filter aggregated trends by relevance to Oyster Labs brand and products. Only surface trends worth writing articles about.

## 约束
- Python 3.11+
- Input: List[TrendItem] from aggregator
- Output: List[RankedTrend] with added fields: relevance_score, article_worthiness, suggested_angle
- Brand keywords (hardcoded list): AI, agents, AR glasses, Web3, DePIN, smart devices, wearables, privacy, decentralized, mobile AI, on-device, LLM, crypto
- Scoring formula: `final_score = trend.score * 0.4 + velocity * 0.3 + brand_relevance * 0.3`
- brand_relevance: keyword overlap ratio with brand keywords (0.0-1.0)
- article_worthiness threshold: final_score >= 0.5
- Deduplicate similar trends (fuzzy match, threshold 0.8)
- Max output: top 10 trends per cycle

## 验收标准
- [ ] TrendRanker class with `rank(trends: List[TrendItem]) -> List[RankedTrend]`
- [ ] Brand relevance scoring works
- [ ] Deduplication removes near-duplicates
- [ ] Only article-worthy trends pass (>= 0.5)
- [ ] pytest test passes

## 不要做
- No LLM calls (pure algorithmic ranking)
- No external API calls
