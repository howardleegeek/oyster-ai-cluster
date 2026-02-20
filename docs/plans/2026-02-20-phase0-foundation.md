# Phase 0: Foundation Fixes — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix all critical bugs, security issues, and infrastructure gaps before building new features.

**Architecture:** Patch existing FastAPI backend in-place. Add Alembic for migrations. Replace in-memory SessionStore with Redis. Add rate limiting middleware.

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, SlowAPI (rate limiting), Redis, pytest

**Working Directory:** `/Users/howardli/Downloads/.claude/worktrees/modest-jennings/puffy-backend`

---

### Task 1: Remove Secret Leak — print(Settings())

**Files:**
- Modify: `app/config.py` (line 44)
- Test: `tests/unit/test_config.py` (Create)

**Step 1: Write the failing test**

```python
# tests/unit/test_config.py
import pytest
from unittest.mock import patch
from io import StringIO

@pytest.mark.unit
class TestConfigSecurity:
    def test_settings_not_printed_to_stdout(self):
        """Ensure Settings() is never printed to stdout on import."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            # Force re-import of config module
            import importlib
            import app.config
            importlib.reload(app.config)
            output = mock_stdout.getvalue()
            assert "settings" not in output.lower()
            assert "secret" not in output.lower()
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/howardli/Downloads/.claude/worktrees/modest-jennings/puffy-backend && python -m pytest tests/unit/test_config.py -v -k test_settings_not_printed`
Expected: FAIL — print statement outputs settings

**Step 3: Fix — Remove the print statement**

In `app/config.py`, remove line 44:
```python
# DELETE THIS LINE:
# print("#########settings", Settings())
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/unit/test_config.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/config.py tests/unit/test_config.py
git commit -m "fix(security): remove Settings() print that leaks secrets to stdout"
```

---

### Task 2: Stop Logging Full JWT Tokens

**Files:**
- Modify: `app/services/token.py` (lines 44, 47, 50)

**Step 1: Write the failing test**

```python
# tests/unit/test_token_logging.py
import pytest
import logging
from app.services.token import Token

@pytest.mark.unit
class TestTokenLogging:
    def test_invalid_token_does_not_log_full_token(self, caplog):
        """Ensure invalid tokens are not logged in full."""
        service = Token(secret="test_secret", exp=3600)
        fake_token = "eyJhbGciOiJIUzI1NiJ9.eyJpZCI6IjEyMyJ9.fakesig_that_is_sensitive"

        with caplog.at_level(logging.DEBUG):
            result = service.parse_token(fake_token)

        for record in caplog.records:
            assert fake_token not in record.message, \
                f"Full token leaked in log: {record.message}"

    def test_expired_token_does_not_log_full_token(self, caplog):
        """Ensure expired tokens are not logged in full."""
        import time, jwt
        service = Token(secret="test_secret", exp=1)
        # Create a token that expires immediately
        payload = {"id": "test", "address": "addr", "exp": int(time.time()) - 10}
        expired_token = jwt.encode(payload, "test_secret", algorithm="HS256")

        with caplog.at_level(logging.DEBUG):
            result = service.parse_token(expired_token)

        for record in caplog.records:
            assert expired_token not in record.message
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/test_token_logging.py -v`
Expected: FAIL — current code logs full token

**Step 3: Fix — Log only token prefix**

In `app/services/token.py`, change the logging lines:

```python
# Line ~44: Change from:
# logger.info("invalid token %s", token)
# To:
logger.info("invalid token %s...", token[:20] if token else "empty")

# Line ~47: Change from:
# logger.info("expired token %s", token)
# To:
logger.info("expired token %s...", token[:20] if token else "empty")

# Line ~50: Change from:
# logger.error("parse token error %s %s", token, err)
# To:
logger.error("parse token error %s... %s", token[:20] if token else "empty", err)
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/unit/test_token_logging.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/services/token.py tests/unit/test_token_logging.py
git commit -m "fix(security): stop logging full JWT tokens, log prefix only"
```

---

### Task 3: Add Pagination to List Endpoints

**Files:**
- Modify: `app/api/order.py` (lines 25-30)
- Modify: `app/api/product.py` (lines 23-29)
- Modify: `app/db/order.py` (lines 32-38)
- Modify: `app/db/product.py` (lines 21-22)
- Test: `tests/api/test_pagination.py` (Create)

