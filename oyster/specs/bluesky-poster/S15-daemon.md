---
task_id: S15-daemon
project: bluesky-poster
priority: 0
estimated_minutes: 40
depends_on: ["S09", "S10", "S11", "S12", "S13"]
modifies: ["bluesky/daemon.py", "bluesky/__main__.py"]
executor: glm
---

## Goal

Main orchestration daemon coordinating all engines.

## Context

- Single long-running process
- Coordinates: trend detection, competitor tracking, content generation, reply farming, worker
- Configurable intervals
- Graceful shutdown
- See `SHARED_CONTEXT.md` for project-wide conventions

## Implementation

Create `/Users/howardli/Downloads/oyster/social/bluesky-poster/bluesky/daemon.py`:

```python
import asyncio
import logging
import signal
from datetime import datetime
from typing import Dict, List
from bluesky.client import BlueskyClient
from bluesky.queue import BlueskyQueue
from bluesky.rate_limiter import RateLimiter
from bluesky.worker import BlueskyWorker
from bluesky.reply_engine import ReplyEngine
from bluesky.content_engine import ContentEngine
from bluesky.content_db import ContentDB
from bluesky.trending import TrendDetector
from bluesky.competitor_tracker import CompetitorTracker
from bluesky.personas import list_personas

logger = logging.getLogger(__name__)

class BlueskyDaemon:
    def __init__(self, accounts_path: str = "accounts.json"):
        self.accounts_path = accounts_path
        self.stop_event = asyncio.Event()
        self.clients: Dict[str, BlueskyClient] = {}
        self.queue = BlueskyQueue()
        self.rate_limiter = RateLimiter()
        self.content_db = ContentDB()
```

**Core Loop**:

```python
async def run(self):
    """
    Main daemon loop:
    1. Load accounts and personas
    2. Initialize all engines
    3. Start worker in background
    4. Run scheduled tasks:
       - Every 1h: trend detection
       - Every 4h: competitor tracking
       - Every 6h: content generation (1-3 posts/account)
       - Every 30min: reply farming (5-10 replies/account)
       - Every 10min: refresh analytics
    5. Handle graceful shutdown
    """

async def _load_accounts(self) -> List[Dict]:
    """Load accounts from accounts.json"""

async def _init_engines(self):
    """Initialize all engines for all accounts"""

async def _run_trend_detection(self):
    """Run trend detection for all accounts"""

async def _run_competitor_tracking(self):
    """Track all competitors for all accounts"""

async def _run_content_generation(self):
    """Generate 1-3 original posts per account"""

async def _run_reply_farming(self):
    """Generate 5-10 replies per account"""

async def _refresh_analytics(self):
    """Refresh engagement metrics from Bluesky"""

async def _start_worker(self):
    """Start worker in background task"""

async def stop(self):
    """Graceful shutdown"""
```

**Schedule Configuration**:

```python
SCHEDULE = {
    "trend_detection": 3600,  # 1h
    "competitor_tracking": 14400,  # 4h
    "content_generation": 21600,  # 6h
    "reply_farming": 1800,  # 30min
    "analytics_refresh": 600,  # 10min
}
```

**Error Handling**:
- Log all errors, don't crash daemon
- Skip failed tasks, continue with next
- Retry transient errors (network)

**CLI Integration**:
Update `/Users/howardli/Downloads/oyster/social/bluesky-poster/bluesky/__main__.py`:

```python
# Add daemon command
daemon_parser = subparsers.add_parser("daemon", help="Run orchestration daemon")
daemon_parser.add_argument("--accounts", default="accounts.json", help="Accounts file")
daemon_parser.add_argument("--config", help="Daemon config file")

# Add handler
elif args.command == "daemon":
    from bluesky.daemon import BlueskyDaemon
    daemon = BlueskyDaemon(accounts_path=args.accounts)

    # Signal handling
    loop = asyncio.get_event_loop()
    for sig in ("SIGINT", "SIGTERM"):
        try:
            loop.add_signal_handler(
                getattr(signal, sig),
                lambda: asyncio.create_task(daemon.stop())
            )
        except NotImplementedError:
            pass

    asyncio.run(daemon.run())
```

## Tests

- `test_daemon.py`: Test daemon initialization
- Test task scheduling
- Test graceful shutdown
- Mock all engines

## Acceptance Criteria

- [ ] Loads all accounts and initializes engines
- [ ] Runs all scheduled tasks at correct intervals
- [ ] Worker processes queue jobs continuously
- [ ] Graceful shutdown on SIGINT/SIGTERM
- [ ] CLI command works: `python -m bluesky daemon --accounts accounts.json`
- [ ] Tests pass: `pytest tests/test_daemon.py -v`

## Do NOT

- Do not run tasks more frequently than specified (rate limits)
- Do not crash daemon on single task failure (log and continue)
- Do not start multiple workers (one worker per daemon)
