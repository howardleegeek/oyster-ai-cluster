---
task_id: S13-competitor-tracker
project: bluesky-poster
priority: 0
estimated_minutes: 35
depends_on: []
modifies: ["bluesky/competitor_tracker.py"]
executor: glm
---

## Goal

Track competitor accounts on Bluesky for competitive intelligence.

## Context

- Monitor competitor activity: posting frequency, engagement, follower growth
- Detect anomalies: engagement spikes, viral posts
- Inform content strategy
- Reference: ClawMarketing competitor_monitor.py
- See `SHARED_CONTEXT.md` for project-wide conventions

## Implementation

Create `/Users/howardli/Downloads/oyster/social/bluesky-poster/bluesky/competitor_tracker.py`:

```python
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Optional
from bluesky.client import BlueskyClient
import aiosqlite

logger = logging.getLogger(__name__)

# Competitor accounts per persona
COMPETITORS = {
    "oysterecosystem": [
        "meta.bsky.social",  # Meta
        "hivemapper.bsky.social",  # DePIN competitor
    ],
    "clawglasses": [
        "ray-ban.bsky.social",  # Meta smart glasses
        "brilliant.bsky.social",  # AR glasses
    ],
    "puffyai": [
        "chatgpt.bsky.social",
        "claude.bsky.social",
    ]
}

class CompetitorTracker:
    def __init__(self, client: BlueskyClient, db_path: str = None):
        self.client = client
        if db_path is None:
            import os
            db_path = os.path.expanduser("~/.bluesky-poster/queue.sqlite3")
        self.db_path = db_path
```

**Database Schema**:

```sql
CREATE TABLE IF NOT EXISTS competitor_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    handle TEXT NOT NULL,
    competitor_handle TEXT NOT NULL,
    followers_count INTEGER,
    following_count INTEGER,
    posts_count INTEGER,
    snapshot_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_snapshots ON competitor_snapshots(handle, competitor_handle, snapshot_at);

CREATE TABLE IF NOT EXISTS competitor_top_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    competitor_handle TEXT NOT NULL,
    post_uri TEXT NOT NULL,
    post_text TEXT NOT NULL,
    likes INTEGER,
    reposts INTEGER,
    replies INTEGER,
    posted_at TEXT NOT NULL,
    detected_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_top_posts ON competitor_top_posts(competitor_handle, detected_at);
```

**Core Functions**:

```python
async def init_db(self):
    """Initialize competitor tracking tables"""

async def track_competitor(
    self,
    competitor_handle: str
) -> Dict:
    """
    Take snapshot of competitor:
    1. client.get_profile(competitor_handle)
    2. Store followers, following, posts counts
    3. Return current stats
    """

async def track_all_competitors(
    self,
    persona_handle: str
) -> List[Dict]:
    """Track all competitors for a persona"""

async def detect_anomalies(
    self,
    competitor_handle: str,
    lookback_days: int = 7
) -> List[Dict]:
    """
    Detect anomalies:
    - Follower spike: >50% increase in 24h
    - Engagement drop: >20% decrease in avg engagement
    - Posting frequency change: >2x increase or decrease
    Returns list of anomalies with descriptions.
    """

async def get_top_posts(
    self,
    competitor_handle: str,
    days: int = 7,
    limit: int = 5
) -> List[Dict]:
    """
    Get competitor's top posts:
    1. Search recent posts
    2. Sort by engagement (likes + reposts)
    3. Return top N
    """
```

**Anomaly Detection**:
- Compare current snapshot vs 7-day average
- Flag: follower spike >50%, engagement drop >20%, posting frequency change >2x

**CLI Integration**:
Add to `__main__.py`:
```python
async def cmd_competitors(args):
    client = BlueskyClient(handle=args.handle, app_password=args.password)
    await client.login()
    tracker = CompetitorTracker(client=client)

    if args.competitors_sub == "track":
        stats = await tracker.track_all_competitors(args.handle)
        for s in stats:
            print(f"{s['competitor_handle']}: {s['followers_count']} followers, {s['posts_count']} posts")

    elif args.competitors_sub == "anomalies":
        for comp in COMPETITORS.get(args.handle, []):
            anomalies = await tracker.detect_anomalies(comp)
            if anomalies:
                print(f"{comp}: {len(anomalies)} anomalies")
                for a in anomalies:
                    print(f"  - {a}")
```

## Tests

- `test_competitor_tracker.py`: Mock client.get_profile(), test tracking
- Test anomaly detection
- Test top posts retrieval

## Acceptance Criteria

- [ ] Tracks all competitors defined in COMPETITORS dict
- [ ] Stores snapshots in DB
- [ ] Detects follower spikes and engagement anomalies
- [ ] CLI command works: `python -m bluesky competitors track --handle X`
- [ ] Tests pass: `pytest tests/test_competitor_tracker.py -v`

## Do NOT

- Do not track competitors more than once per hour (rate limits)
- Do not add competitors not in COMPETITORS dict without approval
- Do not alert on small fluctuations (<10%)