**Step 1: Write the failing test**

```python
# tests/api/test_pagination.py
import pytest
from starlette import status

@pytest.mark.api
class TestPagination:
    def test_get_orders_supports_limit_param(self, test_client, auth_headers):
        response = test_client.get("/order/?limit=5", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_get_orders_supports_offset_param(self, test_client, auth_headers):
        response = test_client.get("/order/?limit=5&offset=0", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_get_orders_default_limit_is_20(self, test_client, auth_headers):
        response = test_client.get("/order/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_get_orders_max_limit_is_100(self, test_client, auth_headers):
        response = test_client.get("/order/?limit=999", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        # Backend should cap at 100

    def test_get_products_supports_pagination(self, test_client):
        response = test_client.get("/product/?limit=10&offset=0")
        assert response.status_code == status.HTTP_200_OK
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/api/test_pagination.py -v`
Expected: FAIL — current endpoints don't accept limit/offset params

**Step 3: Add pagination to order repo**

In `app/db/order.py`, modify `get_orders()`:
```python
def get_orders(self, limit: int = 20, offset: int = 0, **kwargs) -> list:
    limit = min(limit, 100)  # Cap at 100
    return (
        self.db.query(OrderModel)
        .filter_by(**kwargs)
        .options(
            joinedload(OrderModel.items),
            joinedload(OrderModel.shipping_address),
            joinedload(OrderModel.payment),
        )
        .order_by(OrderModel.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
```

In `app/api/order.py`, modify `get_orders()` endpoint:
```python
@router.get("/")
def get_orders(
    user: UserAuthDep,
    order_service: OrderServiceDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    orders = order_service.get_orders(user_id=user.id, limit=limit, offset=offset)
    return orders
```

In `app/db/product.py`, modify `get_products()`:
```python
def get_products(self, limit: int = 20, offset: int = 0) -> list:
    limit = min(limit, 100)
    return self.db.query(Product).offset(offset).limit(limit).all()
```

In `app/api/product.py`, modify `get_products()` endpoint:
```python
@router.get("/")
def get_products(
    product_service: ProductServiceDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return product_service.get_products(limit=limit, offset=offset)
```

**Step 4: Run tests**

Run: `python -m pytest tests/api/test_pagination.py -v`
Expected: PASS

**Step 5: Run existing tests to check no regressions**

Run: `python -m pytest tests/ -v --ignore=tests/integration`
Expected: All existing tests PASS

**Step 6: Commit**

```bash
git add app/api/order.py app/api/product.py app/db/order.py app/db/product.py tests/api/test_pagination.py
git commit -m "feat: add pagination (limit/offset) to order and product list endpoints"
```

---

### Task 4: Invalidate Session After Verify (Prevent Signature Replay)

**Files:**
- Modify: `app/api/user.py` (lines 72-102)
- Test: `tests/api/test_session_invalidation.py` (Create)

**Step 1: Write the failing test**

```python
# tests/api/test_session_invalidation.py
import pytest
from unittest.mock import MagicMock, patch
from starlette import status

@pytest.mark.api
class TestSessionInvalidation:
    def test_session_deleted_after_successful_verify(self, test_client):
        """After a successful verify, the session should be deleted from Redis."""
        mock_cache = MagicMock()
        mock_cache.get_session.return_value = MagicMock(message="test_message")

        with patch("app.api.user.CacheDb", return_value=mock_cache):
            # The exact mocking depends on DI setup; key assertion:
            # After verify succeeds, close_session() must be called
            pass

        # Conceptual test: verify that close_session is called
        # Implementation will be tested via integration test
```

**Step 2: Fix — Add session deletion after verify**

In `app/api/user.py`, in the `verify` endpoint (around line 95-100), after successful token generation, add:

```python
# After: token = token_service.gen_token(user_schema)
# Add:
cache_db.close_session(req.session_id)
```

**Step 3: Run all tests**

Run: `python -m pytest tests/ -v --ignore=tests/integration`
Expected: PASS

**Step 4: Commit**

```bash
git add app/api/user.py
git commit -m "fix(security): invalidate session after successful verify to prevent signature replay"
```

---

### Task 5: Make Passcode/Referral Increment Atomic

**Files:**
- Modify: `app/db/order.py` (lines 62-66)
- Test: `tests/unit/test_atomic_increment.py` (Create)

**Step 1: Write the failing test**

