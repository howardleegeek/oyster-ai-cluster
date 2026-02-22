---
task_id: S012-x-article-publisher
project: article-pipeline
priority: 0
estimated_minutes: 35
depends_on: ["S008-article-quality-gate", "S010-article-db"]
modifies: ["oyster/social/article-pipeline/x_article_publisher.py"]
executor: glm
---

## 目标
Publish articles to X (Twitter) Articles feature using CDP browser automation.

## 约束
- Python 3.11+, Playwright CDP
- X Articles editor URL: https://x.com/i/articles/new (or compose equivalent)
- Publishing flow:
  1. Connect to existing Chrome CDP session (ws://localhost:9222)
  2. Navigate to X Articles editor
  3. Set title via DOM injection
  4. Set body via clipboard paste (markdown → rich text)
  5. Add cover image if provided
  6. Click publish
  7. Capture published URL
- Retry: 3 attempts with 10s delay
- Save published URL to ArticleDB
- Fallback: if X Articles is unavailable, save article as "ready_to_publish" in DB

## 验收标准
- [ ] XArticlePublisher class with `async def publish(article: Article) -> str` (returns URL)
- [ ] CDP connection to Chrome
- [ ] Title and body injection works
- [ ] Published URL capture
- [ ] Error handling and retry logic
- [ ] pytest test with mock CDP

## 不要做
- Don't implement Chrome launch (assume CDP session exists)
- Don't modify article content
- Don't post tweet thread (separate spec)
