---
task_id: S003-trend-adapter-reddit
project: article-pipeline
priority: 0
estimated_minutes: 25
depends_on: ["S001-trend-aggregator-core"]
modifies: ["oyster/social/article-pipeline/adapters/reddit_trends.py"]
executor: glm
---

## 目标
Reddit rising posts adapter. Fetches rising/hot posts from target subreddits to detect emerging trends.

## 约束
- Python 3.11+, httpx (Reddit JSON API, no auth needed for public endpoints)
- Subreddits: r/technology, r/artificial, r/cryptocurrency, r/startups, r/web3, r/MachineLearning
- Endpoint: `https://www.reddit.com/r/{subreddit}/rising.json?limit=25`
- Score = upvote_ratio * log(score+1) / max_score, normalized to 0.0-1.0
- Velocity = comments_per_hour since post creation
- Rate limit: 1 request per 2 seconds (Reddit rate limit)
- User-Agent required: "OysterTrendBot/1.0"

## 验收标准
- [ ] RedditTrendsAdapter class implementing TrendAdapter protocol
- [ ] fetch_trends returns List[TrendItem] with source="reddit"
- [ ] Proper User-Agent header
- [ ] Rate limiting between subreddit fetches
- [ ] pytest test passes with mock Reddit JSON

## 不要做
- No Reddit OAuth/PRAW (use public JSON API)
- Don't touch other adapters
