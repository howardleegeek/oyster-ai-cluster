---
task_id: S14-ab-testing
project: bluesky-poster
priority: 0
estimated_minutes: 30
depends_on: ["S10", "S11"]
modifies: ["bluesky/ab_testing.py"]
executor: glm
---

## Goal

A/B testing for content optimization.

## Context

- Generate 2-3 variants for each original post
- Post at different times or on different days
- Track engagement per variant
- Determine winner after min 24h + min samples
- Feed learnings back into content generation
- See `SHARED_CONTEXT.md` for project-wide conventions

## Implementation

Create `/Users/howardli/Downloads/oyster/social/bluesky-poster/bluesky/ab_testing.py`:

```python
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from bluesky.content_engine import ContentEngine
from bluesky.content_db import ContentDB
import aiosqlite

logger = logging.getLogger(__name__)

class ABTesting:
    def __init__(self, content_engine: ContentEngine, content_db: ContentDB):
        self.content_engine = content_engine
        self.content_db = content_db
```

**Database Schema**:

```sql
CREATE TABLE IF NOT EXISTS ab_tests (
    test_id TEXT PRIMARY KEY,
    handle TEXT NOT NULL,
    post_type TEXT NOT NULL,
    topic TEXT,
    created_at TEXT NOT NULL,
    status TEXT DEFAULT 'active',  -- active, completed
    winner_variant TEXT
);

CREATE INDEX IF NOT EXISTS idx_ab_tests ON ab_tests(handle, status);

CREATE TABLE IF NOT EXISTS ab_variants (
    variant_id TEXT PRIMARY KEY,
    test_id TEXT NOT NULL,
    variant_name TEXT NOT NULL,  -- A, B, C
    text TEXT NOT NULL,
    post_uri TEXT,
    post_url TEXT,
    posted_at TEXT,
    likes INTEGER DEFAULT 0,
    reposts INTEGER DEFAULT 0,
    replies INTEGER DEFAULT 0,
    engagement_score REAL DEFAULT 0.0,
    FOREIGN KEY (test_id) REFERENCES ab_tests(test_id)
);
```

**Core Functions**:

```python
async def create_ab_test(
    self,
    handle: str,
    post_type: str,
    topic: Optional[str] = None,
    num_variants: int = 2
) -> str:
    """
    Create A/B test:
    1. Generate num_variants posts for same topic/type
    2. Create test record
    3. Create variant records
    4. Return test_id
    """

async def schedule_variants(
    self,
    test_id: str,
    delay_hours: int = 6
):
    """
    Schedule variants to post at different times:
    - Variant A: now
    - Variant B: +6h
    - Variant C: +12h (if 3 variants)
    """

async def check_winner(
    self,
    test_id: str,
    min_hours: int = 24,
    min_samples: int = 100
) -> Optional[str]:
    """
    Determine winner:
    1. Check if min_hours passed and min engagement samples reached
    2. Calculate engagement_score = likes + (2 * reposts) + (3 * replies)
    3. Statistical test (simple: >20% difference = significant)
    4. Mark winner, update test status
    5. Return winner variant_id or None if not ready
    """

async def get_active_tests(
    self,
    handle: str
) -> List[Dict]:
    """Get all active A/B tests for handle"""

async def get_learnings(
    self,
    handle: str,
    days: int = 30
) -> Dict[str, any]:
    """
    Extract learnings from completed tests:
    - Which post_types perform best
    - Which topics resonate
    - Optimal posting times
    Returns summary dict.
    """
```

**Winner Determination**:
- Min 24h after first variant posted
- Min 100 total engagement (likes + reposts + replies across variants)
- Statistical significance: winner has >20% higher engagement score than others

**CLI Integration**:
Add to `__main__.py`:
```python
async def cmd_ab_test(args):
    content_db = ContentDB()
    await content_db.init_db()
    queue = BlueskyQueue()
    await queue.init_db()
    content_engine = ContentEngine(queue=queue, rate_limiter=RateLimiter())

    ab_testing = ABTesting(content_engine=content_engine, content_db=content_db)

    if args.ab_sub == "create":
        test_id = await ab_testing.create_ab_test(
            handle=args.handle,
            post_type=args.post_type,
            num_variants=args.variants
        )
        print(f"Created A/B test: {test_id}")

    elif args.ab_sub == "status":
        tests = await ab_testing.get_active_tests(args.handle)
        for t in tests:
            winner = await ab_testing.check_winner(t['test_id'])
            print(f"{t['test_id']}: {t['status']}, winner: {winner or 'TBD'}")
```

## Tests

- `test_ab_testing.py`: Test variant generation
- Test winner determination logic
- Test learnings extraction

## Acceptance Criteria

- [ ] Generates 2-3 variants for same topic
- [ ] Schedules variants at different times
- [ ] Determines winner after min 24h + min samples
- [ ] Extracts learnings (best post types, topics)
- [ ] CLI command works: `python -m bluesky ab-test create --handle X --post-type question`
- [ ] Tests pass: `pytest tests/test_ab_testing.py -v`

## Do NOT

- Do not run >3 concurrent A/B tests per account (too much noise)
- Do not determine winner before 24h or min samples
- Do not use complex statistical tests (keep it simple)