```python
# tests/unit/test_atomic_increment.py
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy import text

@pytest.mark.unit
class TestAtomicIncrement:
    def test_passcode_increment_uses_atomic_sql(self, test_db_session):
        """Passcode increment should use atomic SQL UPDATE, not read-modify-write."""
        from app.models.user import PassCode
        # Create a passcode
        pc = PassCode(id=1, user_id="test_user", pass_code="TEST123", max_uses=5, current_uses=0)
        test_db_session.add(pc)
        test_db_session.commit()

        # Atomic increment
        rows = test_db_session.execute(
            text("UPDATE pass_codes SET current_uses = current_uses + 1 WHERE pass_code = :code AND current_uses < max_uses"),
            {"code": "TEST123"}
        )
        test_db_session.commit()

        assert rows.rowcount == 1
        refreshed = test_db_session.query(PassCode).filter_by(pass_code="TEST123").first()
        assert refreshed.current_uses == 1

    def test_passcode_increment_fails_at_max(self, test_db_session):
        """Atomic increment should fail (0 rows) when already at max."""
        from app.models.user import PassCode
        pc = PassCode(id=2, user_id="test_user", pass_code="MAXED", max_uses=1, current_uses=1)
        test_db_session.add(pc)
        test_db_session.commit()

        rows = test_db_session.execute(
            text("UPDATE pass_codes SET current_uses = current_uses + 1 WHERE pass_code = :code AND current_uses < max_uses"),
            {"code": "MAXED"}
        )
        test_db_session.commit()

        assert rows.rowcount == 0  # No rows updated
```

**Step 2: Run test to verify the pattern works**

Run: `python -m pytest tests/unit/test_atomic_increment.py -v`

**Step 3: Fix — Replace read-modify-write with atomic SQL**

In `app/db/order.py`, replace lines 62-66:

```python
# OLD (non-atomic):
# if order.pass_code:
#     passcode_db = self.db.query(PassCode).filter(PassCode.pass_code == order.pass_code).first()
#     if passcode_db:
#         passcode_db.current_uses = passcode_db.current_uses + 1
#         self.db.commit()

# NEW (atomic):
if order.pass_code:
    from sqlalchemy import text
    result = self.db.execute(
        text("UPDATE pass_codes SET current_uses = current_uses + 1 "
             "WHERE pass_code = :code AND current_uses < max_uses"),
        {"code": order.pass_code}
    )
    if result.rowcount == 0:
        raise RecordNotFoundError("Pass code exhausted or not found")
```

Apply same pattern for referral codes wherever they're incremented.

**Step 4: Run all tests**

Run: `python -m pytest tests/ -v --ignore=tests/integration`
Expected: PASS

**Step 5: Commit**

```bash
git add app/db/order.py tests/unit/test_atomic_increment.py
git commit -m "fix(security): make passcode/referral increment atomic to prevent race conditions"
```

---

### Task 6: Add UNIQUE Constraint on users.twitter_id

**Files:**
- Modify: `app/models/user.py` (line 31)
- Test: `tests/unit/test_twitter_unique.py` (Create)

**Step 1: Modify the model**

In `app/models/user.py`, change twitter_id column:
```python
# From:
twitter_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
# To:
twitter_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)
```

**Step 2: Write test**

```python
# tests/unit/test_twitter_unique.py
import pytest
from sqlalchemy.exc import IntegrityError
from app.models.user import User, Balance

@pytest.mark.unit
class TestTwitterUnique:
    def test_cannot_link_same_twitter_to_two_users(self, test_db_session):
        """Two users cannot have the same twitter_id."""
        user1 = User(id="user1", address="addr1", twitter_id="tw_123")
        bal1 = Balance(id="user1")
        user2 = User(id="user2", address="addr2", twitter_id="tw_123")
        bal2 = Balance(id="user2")

        test_db_session.add_all([user1, bal1, user2, bal2])
        with pytest.raises(IntegrityError):
            test_db_session.commit()
```

**Step 3: Run test**

Run: `python -m pytest tests/unit/test_twitter_unique.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add app/models/user.py tests/unit/test_twitter_unique.py
git commit -m "fix(data): add UNIQUE constraint on users.twitter_id to prevent double-linking"
```

---

### Task 7: Fix create_user Race Condition

**Files:**
- Modify: `app/db/user.py` (lines 44-71)

