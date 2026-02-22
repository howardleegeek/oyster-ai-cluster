---
task_id: S014-pipeline-orchestrator
project: article-pipeline
priority: 0
estimated_minutes: 35
depends_on: ["S005-trend-ranker", "S009-article-reviser", "S010-article-db", "S013-tweet-thread-publisher"]
modifies: ["oyster/social/article-pipeline/orchestrator.py"]
executor: glm
---

## 目标
Main pipeline orchestrator. Runs the full cycle: trends → articles → publish → distribute.

## 约束
- Python 3.11+, asyncio
- Pipeline stages:
  1. Fetch trends from all adapters via TrendAggregator
  2. Rank trends via TrendRanker → top 3
  3. For each top trend:
     a. Generate outline via ArticleOutliner
     b. Write article via ArticleWriter
     c. Quality gate check → revise if needed (max 2 rounds)
     d. Save to ArticleDB
     e. Publish to X Articles → get URL
     f. Generate tweet thread with article URL
     g. Publish tweet thread
     h. Update distribution status in DB
  4. Log full pipeline metrics (time, articles produced, published)
- Concurrency: process trends sequentially (one article at a time to avoid rate limits)
- Config from env:
  - PIPELINE_MAX_ARTICLES_PER_RUN: default 3
  - PIPELINE_DRY_RUN: if true, don't publish (just generate and save)
- CLI entry point: `python -m article_pipeline.orchestrator`

## 验收标准
- [ ] PipelineOrchestrator class with `async def run() -> PipelineReport`
- [ ] PipelineReport: articles_generated, articles_published, articles_failed, duration_seconds
- [ ] Full pipeline works end-to-end with all components
- [ ] Dry run mode skips publishing
- [ ] CLI entry point works
- [ ] pytest integration test with all mocks

## 不要做
- No scheduling/cron (separate spec)
- No web UI
