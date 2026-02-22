---
task_id: S011-tweet-thread-splitter
project: article-pipeline
priority: 0
estimated_minutes: 25
depends_on: ["S007-article-writer"]
modifies: ["oyster/social/article-pipeline/tweet_thread_splitter.py"]
executor: glm
---

## 目标
Split a full article into a compelling Twitter thread (5-15 tweets) that drives traffic back to the full article.

## 约束
- Python 3.11+
- Input: Article from writer
- Output: TweetThread pydantic model:
  - tweets: List[Tweet] each with text (max 280 chars), position (1-based), has_link: bool
  - article_url: Optional[str] (set later when article is published)
- Thread structure:
  - Tweet 1: Hook — provocative question or bold claim from article
  - Tweet 2-N: Key insights, one per tweet, numbered with emoji
  - Last tweet: CTA — "Full article: {url}" + relevant hashtags (max 3)
- Use LLM to extract key insights from article
- Each tweet must be self-contained and valuable (not just "thread 🧵")
- No AI slop phrases

## 验收标准
- [ ] TweetThreadSplitter class with `async def split(article: Article) -> TweetThread`
- [ ] All tweets <= 280 chars
- [ ] Thread has hook + insights + CTA structure
- [ ] LLM extracts genuine insights (not generic)
- [ ] pytest test passes

## 不要做
- Don't post tweets (separate spec)
- Don't modify article content