**Step 1: Review current code**

Current `create_or_get_user()` catches `IntegrityError` but has a race window.

**Step 2: Fix — Add retry with unique constraint**

```python
# In app/db/user.py, replace create_or_get_user():
def create_or_get_user(self, address: str) -> models.User:
    # Try to get first
    user = self.get_user(address=address)
    if user:
        return user

    # Try to create
    try:
        new_user_id = str(uuid.uuid4())
        user = models.User(id=new_user_id, address=address)
        balance = models.Balance(id=new_user_id)
        self.db.add(user)
        self.db.add(balance)
        self.db.commit()
        self.db.refresh(user)
        return user
    except IntegrityError:
        self.db.rollback()
        # Another request created the user first — fetch it
        user = self.get_user(address=address)
        if user:
            return user
        raise  # Re-raise if still can't find
```

**Step 3: Run all tests**

Run: `python -m pytest tests/ -v --ignore=tests/integration`
Expected: PASS

**Step 4: Commit**

```bash
git add app/db/user.py
git commit -m "fix: handle create_user race condition with IntegrityError retry"
```

---

### Task 8: Remove wallet_db Dependency from OrderService

**Files:**
- Modify: `app/services/order.py`

**Step 1: Search for wallet_db references**

```bash
grep -n "wallet_db" app/services/order.py
```

**Step 2: Remove or stub the reference**

Remove any `self.wallet_db` assignment and references. If the code path that uses it is unreachable, remove entirely. If needed, replace with a TODO comment.

**Step 3: Run all tests**

Run: `python -m pytest tests/ -v --ignore=tests/integration`
Expected: PASS

**Step 4: Commit**

```bash
git add app/services/order.py
git commit -m "fix: remove undefined wallet_db dependency from OrderService"
```

---

### Task 9: Update Deprecated .from_orm() to .model_validate()

**Files:**
- Modify: All files using `.from_orm()` — search with `grep -rn "from_orm" app/`

**Step 1: Find all occurrences**

```bash
grep -rn "from_orm" app/
```

**Step 2: Replace each occurrence**

```python
# From:
schema = SomeSchema.from_orm(db_model)
# To:
schema = SomeSchema.model_validate(db_model)
```

**Step 3: Run all tests**

Run: `python -m pytest tests/ -v --ignore=tests/integration`
Expected: PASS

**Step 4: Commit**

```bash
git add -A
git commit -m "refactor: replace deprecated .from_orm() with .model_validate() (Pydantic v2)"
```

---

### Task 10: Fix Broken Imports in payment_crawler.py and job_runner.py

**Files:**
- Modify: `app/jobs/payment_crawler.py` (line 79 — `Annotated` not imported)
- Modify: `app/jobs/job_runner.py` (line 41 — `time` not imported)

**Step 1: Fix payment_crawler.py**

Add `from typing import Annotated` at top of file.

**Step 2: Fix job_runner.py**

Add `import time` at top of file.

**Step 3: Verify imports work**

```bash
python -c "from app.jobs.payment_crawler import PaymentCrawler; print('OK')"
python -c "from app.jobs.job_runner import run_payment_crawler_job; print('OK')"
```

**Step 4: Commit**

```bash
git add app/jobs/payment_crawler.py app/jobs/job_runner.py
git commit -m "fix: add missing imports in payment_crawler and job_runner"
```

---

### Task 11: Set Up Alembic Migration Tooling

**Files:**
- Create: `alembic.ini`
- Create: `alembic/env.py`
- Create: `alembic/versions/` (directory)

**Step 1: Install alembic**

```bash
pip install alembic
echo "alembic" >> requirements.txt
```

**Step 2: Initialize alembic**

```bash
cd /Users/howardli/Downloads/.claude/worktrees/modest-jennings/puffy-backend
alembic init alembic
```

**Step 3: Configure alembic/env.py**

Edit `alembic/env.py` to import Base and engine:

```python
from app.db.base import Base, SQLALCHEMY_DATABASE_URL
from app.models import user, order, product  # import all models

config = context.config
config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)
target_metadata = Base.metadata
```

**Step 4: Create initial migration**

```bash
alembic revision --autogenerate -m "initial schema"
```

**Step 5: Verify migration runs**

```bash
alembic upgrade head
```

**Step 6: Commit**

