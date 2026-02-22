---
task_id: S010-article-db
project: article-pipeline
priority: 0
estimated_minutes: 20
depends_on: []
modifies: ["oyster/social/article-pipeline/article_db.py"]
executor: glm
---

## 目标
SQLite database for storing articles, outlines, trends, and distribution status.

## 约束
- Python 3.11+, aiosqlite
- Tables:
  - trends: id, topic, source, score, velocity, category, discovered_at, used_at
  - outlines: id, trend_id, title, outline_json, created_at, status
  - articles: id, outline_id, title, body_markdown, total_words, quality_score, status (draft/reviewed/published/failed), created_at, published_at
  - distributions: id, article_id, platform (x_article/tweet_thread/blog), status, published_url, published_at, engagement_stats_json
- DB path from env: ARTICLE_PIPELINE_DB (default: ~/.oyster/article-pipeline.db)
- All operations async
- Migration on first connect (CREATE IF NOT EXISTS)

## 验收标准
- [ ] ArticleDB class with CRUD methods for all 4 tables
- [ ] Auto-migration on connect
- [ ] `get_unused_trends()`, `get_articles_ready_to_publish()`, `update_distribution_status()`
- [ ] pytest test passes with in-memory SQLite

## 不要做
- No PostgreSQL (SQLite is fine for this volume)
- No ORM (raw SQL with aiosqlite)
