---
task_id: S09-reply-engine
project: bluesky-poster
priority: 0
estimated_minutes: 45
depends_on: ["S05", "S07", "S08"]
modifies: ["bluesky/reply_engine.py"]
executor: glm
---

## Goal

High-frequency reply generation engine (THE MOST IMPORTANT MODULE). Reply-first strategy: 30-50 quality replies/day/account.

## Context

- Reference: `/Users/howardli/Downloads/oyster/social/twitter-poster/engagement_farmer.py` (full file)
- Reply-first strategy: 30-50 quality replies/day/account
- Discovery: search + timeline to find reply targets
- Filtering: min 1 like, prefer 10+ replies (not blown up yet), relevant topics
- Uses existing `bluesky/client.py` for search and timeline
- Uses existing `bluesky/queue.py` to enqueue replies
- See `SHARED_CONTEXT.md` for project-wide conventions

## Implementation

Create `/Users/howardli/Downloads/oyster/social/bluesky-poster/bluesky/reply_engine.py`:

```python
import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from bluesky.client import BlueskyClient
from bluesky.queue import BlueskyQueue
from bluesky.personas import get_persona, Persona
from bluesky.quality_gate import QualityGate
from bluesky.llm_client import generate_reply

logger = logging.getLogger(__name__)

class ReplyEngine:
    def __init__(self, client: BlueskyClient, queue: BlueskyQueue):
        self.client = client
        self.queue = queue
        self.quality_gate = QualityGate(min_score=0.7)
```

**Core Functions**:

```python
async def discover_targets(
    self,
    persona: Persona,
    limit: int = 100
) -> List[dict]:
    """
    Find posts to reply to using:
    1. client.search_posts() with persona keywords
    2. client.get_timeline() for timeline posts
    Combine and deduplicate.
    """

async def filter_targets(
    self,
    targets: List[dict],
    persona: Persona
) -> List[dict]:
    """
    Filter targets:
    - Min 1 like
    - Prefer 10+ replies (not viral yet)
    - Max age 48h
    - Not spam
    - Relevant to persona topics
    - Not already replied to by this account
    Return top 20 ranked by score.
    """

async def should_reply(
    self,
    post: dict,
    persona: Persona
) -> bool:
    """
    Decide if should reply based on:
    - Relevance to persona topics
    - Author credibility
    - Content quality
    Returns True/False.
    """

async def generate_and_enqueue_reply(
    self,
    post: dict,
    persona: Persona,
    dry_run: bool = False
) -> Optional[str]:
    """
    Generate reply using LLM:
    1. Call generate_reply(persona, post_text, post_author)
    2. Run through quality_gate
    3. If passes, enqueue via queue.enqueue(reply_to_uri=..., reply_to_cid=...)
    4. If fails quality, retry once with different temperature
    5. If still fails, skip (don't use template fallback for replies)
    Returns job_id if enqueued, None if skipped.
    """

async def run_reply_farm(
    self,
    handle: str,
    target_replies: int = 30,
    dry_run: bool = False
) -> Dict[str, int]:
    """
    Main reply farming loop:
    1. Load persona for handle
    2. Discover targets (100 posts)
    3. Filter to top 20
    4. For each target:
       - should_reply()
       - generate_and_enqueue_reply()
       - Stop when reached target_replies
    5. Return stats: {"discovered": N, "filtered": M, "enqueued": K}
    """
```

**Reply Scoring Algorithm**:
```python
def _score_target(self, post: dict, persona: Persona) -> float:
    """
    Score 0.0-1.0 based on:
    - Topic relevance (0-0.4): keyword match in post text
    - Engagement sweet spot (0-0.3): prefer 10-50 replies (not 0, not 1000)
    - Recency (0-0.2): prefer last 12h
    - Author quality (0-0.1): follower count, verified
    """
```

**CLI Integration**:
Add command to `__main__.py`:
```python
# reply-farm command
async def cmd_reply_farm(args):
    client = BlueskyClient(handle=args.handle, app_password=args.password)
    await client.login()
    queue = BlueskyQueue()
    await queue.init_db()

    engine = ReplyEngine(client=client, queue=queue)
    stats = await engine.run_reply_farm(
        handle=args.handle,
        target_replies=args.target,
        dry_run=args.dry_run
    )
    print(f"Reply farm stats: {stats}")
```

## Tests

- `test_reply_engine.py`: Mock client methods, test discovery + filtering
- Test should_reply() decision logic
- Test quality gate integration
- Test enqueue integration

## Acceptance Criteria

- [ ] Discovers 100+ posts via search + timeline
- [ ] Filters to top 20 targets ranked by score
- [ ] Generates replies that pass quality gate (70%+ pass rate)
- [ ] Enqueues replies with correct reply_to_uri and reply_to_cid
- [ ] CLI command works: `python -m bluesky reply-farm --handle X --target 30`
- [ ] Tests pass: `pytest tests/test_reply_engine.py -v`

## Do NOT

- Do not reply to posts older than 48h
- Do not reply to posts with 1000+ replies (already viral)
- Do not use template fallback for failed replies (skip instead)
- Do not reply to same post twice