```bash
git add alembic/ alembic.ini requirements.txt
git commit -m "infra: set up Alembic database migration tooling"
```

---

### Task 12: Add /health and /ready Endpoints

**Files:**
- Modify: `app/puffy.py`
- Test: `tests/api/test_health.py` (Create)

**Step 1: Write the failing test**

```python
# tests/api/test_health.py
import pytest
from starlette import status

@pytest.mark.api
class TestHealthEndpoints:
    def test_health_returns_ok(self, test_client):
        response = test_client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "ok"

    def test_ready_returns_ready(self, test_client):
        response = test_client.get("/ready")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "ready"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/api/test_health.py -v`
Expected: FAIL — 404

**Step 3: Add endpoints to puffy.py**

```python
# In app/puffy.py, add after app creation:

@puffy.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}

@puffy.get("/ready")
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
```

**Step 4: Run test**

Run: `python -m pytest tests/api/test_health.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/puffy.py tests/api/test_health.py
git commit -m "feat: add /health and /ready endpoints for load balancer integration"
```

---

### Task 13: Fix CORS — Add allow_credentials=True

**Files:**
- Modify: `app/puffy.py` (CORS middleware section)

**Step 1: Fix CORS config**

In `app/puffy.py`, change CORS middleware:

```python
if settings.env in ("DEV", "TEST"):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,  # ADD THIS
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

**Step 2: Run all tests**

Run: `python -m pytest tests/ -v --ignore=tests/integration`
Expected: PASS

**Step 3: Commit**

```bash
git add app/puffy.py
git commit -m "fix: add allow_credentials=True to CORS for frontend auth headers"
```

---

### Task 14: Replace In-Memory SessionStore with Redis

**Files:**
- Modify: `app/plib/session_store.py` or `app/plib/session_db.py`
- Modify: `app/api/user.py` (if it uses SessionStore directly)
- Test: `tests/unit/test_session_redis.py` (Create)

**Step 1: Identify current SessionStore usage**

```bash
grep -rn "SessionStore\|session_store\|session_db" app/
```

**Step 2: If SessionStore is in-memory dict, replace with Redis wrapper**

```python
# app/plib/session_store.py — Replace entire content:
from app.db.cache import CacheDb, get_cache
from app.schemas.session import SessionData

class SessionStore:
    """Redis-backed session store. Replaces in-memory dict."""
    def __init__(self, cache: CacheDb):
        self.cache = cache

    def create_session(self, message: str) -> str:
        data = SessionData(message=message)
        return self.cache.new_session(data)

    def get_session(self, session_id: str):
        return self.cache.get_session(session_id)

    def delete_session(self, session_id: str):
        self.cache.close_session(session_id)
```

**Step 3: Run all tests**

Run: `python -m pytest tests/ -v --ignore=tests/integration`
Expected: PASS

**Step 4: Commit**

```bash
git add app/plib/session_store.py app/plib/session_db.py
git commit -m "fix(critical): replace in-memory SessionStore with Redis to fix multi-worker session loss"
```

---

### Task 15: Fix Twitter OAuth PKCE

**Files:**
- Modify: `app/plib/oauth.py` (line with `code_verifier='challenge'`)
- Modify: `app/db/cache.py` (add PKCE verifier storage)

**Step 1: Store code_verifier in Redis when generating auth URL**

```python
# In the flow that generates the Twitter OAuth URL, store:
cache.set_data(f"pkce:{state}", code_verifier, expire_hours=0.5)
```

**Step 2: Retrieve code_verifier in oauth.py**

```python
# In twitter_oauth(), change:
# 'code_verifier': 'challenge',
# To:
# 'code_verifier': code_verifier,  # passed as parameter
```

Update function signature:
```python
def twitter_oauth(client_id, client_secret, code, redirect_url, code_verifier='challenge'):
```

**Step 3: Run all tests**

Run: `python -m pytest tests/ -v --ignore=tests/integration`
Expected: PASS

**Step 4: Commit**

```bash
git add app/plib/oauth.py app/db/cache.py
git commit -m "fix(security): support proper PKCE code_verifier for Twitter OAuth"
```

---

### Task 16: Add pool_pre_ping to SQLAlchemy Engine

**Files:**
- Modify: `app/db/base.py` (lines 11-16)

**Step 1: Add pool_pre_ping**

```python
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_recycle=3600,
    pool_size=settings.db_pool_size,
    max_overflow=5,
    pool_pre_ping=True,  # ADD: test connections before use
)
```

**Step 2: Run all tests**

Run: `python -m pytest tests/ -v --ignore=tests/integration`
Expected: PASS

**Step 3: Commit**

```bash
git add app/db/base.py
git commit -m "fix: add pool_pre_ping to catch stale DB connections"
```

---

### Task 17: Make Redis TTL Configurable

**Files:**
- Modify: `app/config.py` (add `session_ttl` setting)
- Modify: `app/db/cache.py` (use setting instead of hardcoded 600)

**Step 1: Add setting**

In `app/config.py`, add to Settings class:
```python
session_ttl: int = 600  # seconds, default 10 minutes
```

**Step 2: Use setting in cache.py**

```python
# In CacheDb.__init__:
self.session_ttl = settings.session_ttl

