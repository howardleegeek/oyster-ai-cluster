---
task_id: S12-trend-detector
project: bluesky-poster
priority: 0
estimated_minutes: 30
depends_on: ["S10"]
modifies: ["bluesky/trending.py"]
executor: glm
---

## Goal

Real-time Bluesky trend detection to inform content generation.

## Context

- Existing `/Users/howardli/Downloads/oyster/social/bluesky-poster/bluesky/trending.py` has static tag lists
- Enhance with real-time detection using client.search_posts()
- Score topics by post volume + engagement + recency
- Feed trending topics into content_engine for timely content
- See `SHARED_CONTEXT.md` for project-wide conventions

## Implementation

Enhance existing `/Users/howardli/Downloads/oyster/social/bluesky-poster/bluesky/trending.py`:

Add new class:
```python
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict
from bluesky.client import BlueskyClient

class TrendDetector:
    def __init__(self, client: BlueskyClient):
        self.client = client
        self.search_keywords = [
            "AI", "crypto", "DePIN", "agents", "OpenAI", "blockchain",
            "hardware", "wearables", "UBI", "sovereignty", "AR", "VR"
        ]
```

**Core Functions**:

```python
async def detect_trends(
    self,
    hours: int = 24,
    min_posts: int = 10
) -> List[Dict]:
    """
    Detect trending topics:
    1. For each search keyword, call client.search_posts()
    2. Count posts in last N hours
    3. Calculate engagement rate (avg likes per post)
    4. Score = post_volume * engagement_rate * recency_factor
    5. Return top 20 topics sorted by score

    Returns: [{"topic": "AI agents", "score": 0.85, "posts": 42, "avg_likes": 12}, ...]
    """

async def get_trending_for_persona(
    self,
    persona
) -> List[str]:
    """
    Get trending topics relevant to persona:
    1. detect_trends()
    2. Filter to persona.topics keywords
    3. Return top 5 relevant trends
    """

def _score_topic(
    self,
    topic: str,
    posts: List[dict],
    hours: int
) -> float:
    """
    Score 0.0-1.0:
    - Volume (0-0.4): number of posts
    - Engagement (0-0.4): avg likes/reposts
    - Recency (0-0.2): prefer last 6h over 24h
    """
```

**Integration with ContentEngine**:
content_engine can call `trend_detector.get_trending_for_persona()` to get timely topics.

**CLI Integration**:
Enhance existing `trends` command in `__main__.py`:
```python
async def cmd_trends(args):
    # Existing static trends
    if args.trending_sub == "tags":
        ...
    # New: real-time detection
    elif args.trending_sub == "detect":
        client = BlueskyClient(handle=args.handle, app_password=args.password)
        await client.login()
        detector = TrendDetector(client=client)
        trends = await detector.detect_trends(hours=24)
        for t in trends[:20]:
            print(f"{t['topic']}: {t['score']:.2f} ({t['posts']} posts, {t['avg_likes']:.1f} avg likes)")
```

## Tests

- `test_trending.py`: Mock client.search_posts(), test trend detection
- Test scoring algorithm
- Test persona filtering

## Acceptance Criteria

- [ ] Detects 20+ trending topics in last 24h
- [ ] Scores topics by volume + engagement + recency
- [ ] Filters trends by persona topics
- [ ] CLI command works: `python -m bluesky trends detect --handle X`
- [ ] Tests pass: `pytest tests/test_trending.py -v`

## Do NOT

- Do not call search_posts() more than once per keyword (rate limits)
- Do not return topics with <10 posts (too niche)
- Do not modify existing static tag functionality
