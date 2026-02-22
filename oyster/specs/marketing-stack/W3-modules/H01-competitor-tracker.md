---
task_id: H01-competitor-tracker
project: marketing-stack
priority: 3
estimated_minutes: 30
depends_on: [A01-unified-db, G07-obsei-deploy, B12-serpbear-deploy]
modifies: ["oyster/social/common/competitor_tracker.py"]
executor: glm
---
## 目标
Create competitor tracking module to monitor follower growth, post frequency, engagement rate across platforms

## 约束
- Data sources: Obsei sentiment + SerpBear rank + platform APIs
- Metrics: follower count, daily posts, avg engagement, sentiment trend
- Store in unified.db: competitors, competitor_metrics tables
- Method: daily_digest() returns markdown report
- Platforms: Twitter, Bluesky, LinkedIn

## 验收标准
- [ ] competitor_tracker.py created with class CompetitorTracker
- [ ] Track 5+ competitors per platform
- [ ] SQLite schema for competitors/metrics
- [ ] daily_digest() generates report
- [ ] pytest tests pass
- [ ] Can run via: python -m competitor_tracker --report

## 不要做
- No auto-response to competitors
- No scraping (use APIs only)
- No UI dashboard yet
