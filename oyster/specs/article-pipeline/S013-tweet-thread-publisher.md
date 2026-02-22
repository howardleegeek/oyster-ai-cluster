---
task_id: S013-tweet-thread-publisher
project: article-pipeline
priority: 0
estimated_minutes: 25
depends_on: ["S011-tweet-thread-splitter", "S012-x-article-publisher"]
modifies: ["oyster/social/article-pipeline/tweet_thread_publisher.py"]
executor: glm
---

## 目标
Post tweet threads to Twitter, with each tweet as a reply to the previous one.

## 约束
- Python 3.11+
- Use existing twitter-poster library: `from twitter_poster import TwitterPoster`
- Import path: oyster/social/twitter-poster/src/twitter_poster/poster.py
- Publishing flow:
  1. Post first tweet (hook)
  2. For each subsequent tweet: post as reply to previous tweet ID
  3. Last tweet includes article URL
  4. Save all tweet IDs to ArticleDB distributions table
- Rate limiting: 5-second delay between tweets in thread
- If any tweet fails mid-thread, log partial thread and mark as "partial" in DB
- Method preference: RapidAPI first, CDP fallback

## 验收标准
- [ ] TweetThreadPublisher class with `async def publish_thread(thread: TweetThread) -> List[str]` (tweet IDs)
- [ ] Reply chain maintained (each tweet replies to previous)
- [ ] Rate limiting between tweets
- [ ] Partial failure handling
- [ ] pytest test with mock TwitterPoster

## 不要做
- Don't generate tweet content (comes from splitter)
- Don't modify twitter-poster library