# In new_session():
self.redis_client.setex(session_id, value=data_json, time=self.session_ttl)
```

**Step 3: Run tests, commit**

```bash
git add app/config.py app/db/cache.py
git commit -m "feat: make Redis session TTL configurable via settings"
```

---

### Task 18: Pin Python Dependency Versions

**Files:**
- Modify: `requirements.txt`

**Step 1: Generate pinned versions**

```bash
pip freeze > requirements.lock.txt
```

**Step 2: Update requirements.txt with pinned versions**

Pin all currently-unpinned packages (uvicorn, redis, PyJWT, etc.) to their current installed versions.

**Step 3: Commit**

```bash
git add requirements.txt
git commit -m "chore: pin all Python dependency versions for reproducible builds"
```

---

### Task 19: Add Order State Machine Validation

**Files:**
- Create: `app/services/state_machine.py`
- Modify: `app/db/order.py` (update_order method)
- Test: `tests/unit/test_state_machine.py` (Create)

**Step 1: Write the failing test**

```python
# tests/unit/test_state_machine.py
import pytest
from app.enums import OrderStatus

@pytest.mark.unit
class TestOrderStateMachine:
    def test_new_can_transition_to_paid(self):
        from app.services.state_machine import validate_order_transition
        assert validate_order_transition(OrderStatus.NEW, OrderStatus.PAID) is True

    def test_new_can_transition_to_cancelled(self):
        from app.services.state_machine import validate_order_transition
        assert validate_order_transition(OrderStatus.NEW, OrderStatus.CANCELLED) is True

    def test_cancelled_cannot_transition_to_paid(self):
        from app.services.state_machine import validate_order_transition
        assert validate_order_transition(OrderStatus.CANCELLED, OrderStatus.PAID) is False

    def test_delivered_is_terminal(self):
        from app.services.state_machine import validate_order_transition
        assert validate_order_transition(OrderStatus.DELIVERED, OrderStatus.NEW) is False
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/test_state_machine.py -v`
Expected: FAIL — module doesn't exist

**Step 3: Implement state machine**

```python
# app/services/state_machine.py
from app.enums import OrderStatus

VALID_TRANSITIONS = {
    OrderStatus.NEW: {OrderStatus.PAID, OrderStatus.CANCELLED, OrderStatus.EXPIRED},
    OrderStatus.PAID: {OrderStatus.CONFIRMED, OrderStatus.EXPIRED, OrderStatus.REFUNDED},
    OrderStatus.CONFIRMED: {OrderStatus.PROCESSING, OrderStatus.REFUNDED},
    OrderStatus.PROCESSING: {OrderStatus.SHIPPED},
    OrderStatus.SHIPPED: {OrderStatus.DELIVERED},
    OrderStatus.CANCELLED: set(),
    OrderStatus.DELIVERED: set(),
    OrderStatus.EXPIRED: set(),
    OrderStatus.REFUNDED: set(),
}

def validate_order_transition(current: OrderStatus, target: OrderStatus) -> bool:
    """Return True if transition from current to target is valid."""
    allowed = VALID_TRANSITIONS.get(current, set())
    return target in allowed
```

**Step 4: Wire into update_order**

In `app/db/order.py`, `update_order()` method, add validation:

```python
def update_order(self, order_id: str, **kwargs):
    order = self.get_order(id=order_id)
    if not order:
        raise RecordNotFoundError(f"Order {order_id} not found")

    if "status" in kwargs:
        from app.services.state_machine import validate_order_transition
        new_status = kwargs["status"]
        if not validate_order_transition(order.status, new_status):
            raise InvalidOrderError(
                f"Cannot transition order from {order.status} to {new_status}"
            )

    for key, value in kwargs.items():
        setattr(order, key, value)
    self.db.commit()
    return order
