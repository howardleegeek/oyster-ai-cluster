---
task_id: S11-content-db
project: bluesky-poster
priority: 0
estimated_minutes: 35
depends_on: []
modifies: ["bluesky/content_db.py"]
executor: glm
---

## Goal

Content history and analytics database for tracking what was posted and engagement.

## Context

- Extends existing SQLite DB (same as queue.py uses)
- Tracks all generated content + engagement metrics
- Used by ab_testing and future analytics
- Stores reply history separately from original posts
- See `SHARED_CONTEXT.md` for project-wide conventions

## Implementation

Create `/Users/howardli/Downloads/oyster/social/bluesky-poster/bluesky/content_db.py`:

```python
import aiosqlite
import logging
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PostRecord:
    id: str
    handle: str
    text: str
    post_type: str  # vision, question, etc.
    posted_at: str
    uri: str
    url: str
    likes: int = 0
    reposts: int = 0
    replies: int = 0
    last_checked: Optional[str] = None

@dataclass
class ReplyRecord:
    id: str
    handle: str
    text: str
    replied_to_uri: str
    replied_to_author: str
    posted_at: str
    uri: str
    url: str
    likes: int = 0
    engagement_gained: int = 0  # Likes on reply

class ContentDB:
    def __init__(self, db_path: str = None):
        if db_path is None:
            import os
            db_path = os.path.expanduser("~/.bluesky-poster/queue.sqlite3")
        self.db_path = db_path
```

**Database Schema**:

```sql
CREATE TABLE IF NOT EXISTS content_history (
    id TEXT PRIMARY KEY,
    handle TEXT NOT NULL,
    text TEXT NOT NULL,
    post_type TEXT NOT NULL,
    posted_at TEXT NOT NULL,
    uri TEXT NOT NULL,
    url TEXT NOT NULL,
    likes INTEGER DEFAULT 0,
    reposts INTEGER DEFAULT 0,
    replies INTEGER DEFAULT 0,
    last_checked TEXT
);

CREATE INDEX IF NOT EXISTS idx_content_handle_date ON content_history(handle, posted_at);

CREATE TABLE IF NOT EXISTS reply_history (
    id TEXT PRIMARY KEY,
    handle TEXT NOT NULL,
    text TEXT NOT NULL,
    replied_to_uri TEXT NOT NULL,
    replied_to_author TEXT NOT NULL,
    posted_at TEXT NOT NULL,
    uri TEXT NOT NULL,
    url TEXT NOT NULL,
    likes INTEGER DEFAULT 0,
    engagement_gained INTEGER DEFAULT 0,
    last_checked TEXT
);

CREATE INDEX IF NOT EXISTS idx_reply_handle_date ON reply_history(handle, posted_at);

CREATE TABLE IF NOT EXISTS template_usage (
    template_id TEXT PRIMARY KEY,
    handle TEXT NOT NULL,
    post_type TEXT NOT NULL,
    times_used INTEGER DEFAULT 0,
    total_engagement INTEGER DEFAULT 0,
    avg_engagement REAL DEFAULT 0.0,
    last_used TEXT
);

CREATE INDEX IF NOT EXISTS idx_template_handle ON template_usage(handle, post_type);
```

**Core Functions**:

```python
async def init_db(self):
    """Initialize all content tracking tables"""

async def track_post(
    self,
    handle: str,
    text: str,
    post_type: str,
    uri: str,
    url: str
) -> str:
    """Record a posted original post, return record id"""

async def track_reply(
    self,
    handle: str,
    text: str,
    replied_to_uri: str,
    replied_to_author: str,
    uri: str,
    url: str
) -> str:
    """Record a posted reply, return record id"""

async def update_engagement(
    self,
    uri: str,
    likes: int,
    reposts: int = 0,
    replies: int = 0
):
    """Update engagement metrics for a post/reply"""

async def get_recent_posts(
    self,
    handle: str,
    days: int = 7,
    limit: int = 50
) -> List[PostRecord]:
    """Get recent posts for deduplication"""

async def get_top_posts(
    self,
    handle: str,
    limit: int = 10
) -> List[PostRecord]:
    """Get top performing posts by engagement"""

async def get_content_stats(
    self,
    handle: str,
    days: int = 30
) -> Dict[str, any]:
    """
    Get content stats:
    - Total posts
    - Total replies
    - Avg engagement by post_type
    - Best performing post_type
    """

async def track_template_usage(
    self,
    handle: str,
    template_id: str,
    post_type: str,
    engagement: int = 0
):
    """Track template usage and performance"""
```

**Engagement Refresh**:
Periodically fetch engagement from Bluesky using `client.get_post_thread()` and update DB.

## Tests

- `test_content_db.py`: Test all DB operations
- Test schema creation
- Test tracking posts and replies
- Test stats calculation

## Acceptance Criteria

- [ ] All tables created successfully
- [ ] track_post() and track_reply() insert correctly
- [ ] update_engagement() updates metrics
- [ ] get_recent_posts() returns last 7 days for dedup
- [ ] get_content_stats() calculates correct averages
- [ ] Tests pass: `pytest tests/test_content_db.py -v`

## Do NOT

- Do not create separate database file (use existing ~/.bluesky-poster/queue.sqlite3)
- Do not auto-refresh engagement on every query (manual refresh only)
- Do not track engagement for failed/draft posts
