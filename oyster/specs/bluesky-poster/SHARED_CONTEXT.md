# Bluesky-Poster Shared Context

## Project Path
`/Users/howardli/Downloads/oyster/social/bluesky-poster/`

## Runtime Requirements
- Python 3.11+, asyncio, type hints everywhere
- Package structure: `bluesky/` is an importable Python package

## Dependencies
- `atproto` - Bluesky AT Protocol client (`pip install atproto`)
- `aiosqlite` - Async SQLite access
- `python-dateutil` - Date parsing utilities
- `httpx` - HTTP client (async, for LLM API calls)
- CLI: argparse (no click/typer, zero extra deps)

## Authentication
- atproto SDK: `client = AsyncClient(); await client.login(handle, app_password)`
- **App Password** format: `xxxx-xxxx-xxxx-xxxx` (from bsky.app Settings -> Dev -> App Password)
- Account config read from `accounts.json`

## Database
- SQLite DB path: `~/.bluesky-poster/queue.sqlite3` (shared across all modules)
- All new tables go in the same DB file
- Use aiosqlite for all DB operations
- Write operations use `BEGIN IMMEDIATE` to avoid concurrency conflicts

## Rate Limiting
- Daily cap: 120 posts + 50 replies / account
- Inter-post delay: 75-240s random
- Peak hours (Beijing UTC+8): 8-10, 20-23
- API limits (Bluesky official): 5000 points/hour, 35000/day

## File Layout
- All new source files go in `bluesky/` subdirectory
- All new test files go in `tests/` subdirectory
- Test file naming: `tests/test_<module_name>.py`
- Each spec creates max 3 new files

## DO NOT Modify These Existing Files
- `bluesky/client.py` - Bluesky API client (use as-is)
- `bluesky/queue.py` - Job queue (use as-is)
- `bluesky/worker.py` - Queue worker (use as-is, unless S16 requires multi-account fix)
- `bluesky/rate_limiter.py` - Rate limiting (use as-is)

## Code Style
- Black formatted (line length 88)
- Type hints on all function signatures
- Use kwargs (not positional arguments)
- Use `logging` module (not print) for operational output
- `logger = logging.getLogger(__name__)` at top of each module
- All IO operations must be async def
- Exceptions must be caught and logged, no bare except
- Do not hardcode paths, use `Path.home() / ".bluesky-poster"`
- Do not import modules from specs not yet written (use TYPE_CHECKING or lazy import)

## Environment Variables
- `ANTHROPIC_API_KEY` - Required for LLM calls (S08-llm-client)
- Account credentials stored in `accounts.json` (not env vars)

## Accounts
Three accounts supported:
1. `oysterecosystem.bsky.social` - Community voice
2. `clawglasses.bsky.social` - Technical builder
3. `puffyai.bsky.social` - AI power user

## Test Conventions

### Mock Strategy
```python
# Use unittest.mock
from unittest.mock import AsyncMock, MagicMock, patch

# Client mock
@pytest.fixture
def mock_client():
    client = AsyncMock(spec=BlueskyClient)
    client.post.return_value = PostResult(uri="at://...", cid="...", url="https://...", author_did="did:plc:xxx", timestamp="2024-01-01T00:00:00Z")
    return client

# Queue mock
@pytest.fixture
def mock_queue():
    queue = AsyncMock(spec=BlueskyQueue)
    queue.claim_next.return_value = test_job
    return queue
```

### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific module tests
pytest tests/test_client.py -v

# With coverage
pytest tests/ --cov=bluesky --cov-report=term-missing
```

## Dependency DAG (S05-S16)

```
Phase 1 (Foundation - all parallel):
├── S05-persona-config
├── S06-content-templates
├── S07-quality-gate
└── S08-llm-client

Phase 2 (Engines - parallel after Phase 1):
├── S09-reply-engine (depends: S05, S07, S08)
├── S10-content-engine (depends: S05, S06, S07, S08)
└── S11-content-db (depends: none - parallel)

Phase 3 (Intelligence - parallel after Phase 2):
├── S12-trend-detector (depends: S10)
├── S13-competitor-tracker (depends: none - parallel)
└── S14-ab-testing (depends: S10, S11)

Phase 4 (Orchestration - depends on all):
├── S15-daemon (depends: S09, S10, S11, S12, S13)
└── S16-accounts-setup (depends: S15)
```

## Integration Points

### Queue Integration
- `reply_engine.py` enqueues via `queue.enqueue(reply_to_uri=..., reply_to_cid=...)`
- `content_engine.py` enqueues via `queue.enqueue(text=..., not_before=...)`
- `worker.py` processes all jobs via `queue.claim_next()`

### Client Integration
- All engines use `BlueskyClient` for API calls
- `reply_engine`: `search_posts()`, `get_timeline()`, `get_post_thread()`
- `trend_detector`: `search_posts()`
- `competitor_tracker`: `get_profile()`

### LLM Integration
- `reply_engine` calls `llm_client.generate_reply()`
- `content_engine` calls `llm_client.generate_post()`
- Fallback to templates if LLM fails

## Existing File Map
```
bluesky/
  __init__.py
  client.py        # S01 - Bluesky API client
  queue.py         # S02 - Job queue
  worker.py        # S03 - Queue worker
  rate_limiter.py  # S04 - Rate limiting
  trending.py      # S07/S12 - Trending tags + detector
  __main__.py      # CLI entry point
accounts.json      # Account credentials
tests/             # Test files (each spec must have tests)
```

## Common Error Checklist
- [ ] Constructor params use kwargs not positional
- [ ] DB operations are async, writes use transactions
- [ ] Do not hardcode paths, use Path.home() / ".bluesky-poster"
- [ ] Exceptions caught and logged, no bare except
- [ ] Do not import modules from unwritten specs (use TYPE_CHECKING or lazy import)