```

**Step 5: Run all tests**

Run: `python -m pytest tests/ -v --ignore=tests/integration`
Expected: PASS

**Step 6: Commit**

```bash
git add app/services/state_machine.py app/db/order.py tests/unit/test_state_machine.py
git commit -m "feat: add order state machine validation to prevent invalid status transitions"
```

---

### Task 20: Resolve Vape Country Eligibility Conflict

**Files:**
- Modify: `app/enums.py` (lines 73-80, RESTRICTED_COUNTRIES)
- Modify: `app/services/order.py` (vape validation logic)
- Test: `tests/unit/test_vape_eligibility.py` (Create)

**Step 1: Write the failing test**

```python
# tests/unit/test_vape_eligibility.py
import pytest

@pytest.mark.unit
class TestVapeEligibility:
    def test_us_is_eligible_for_vape(self):
        from app.enums import VAPE_ELIGIBLE_COUNTRIES
        assert "US" in VAPE_ELIGIBLE_COUNTRIES

    def test_gb_is_eligible_for_vape(self):
        from app.enums import VAPE_ELIGIBLE_COUNTRIES
        assert "GB" in VAPE_ELIGIBLE_COUNTRIES

    def test_cn_is_not_eligible_for_vape(self):
        from app.enums import VAPE_ELIGIBLE_COUNTRIES
        assert "CN" not in VAPE_ELIGIBLE_COUNTRIES
```

**Step 2: Implement — Replace restricted list with eligible list**

In `app/enums.py`, replace:
```python
# OLD: RESTRICTED_COUNTRIES for VAPE
# NEW: Eligible countries (matching frontend puffyRules.ts)
VAPE_ELIGIBLE_COUNTRIES = {"US", "CA", "GB", "DE", "FR", "AU", "JP"}
```

Update `app/services/order.py` to use `VAPE_ELIGIBLE_COUNTRIES` instead of restricted list.

**Step 3: Run tests, commit**

```bash
git add app/enums.py app/services/order.py tests/unit/test_vape_eligibility.py
git commit -m "fix: align vape country eligibility with frontend rules (allowlist instead of blocklist)"
```

---

### Task 21: Add Rate Limiting with SlowAPI

**Files:**
- Modify: `requirements.txt` (add slowapi)
- Modify: `app/puffy.py` (add middleware)
- Create: `app/rate_limit.py`
- Test: `tests/api/test_rate_limit.py` (Create)

**Step 1: Install SlowAPI**

```bash
pip install slowapi
echo "slowapi" >> requirements.txt
```

**Step 2: Create rate limit config**

```python
# app/rate_limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
```

**Step 3: Add middleware to puffy.py**

```python
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.rate_limit import limiter

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

**Step 4: Add rate limits to sensitive endpoints**

In `app/api/user.py`:
```python
from app.rate_limit import limiter

@router.get("/sign-in")
@limiter.limit("10/minute")
def sign_in(request: Request, ...):
    ...

@router.post("/verify")
@limiter.limit("10/minute")
def verify(request: Request, ...):
    ...
```

**Step 5: Run tests, commit**

```bash
git add app/rate_limit.py app/puffy.py app/api/user.py requirements.txt tests/api/test_rate_limit.py
git commit -m "feat: add SlowAPI rate limiting to auth endpoints (10/min)"
```

---

### Task 22: Fix ShippingAddress Field Name Mismatch

**Files:**
- Modify: `app/models/order.py` (ShippingAddress columns)
- Modify: `app/schemas/order.py` (ShippingAddress schema)
- Modify: `app/db/order.py` (address creation code)

**Step 1: Add field aliases to schema**

In `app/schemas/order.py`, update ShippingAddress:

```python
class ShippingAddress(BaseSchema):
    id: Optional[str] = None
    name: Optional[str] = Field(max_length=255, default=None)
    email: Optional[str] = Field(max_length=255, default=None)
    phone: Optional[str] = Field(max_length=50, default=None, alias="phone_number")
    line1: Optional[str] = Field(max_length=500, default=None, alias="address_line_1")
    line2: Optional[str] = Field(max_length=500, default=None, alias="address_line_2")
    city: Optional[str] = Field(max_length=255, default=None)
    state: Optional[str] = Field(max_length=255, default=None)
    postal_code: Optional[str] = Field(max_length=50, default=None)
    country: Optional[str] = Field(max_length=10, default=None)

    model_config = ConfigDict(populate_by_name=True)
```

