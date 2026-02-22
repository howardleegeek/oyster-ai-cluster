## Goal

Multi-account configuration and setup verification.

## Context

- Update accounts.json to include all 3 accounts
- Create accounts.json.example template
- Verify all accounts can login
- Update worker.py if needed for multi-account
- See `SHARED_CONTEXT.md` for project-wide conventions

## Implementation

**1. Update `/Users/howardli/Downloads/oyster/social/bluesky-poster/accounts.json`**:

```json
[
  {
    "handle": "oysterecosystem.bsky.social",
    "app_password": "XXXXX"
  },
  {
    "handle": "clawglasses.bsky.social",
    "app_password": "XXXXX"
  },
  {
    "handle": "puffyai.bsky.social",
    "app_password": "XXXXX"
  }
]
```

**2. Create `/Users/howardli/Downloads/oyster/social/bluesky-poster/accounts.json.example`**:

```json
[
  {
    "handle": "your-account.bsky.social",
    "app_password": "your-app-password-here"
  }
]
```

**3. Create setup verification script** `/Users/howardli/Downloads/oyster/social/bluesky-poster/verify_setup.py`:

```python
#!/usr/bin/env python3
"""Verify all accounts can login"""
import asyncio
import json
import sys
from bluesky.client import BlueskyClient

async def verify_accounts(accounts_path: str = "accounts.json"):
    with open(accounts_path) as f:
        accounts = json.load(f)

    results = []
    for account in accounts:
        handle = account["handle"]
        password = account["app_password"]

        client = BlueskyClient(handle=handle, app_password=password)
        success = await client.login()

        results.append({
            "handle": handle,
            "login_success": success,
            "did": client.did if success else None
        })

        if success:
            print(f"OK {handle}: login successful (DID: {client.did})")
        else:
            print(f"FAIL {handle}: login failed")

    all_success = all(r["login_success"] for r in results)
    if all_success:
        print(f"\nAll {len(results)} accounts verified successfully")
        return 0
    else:
        failed = [r["handle"] for r in results if not r["login_success"]]
        print(f"\n{len(failed)} accounts failed: {failed}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(verify_accounts()))
```

**4. Check worker.py multi-account support**:

Review `/Users/howardli/Downloads/oyster/social/bluesky-poster/bluesky/worker.py` lines 197-222.
The `_load_accounts()` method already supports multiple accounts from JSON.
Verify it works correctly:
- Loads all accounts from JSON
- Creates separate client for each
- claim_next() can handle jobs for any account

**5. Add README section**:

Create or update `/Users/howardli/Downloads/oyster/social/bluesky-poster/README.md` with setup instructions:

```markdown
## Setup

1. Copy `accounts.json.example` to `accounts.json`
2. Add your Bluesky handles and app passwords
3. Verify setup: `python3 verify_setup.py`
4. Run daemon: `python -m bluesky daemon --accounts accounts.json`

## Multi-Account Support

The poster supports multiple accounts simultaneously:
- Each account has its own persona (defined in `bluesky/personas.py`)
- Worker processes jobs for all accounts
- Rate limiter enforces per-account daily caps
- Content engine generates different content per account
```

## Tests

- `test_accounts_setup.py`: Test accounts.json parsing
- Test verify_setup.py with mock accounts
- Test worker multi-account loading

## Acceptance Criteria

- [ ] accounts.json has all 3 accounts (with placeholder passwords)
- [ ] accounts.json.example created
- [ ] verify_setup.py successfully verifies all accounts can login
- [ ] worker.py correctly handles multiple accounts
- [ ] README documents setup process
- [ ] Tests pass: `pytest tests/test_accounts_setup.py -v`

## Do NOT

- Do not commit real app passwords to git
- Do not modify worker.py unless multi-account handling is broken
- Do not add accounts beyond the 3 specified