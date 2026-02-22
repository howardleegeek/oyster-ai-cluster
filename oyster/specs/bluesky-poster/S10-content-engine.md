---
task_id: S10-content-engine
project: bluesky-poster
priority: 0
estimated_minutes: 40
depends_on: ["S05", "S06", "S07", "S08"]
modifies: ["bluesky/content_engine.py"]
executor: glm
---

## Goal

Original content generation engine (1-3 posts/day/account).

## Context

- Reference: `/Users/howardli/Downloads/oyster/social/bluesky-automation/content_engine.py` lines 243-end
- Uses personas + content_templates + llm_client
- Enforces content mix (25% emotional, 25% questions, etc.)
- Deduplicates against recent posts
- Schedules across peak hours
- See `SHARED_CONTEXT.md` for project-wide conventions

## Implementation

Create `/Users/howardli/Downloads/oyster/social/bluesky-poster/bluesky/content_engine.py`:

```python
import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from bluesky.personas import get_persona, Persona
from bluesky.content_templates import get_template, fill_template
from bluesky.quality_gate import QualityGate
from bluesky.llm_client import generate_post
from bluesky.queue import BlueskyQueue
from bluesky.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

class ContentEngine:
    def __init__(self, queue: BlueskyQueue, rate_limiter: RateLimiter):
        self.queue = queue
        self.rate_limiter = rate_limiter
        self.quality_gate = QualityGate(min_score=0.7)
        self.recent_posts = {}  # handle -> list of recent post texts for dedup
```

**Core Functions**:

```python
async def generate_post(
    self,
    persona: Persona,
    post_type: Optional[str] = None,
    topic: Optional[str] = None,
    use_llm: bool = True
) -> str:
    """
    Generate post:
    1. Select post_type based on content_mix if not provided
    2. If use_llm: call llm_client.generate_post()
    3. If LLM fails or use_llm=False: use template fallback
    4. Fill template variables if using template
    5. Run through quality_gate
    6. Return final post text
    """

def select_post_type(self, persona: Persona) -> str:
    """
    Select post type based on content_mix ratios.
    Use weighted random selection to match target mix.
    """

async def check_dedup(self, handle: str, text: str) -> bool:
    """
    Check if similar post was made recently (last 7 days).
    Use simple similarity: Levenshtein distance or jaccard similarity.
    Return True if duplicate, False if unique.
    """

async def schedule_post(
    self,
    persona: Persona,
    text: str,
    delay_minutes: int = 0
) -> str:
    """
    Schedule post by enqueueing with not_before timestamp.
    Spread posts across peak hours (8-10am, 8-11pm Beijing time).
    Returns job_id.
    """

async def generate_daily_content(
    self,
    handle: str,
    num_posts: int = 2,
    dry_run: bool = False
) -> List[str]:
    """
    Generate daily content:
    1. Load persona
    2. Generate num_posts posts with varied post_types
    3. Check dedup for each
    4. Schedule across day (peak hours)
    5. Return list of job_ids
    """
```

**Content Mix Enforcement**:
Track recent post types and adjust selection to match target ratios over time.

**Deduplication**:
Store last 50 posts per account in memory, check similarity before posting.

**CLI Integration**:
Add to `__main__.py`:
```python
async def cmd_content_gen(args):
    queue = BlueskyQueue()
    await queue.init_db()
    rate_limiter = RateLimiter()

    engine = ContentEngine(queue=queue, rate_limiter=rate_limiter)
    job_ids = await engine.generate_daily_content(
        handle=args.handle,
        num_posts=args.num_posts,
        dry_run=args.dry_run
    )
    print(f"Generated {len(job_ids)} posts: {job_ids}")
```

## Tests

- `test_content_engine.py`: Test post generation with templates
- Test content mix selection
- Test deduplication
- Test scheduling across peak hours

## Acceptance Criteria

- [ ] Generates posts matching persona content_mix ratios
- [ ] Deduplicates against recent posts (no repeats in 7 days)
- [ ] Schedules posts during peak hours (8-10am, 8-11pm Beijing)
- [ ] Falls back to templates if LLM fails
- [ ] CLI command works: `python -m bluesky content-gen --handle X --num-posts 3`
- [ ] Tests pass: `pytest tests/test_content_engine.py -v`

## Do NOT

- Do not generate more than 5 posts/day/account
- Do not post during off-peak hours unless explicitly requested
- Do not ignore content_mix ratios (track and enforce)