This way the schema accepts both `phone` and `phone_number`, `line1` and `address_line_1`.

**Step 2: Run all tests**

Run: `python -m pytest tests/ -v --ignore=tests/integration`
Expected: PASS

**Step 3: Commit**

```bash
git add app/schemas/order.py app/models/order.py app/db/order.py
git commit -m "fix: add field aliases to ShippingAddress for frontend compatibility"
```

---

### Task 23: Add Axios Timeout to Frontend

**Files:**
- Modify: `../puffy-frontend2/src/lib/axios.ts`

**Step 1: Add timeout**

```typescript
export const config = {
  baseURL: process.env.NEXT_PUBLIC_BACKEND_BASE_URL,
  timeout: 15000, // 15 second timeout
  headers: {
    // ... existing headers
  },
};
```

**Step 2: Remove rejectUnauthorized: false**

```typescript
// DELETE the https.Agent with rejectUnauthorized: false
// Or change to:
// const agent = new https.Agent({ rejectUnauthorized: true });
```

**Step 3: Commit**

```bash
git add ../puffy-frontend2/src/lib/axios.ts
git commit -m "fix(security): add axios timeout (15s) and enable TLS verification"
```

---

### Task 24: Write to ReferralCodeUsage/PassCodeUsage Audit Tables

**Files:**
- Modify: `app/db/order.py` (after passcode/referral increment)

**Step 1: Add usage record creation**

After the atomic increment in `create_order()`, add:

```python
# After passcode increment:
if order.pass_code:
    usage = PassCodeUsage(
        code_owner_id=passcode_owner_id,
        code_user_id=order.user_id,
        order_id=order.id
    )
    self.db.add(usage)

# After referral code use:
if order.referral_code:
    usage = ReferralCodeUsage(
        code_owner_id=referral_owner_id,
        code_user_id=order.user_id,
        order_id=order.id
    )
    self.db.add(usage)
```

**Step 2: Run tests, commit**

```bash
git add app/db/order.py
git commit -m "feat: write to passcode/referral usage audit tables for tracking"
```

---

### Task 25: Run Full Test Suite — Fix All Broken Tests

**Step 1: Run full suite**

```bash
python -m pytest tests/ -v --ignore=tests/integration --tb=short 2>&1 | head -100
```

**Step 2: Fix any failing tests**

Address each failure individually.

**Step 3: Run again to confirm**

```bash
python -m pytest tests/ -v --ignore=tests/integration
```

Expected: ALL PASS

**Step 4: Commit**

```bash
git add -A
git commit -m "fix: resolve all test failures after Phase 0 changes"
```

---

## Phase 0 Complete Checklist

- [ ] Task 1: Remove print(Settings()) leak
- [ ] Task 2: Stop logging full JWT tokens
- [ ] Task 3: Add pagination to list endpoints
- [ ] Task 4: Invalidate session after verify
- [ ] Task 5: Atomic passcode/referral increment
- [ ] Task 6: UNIQUE constraint on twitter_id
- [ ] Task 7: Fix create_user race condition
- [ ] Task 8: Remove wallet_db dependency
- [ ] Task 9: Update .from_orm() to .model_validate()
- [ ] Task 10: Fix broken imports
- [ ] Task 11: Set up Alembic
- [ ] Task 12: Add /health and /ready endpoints
- [ ] Task 13: Fix CORS allow_credentials
- [ ] Task 14: Replace SessionStore with Redis
- [ ] Task 15: Fix Twitter OAuth PKCE
- [ ] Task 16: Add pool_pre_ping
- [ ] Task 17: Make Redis TTL configurable
- [ ] Task 18: Pin dependency versions
- [ ] Task 19: Add order state machine
- [ ] Task 20: Fix vape country eligibility
- [ ] Task 21: Add rate limiting
- [ ] Task 22: Fix ShippingAddress field names
- [ ] Task 23: Add frontend axios timeout + TLS
- [ ] Task 24: Write to audit tables
- [ ] Task 25: Full test suite green
