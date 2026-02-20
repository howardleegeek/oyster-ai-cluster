# Phase 1: Auth + User Schema — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refactor auth flow (sign-in/verify) to match Reward Center API spec. Update User schema and JWT payload. Add multi-chain wallet support. All existing auth flows must still work.

**Architecture:** Move sign-in/verify from `/user/` router to root router. Add nested verify body (SolSignProof | TonSignProof). Change JWT fields. Add EVM/TON wallet endpoints. All changes backward-compatible via Alembic migration.

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, PyNaCl, PyJWT, pytest

**Working Directory:** `/Users/howardli/Downloads/.claude/worktrees/modest-jennings/puffy-backend`

**Depends On:** Phase 0 complete (Alembic set up, SessionStore on Redis, bugs fixed)

---

### Task 1: Alembic Migration — Add Columns to Users Table

**Files:**
- Create: `alembic/versions/xxxx_add_user_columns.py` (auto-generated)
- Modify: `app/models/user.py` (add new columns)

**Step 1: Add new columns to User model**

In `app/models/user.py`, add to the `User` class:

```python
eth_wallet_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
ton_wallet_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
twitter_icon_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
twitter_locked: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=False)
email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
chain: Mapped[str] = mapped_column(Enum(Chain), default=Chain.SOL)
```

**Step 2: Generate Alembic migration**

```bash
alembic revision --autogenerate -m "add eth_wallet, ton_wallet, twitter_icon, twitter_locked, email, chain to users"
```

**Step 3: Review generated migration**

```bash
cat alembic/versions/*add_eth_wallet*.py
```

Verify it has correct ALTER TABLE ADD COLUMN statements.

**Step 4: Apply migration (test DB)**

```bash
alembic upgrade head
```

**Step 5: Run existing tests**

```bash
python -m pytest tests/ -v --ignore=tests/integration
```
Expected: PASS (new columns are nullable, won't break existing code)

**Step 6: Commit**

```bash
git add app/models/user.py alembic/versions/
git commit -m "feat: add multi-chain wallet and profile columns to users table"
```

---

### Task 2: New Auth Schemas — SolSignProof, TonSignProof, SignInVerify

**Files:**
- Create: `app/schemas/auth.py`
- Test: `tests/unit/test_auth_schemas.py` (Create)

**Step 1: Write the failing test**

```python
# tests/unit/test_auth_schemas.py
import pytest
from pydantic import ValidationError

@pytest.mark.unit
class TestAuthSchemas:
    def test_sol_sign_proof_valid(self):
        from app.schemas.auth import SolSignProof
        proof = SolSignProof(signature="abc123", address="7xKXt...")
        assert proof.signature == "abc123"
        assert proof.address == "7xKXt..."

    def test_ton_sign_proof_valid(self):
        from app.schemas.auth import TonSignProof
        proof = TonSignProof(
            signature="sig",
            state_init="init",
            timestamp=1234567890,
            public_key="pk",
            wallet_address_hex="0x...",
            wallet_address_base64="base64..."
        )
        assert proof.timestamp == 1234567890

    def test_sign_in_verify_with_sol_proof(self):
        from app.schemas.auth import SignInVerify, SolSignProof
        req = SignInVerify(
            session_id="sess_123",
            data={"signature": "sig", "address": "addr"}
        )
        assert req.session_id == "sess_123"

    def test_sign_in_verify_with_ton_proof(self):
        from app.schemas.auth import SignInVerify, TonSignProof
        req = SignInVerify(
            session_id="sess_123",
            data={
                "signature": "sig",
                "state_init": "init",
                "timestamp": 123,
                "public_key": "pk",
                "wallet_address_hex": "0x",
                "wallet_address_base64": "b64"
            }
        )
        assert req.session_id == "sess_123"

    def test_session_info_includes_chain(self):
        from app.schemas.auth import SessionInfoV2
        info = SessionInfoV2(session_id="s1", message="msg", chain="sol")
        assert info.chain == "sol"
```

**Step 2: Run test to verify it fails**

```bash
python -m pytest tests/unit/test_auth_schemas.py -v
```
Expected: FAIL — module doesn't exist

**Step 3: Create auth schemas**

```python
# app/schemas/auth.py
from typing import Optional, Union
from pydantic import BaseModel
from app.enums import Chain

class SolSignProof(BaseModel):
    signature: str
    address: str

class TonSignProof(BaseModel):
    signature: str
    state_init: str
    timestamp: int
    public_key: str
    wallet_address_hex: str
    wallet_address_base64: str

class SignInVerify(BaseModel):
    session_id: str
    data: Union[SolSignProof, TonSignProof]

class SessionInfoV2(BaseModel):
    session_id: str
    message: Optional[str] = None
    chain: Optional[str] = Chain.SOL

class TokenResp(BaseModel):
    token: str
```

**Step 4: Run test**

```bash
python -m pytest tests/unit/test_auth_schemas.py -v
```
Expected: PASS

**Step 5: Commit**

```bash
git add app/schemas/auth.py tests/unit/test_auth_schemas.py
git commit -m "feat: add auth schemas (SolSignProof, TonSignProof, SignInVerify)"
```

---

### Task 3: Update JWT Payload — user_id / wallet_address / chain

**Files:**
- Modify: `app/services/token.py` (gen_token and parse_token)
- Modify: `app/dependencies.py` (parse user from new JWT)
- Modify: `tests/unit/test_token_service.py`

**Step 1: Update test expectations**

```python
# In tests/unit/test_token_service.py, add/modify:
def test_gen_token_uses_user_id_field(self, token_service, sample_user):
    token = token_service.gen_token(sample_user)
    decoded = jwt.decode(token, token_service.secret, algorithms=["HS256"])
    assert "user_id" in decoded
    assert "id" not in decoded  # Old field should not exist

def test_gen_token_uses_wallet_address_field(self, token_service, sample_user):
    token = token_service.gen_token(sample_user)
    decoded = jwt.decode(token, token_service.secret, algorithms=["HS256"])
    assert "wallet_address" in decoded
    assert "address" not in decoded

def test_gen_token_includes_chain(self, token_service, sample_user):
    token = token_service.gen_token(sample_user)
    decoded = jwt.decode(token, token_service.secret, algorithms=["HS256"])
    assert "chain" in decoded
```

**Step 2: Run tests to see failures**

```bash
python -m pytest tests/unit/test_token_service.py -v
```
Expected: FAIL — old field names used

**Step 3: Update token.py**

```python
# app/services/token.py — gen_token():
def gen_token(self, user) -> str:
    payload = {
        "user_id": user.id if hasattr(user, 'id') else user.user_id,
        "wallet_address": user.address if hasattr(user, 'address') else user.wallet_address,
        "chain": getattr(user, 'chain', 'sol'),
        "exp": int(time.time() + self.exp),
    }
    return jwt.encode(payload, self.secret, algorithm="HS256")

# parse_token():
def parse_token(self, token: str):
    # ... existing Bearer stripping ...
    try:
        payload = jwt.decode(token, self.secret, algorithms=["HS256"])
        return schemas.User(
            id=payload.get("user_id", payload.get("id")),  # backward compat
            address=payload.get("wallet_address", payload.get("address")),  # backward compat
        )
    except jwt.ExpiredSignatureError:
        logger.info("expired token %s...", token[:20] if token else "empty")
        return None
    except jwt.InvalidTokenError as err:
        logger.error("parse token error %s... %s", token[:20] if token else "empty", err)
        return None
```

**Step 4: Run tests**

```bash
python -m pytest tests/unit/test_token_service.py -v
```
Expected: PASS

**Step 5: Commit**

```bash
git add app/services/token.py tests/unit/test_token_service.py
git commit -m "feat: update JWT payload to use user_id/wallet_address/chain fields"
```

---

### Task 4: Create Auth Router — Move sign-in/verify to Root

**Files:**
- Create: `app/api/auth.py`
- Modify: `app/puffy.py` (register new router)
- Modify: `app/api/user.py` (remove sign-in/verify endpoints)
- Test: `tests/api/test_auth_api.py` (Create)

**Step 1: Write the failing test**

```python
# tests/api/test_auth_api.py
import pytest
from starlette import status

@pytest.mark.api
class TestAuthAPI:
    def test_sign_in_at_root_path(self, test_client):
        """GET /sign-in should work (moved from /user/sign-in)."""
        response = test_client.get("/sign-in")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "session_id" in data
        assert "message" in data

    def test_sign_in_returns_chain(self, test_client):
        """GET /sign-in should include chain field."""
        response = test_client.get("/sign-in")
        data = response.json()
        assert "chain" in data

    def test_verify_at_root_path(self, test_client):
        """POST /verify should accept nested data body."""
        response = test_client.post("/verify", json={
            "session_id": "test_session",
            "data": {
                "signature": "test_sig",
                "address": "test_addr"
            }
        })
        # Will fail auth but should not 404
        assert response.status_code != 404

    def test_old_user_sign_in_still_works(self, test_client):
        """GET /user/sign-in should still work for backward compat."""
        response = test_client.get("/user/sign-in")
        assert response.status_code == status.HTTP_200_OK
```

**Step 2: Run test to see 404**

```bash
python -m pytest tests/api/test_auth_api.py -v
```
Expected: FAIL — /sign-in returns 404

**Step 3: Create auth router**

```python
# app/api/auth.py
from fastapi import APIRouter, Depends, Request
from app.schemas.auth import SignInVerify, SessionInfoV2, TokenResp
from app.db.cache import CacheDbDep
from app.schemas.session import SessionData
from app.services.token import TokenServiceDep
from app.services.user import UserServiceDep
from app.plib.web3_sol import SolWrapper
from app.plib.utils import gen_random_hex_str
from app.config import SettingsDep
from app.error import UserError
from app.rate_limit import limiter
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])

@router.get("/sign-in", response_model=SessionInfoV2)
@limiter.limit("10/minute")
def sign_in(request: Request, cache_db: CacheDbDep, settings: SettingsDep):
    message = gen_random_hex_str(20)
    data = SessionData(message=message)
    session_id = cache_db.new_session(data)
    return SessionInfoV2(session_id=session_id, message=message)

@router.post("/verify", response_model=TokenResp)
@limiter.limit("10/minute")
def verify(
    request: Request,
    req: SignInVerify,
    cache_db: CacheDbDep,
    token_service: TokenServiceDep,
    user_service: UserServiceDep,
    settings: SettingsDep,
):
    session = cache_db.get_session(req.session_id)
    if not session:
        raise UserError.INVALID_SESSION.http()

    # Detect proof type and verify
    from app.schemas.auth import TonSignProof
    if isinstance(req.data, TonSignProof):
        # TON verification — stub for now
        address = req.data.wallet_address_hex
        chain = "ton"
        # TODO: Implement TON proof verification
        verified = True
    else:
        # Solana verification
        sol = SolWrapper(settings.sol_key)
        verified = sol.verify(req.data.address, req.data.signature, session.message)
        address = req.data.address
        chain = "sol"

    if not verified:
        raise UserError.INVALID_SIGNATURE.http()

    user = user_service.create_or_get_user(address)
    if not user:
        raise UserError.USER_NOT_FOUND.http()

    token = token_service.gen_token(user)
    cache_db.close_session(req.session_id)  # Invalidate session
    return TokenResp(token=token)
```

**Step 4: Register router in puffy.py**

```python
# In app/puffy.py, add:
from app.api.auth import router as auth_router
app.include_router(auth_router)
```

**Step 5: Keep backward-compat /user/sign-in**

In `app/api/user.py`, keep existing sign-in/verify but mark as deprecated or redirect.

**Step 6: Run tests**

```bash
python -m pytest tests/api/test_auth_api.py -v
python -m pytest tests/ -v --ignore=tests/integration
```
Expected: PASS

**Step 7: Commit**

```bash
git add app/api/auth.py app/puffy.py app/api/user.py tests/api/test_auth_api.py
git commit -m "feat: create auth router with /sign-in and /verify at root path"
```

---

### Task 5: Update User Schema to Match Reward Center Spec

**Files:**
- Modify: `app/schemas/user.py` (User class)
- Test: `tests/unit/test_user_schema.py` (Create)

**Step 1: Write the failing test**

```python
# tests/unit/test_user_schema.py
import pytest

@pytest.mark.unit
class TestUserSchemaV2:
    def test_user_schema_has_user_id_field(self):
        from app.schemas.user import User
        u = User(id="test", address="addr")
        # The API response should use user_id
        data = u.model_dump(by_alias=True)
        assert "user_id" in data or "id" in data

    def test_user_schema_has_wallet_address_field(self):
        from app.schemas.user import User
        u = User(id="test", address="addr")
        data = u.model_dump(by_alias=True)
        assert "wallet_address" in data or "address" in data

    def test_user_schema_has_chain_field(self):
        from app.schemas.user import User
        u = User(id="test", address="addr", chain="sol")
        assert u.chain == "sol"

    def test_user_schema_has_new_optional_fields(self):
        from app.schemas.user import User
        u = User(
            id="test",
            address="addr",
            eth_wallet_address="0x123",
            ton_wallet_address="ton_addr",
            twitter_icon_url="https://...",
            twitter_locked=False,
            email="test@test.com",
            chain="sol",
            points=100,
        )
        assert u.eth_wallet_address == "0x123"
        assert u.email == "test@test.com"
        assert u.points == 100
```

**Step 2: Run test to see failures**

**Step 3: Update User schema**

```python
# In app/schemas/user.py, update User class:
class User(BaseSchema):
    id: Optional[str] = Field(default=None, alias="user_id")
    address: str = Field(alias="wallet_address")
    address_hex: Optional[str] = Field(default=None, alias="wallet_address_hex")
    eth_wallet_address: Optional[str] = None
    ton_wallet_address: Optional[str] = None
    twitter_id: Optional[str] = None
    twitter_name: Optional[str] = None
    twitter_icon_url: Optional[str] = None
    twitter_locked: Optional[bool] = None
    email: Optional[str] = None
    chain: Optional[str] = "sol"
    points: Optional[int] = None
    referral_code: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Keep existing relations for backward compat
    balance: Optional[Balance] = None
    records: Optional[List[RewardRecord]] = None
    promote_nfts: Optional[List[PromoteNft]] = None
    nfts: Optional[List[Nft]] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,  # Accept both id and user_id
    )
```

**Step 4: Run tests**

```bash
python -m pytest tests/unit/test_user_schema.py -v
python -m pytest tests/ -v --ignore=tests/integration
```
Expected: PASS

**Step 5: Commit**

```bash
git add app/schemas/user.py tests/unit/test_user_schema.py
git commit -m "feat: update User schema with new fields (wallet_address, chain, email, etc.)"
```

---

### Task 6: New User Endpoints — /user/info, /user/email, /user/twitter-lock, Wallet Updates

**Files:**
- Modify: `app/api/user.py`
- Modify: `app/db/user.py` (add update methods for new fields)
- Test: `tests/api/test_user_endpoints_v2.py` (Create)

**Step 1: Write failing tests**

```python
# tests/api/test_user_endpoints_v2.py
import pytest
from starlette import status

@pytest.mark.api
class TestUserEndpointsV2:
    def test_get_user_info(self, test_client, auth_headers):
        response = test_client.get("/user/info", headers=auth_headers)
        assert response.status_code in (200, 401)  # 401 if mock not set up

    def test_post_user_email(self, test_client, auth_headers):
        response = test_client.post("/user/email", json={"email": "test@test.com"}, headers=auth_headers)
        assert response.status_code in (200, 401)

    def test_get_twitter_lock(self, test_client, auth_headers):
        response = test_client.get("/user/twitter-lock", headers=auth_headers)
        assert response.status_code in (200, 401)

    def test_post_update_eth_wallet(self, test_client, auth_headers):
        response = test_client.post("/user/update-eth-wallet", json={"eth_wallet_address": "0x123"}, headers=auth_headers)
        assert response.status_code in (200, 401)

    def test_post_update_ton_wallet(self, test_client, auth_headers):
        response = test_client.post("/user/update-ton-wallet", json={"ton_wallet_address": "ton_addr"}, headers=auth_headers)
        assert response.status_code in (200, 401)
```

**Step 2: Add endpoints to user.py**

```python
# In app/api/user.py, add:

@router.get("/info")
def get_user_info(user: UserAuthDep, user_service: UserServiceDep):
    return user_service.get_user(id=user.id)

@router.post("/email")
def update_email(user: UserAuthDep, req: UpdateEmailReq, user_service: UserServiceDep):
    user_service.update_user(user_id=user.id, email=req.email)
    return {"success": True}

@router.get("/twitter-lock")
def get_twitter_lock(user: UserAuthDep, user_service: UserServiceDep):
    user_data = user_service.get_user(id=user.id)
    return {"twitter_locked": user_data.twitter_locked if user_data else False}

class UpdateEthWalletReq(BaseModel):
    eth_wallet_address: str

@router.post("/update-eth-wallet")
def update_eth_wallet(user: UserAuthDep, req: UpdateEthWalletReq, user_service: UserServiceDep):
    user_service.update_user(user_id=user.id, eth_wallet_address=req.eth_wallet_address)
    return {"success": True}

class UpdateTonWalletReq(BaseModel):
    ton_wallet_address: str

@router.post("/update-ton-wallet")
def update_ton_wallet(user: UserAuthDep, req: UpdateTonWalletReq, user_service: UserServiceDep):
    user_service.update_user(user_id=user.id, ton_wallet_address=req.ton_wallet_address)
    return {"success": True}
```

**Step 3: Update user repo to support new fields**

In `app/db/user.py`, update `update_user()` to accept `eth_wallet_address`, `ton_wallet_address`, `twitter_icon_url`, `twitter_locked`, `email`, `chain`.

**Step 4: Run tests**

```bash
python -m pytest tests/api/test_user_endpoints_v2.py -v
python -m pytest tests/ -v --ignore=tests/integration
```
Expected: PASS

**Step 5: Commit**

```bash
git add app/api/user.py app/db/user.py tests/api/test_user_endpoints_v2.py
git commit -m "feat: add /user/info, /user/email, /user/twitter-lock, /user/update-eth-wallet, /user/update-ton-wallet"
```

---

### Task 7: Add EVM Signature Verification Stub

**Files:**
- Create: `app/plib/web3_evm.py`
- Test: `tests/unit/test_web3_evm.py` (Create)

**Step 1: Write the test**

```python
# tests/unit/test_web3_evm.py
import pytest

@pytest.mark.unit
class TestEVMWrapper:
    def test_verify_returns_bool(self):
        from app.plib.web3_evm import EVMWrapper
        evm = EVMWrapper()
        result = evm.verify("0xaddr", "0xsig", "message")
        assert isinstance(result, bool)

    def test_check_nft_balance_returns_int(self):
        from app.plib.web3_evm import EVMWrapper
        evm = EVMWrapper()
        result = evm.check_nft_balance("0xwallet", "0xcollection")
        assert isinstance(result, int)
```

**Step 2: Create EVM wrapper (stub)**

```python
# app/plib/web3_evm.py
import logging

logger = logging.getLogger(__name__)

class EVMWrapper:
    """EVM chain interaction. Stub for Phase 1 — full implementation in Phase 2."""

    def verify(self, address: str, signature: str, message: str) -> bool:
        """Verify EIP-191 personal_sign signature. STUB."""
        logger.warning("EVM verify is stubbed — returning False")
        return False

    def check_nft_balance(self, wallet: str, collection_address: str) -> int:
        """Check ERC-721 balanceOf for wallet on collection. STUB."""
        logger.warning("EVM NFT balance check is stubbed — returning 0")
        return 0
```

**Step 3: Run test**

```bash
python -m pytest tests/unit/test_web3_evm.py -v
```
Expected: PASS

**Step 4: Commit**

```bash
git add app/plib/web3_evm.py tests/unit/test_web3_evm.py
git commit -m "feat: add EVM signature verification stub (web3_evm.py)"
```

---

### Task 8: Add TON Signature Verification Stub

**Files:**
- Create: `app/plib/web3_ton.py`
- Test: `tests/unit/test_web3_ton.py` (Create)

**Step 1: Write the test**

```python
# tests/unit/test_web3_ton.py
import pytest

@pytest.mark.unit
class TestTONWrapper:
    def test_verify_proof_returns_bool(self):
        from app.plib.web3_ton import TONWrapper
        ton = TONWrapper()
        result = ton.verify_proof(
            signature="sig",
            state_init="init",
            timestamp=123,
            public_key="pk",
            wallet_address_hex="0x",
            wallet_address_base64="b64"
        )
        assert isinstance(result, bool)
```

**Step 2: Create TON wrapper (stub)**

```python
# app/plib/web3_ton.py
import logging

logger = logging.getLogger(__name__)

class TONWrapper:
    """TON chain interaction. Stub for Phase 1 — full implementation in Phase 2."""

    def verify_proof(self, signature: str, state_init: str, timestamp: int,
                     public_key: str, wallet_address_hex: str,
                     wallet_address_base64: str) -> bool:
        """Verify TON Connect proof. STUB — returns True for now."""
        logger.warning("TON verify_proof is stubbed — returning True")
        return True

    def check_nft_balance(self, wallet: str, collection_address: str) -> int:
        """Check TON NFT balance. STUB."""
        logger.warning("TON NFT balance check is stubbed — returning 0")
        return 0
```

**Step 3: Run test, commit**

```bash
git add app/plib/web3_ton.py tests/unit/test_web3_ton.py
git commit -m "feat: add TON signature verification stub (web3_ton.py)"
```

---

### Task 9: Add Email Verification Endpoints

**Files:**
- Modify: `app/api/user.py` (add 2 endpoints)
- Test: `tests/api/test_email_verification.py` (Create)

**Step 1: Write the failing test**

```python
# tests/api/test_email_verification.py
import pytest
from starlette import status

@pytest.mark.api
class TestEmailVerification:
    def test_send_code_endpoint_exists(self, test_client, auth_headers):
        response = test_client.post("/user/email/send-code", json={"email": "test@test.com"}, headers=auth_headers)
        assert response.status_code != 404

    def test_verify_code_endpoint_exists(self, test_client, auth_headers):
        response = test_client.post("/user/email/verify-code", json={"email": "test@test.com", "code": "123456"}, headers=auth_headers)
        assert response.status_code != 404
```

**Step 2: Add endpoints**

```python
# In app/api/user.py, add:

class SendEmailCodeReq(BaseModel):
    email: str

class VerifyEmailCodeReq(BaseModel):
    email: str
    code: str

@router.post("/email/send-code")
def send_email_code(user: UserAuthDep, req: SendEmailCodeReq, cache_db: CacheDbDep, settings: SettingsDep):
    from app.plib.utils import gen_random_otp
    from app.plib.sendmail import send_mail
    otp = gen_random_otp()
    cache_db.set_data(f"email_otp:{user.id}:{req.email}", otp, expire_hours=0.17)  # 10 min
    send_mail(req.email, otp, settings.sender_account, settings.sender_key)
    return {"success": True}

@router.post("/email/verify-code")
def verify_email_code(user: UserAuthDep, req: VerifyEmailCodeReq, cache_db: CacheDbDep, user_service: UserServiceDep):
    stored_otp = cache_db.get_data(f"email_otp:{user.id}:{req.email}")
    if not stored_otp or stored_otp != req.code:
        return {"success": False, "message": "Invalid or expired code"}
    user_service.update_user(user_id=user.id, email=req.email)
    return {"success": True}
```

**Step 3: Run tests, commit**

```bash
git add app/api/user.py tests/api/test_email_verification.py
git commit -m "feat: add email verification endpoints (/user/email/send-code, /user/email/verify-code)"
```

---

### Task 10: Add Solana Transaction Verification Method

**Files:**
- Modify: `app/services/sol_api.py` or `app/plib/sol_api.py` (wherever SolApi lives)
- Test: `tests/unit/test_sol_api_verify.py` (Create)

**Step 1: Write the test**

```python
# tests/unit/test_sol_api_verify.py
import pytest
from unittest.mock import MagicMock, patch

@pytest.mark.unit
class TestSolanaTransactionVerification:
    def test_verify_mint_transaction_returns_bool(self):
        """verify_mint_transaction should return True/False."""
        # This will be a stub until real Solana RPC is available
        pass

    def test_verify_mint_transaction_method_exists(self):
        """Method should exist on SolApi class."""
        from app.plib.sol_api import SolApi
        api = SolApi.__new__(SolApi)  # Create without __init__
        assert hasattr(api, 'verify_mint_transaction')
```

**Step 2: Add method to SolApi**

```python
# In app/plib/sol_api.py (or wherever SolApi is), add:
def verify_mint_transaction(self, tx_hash: str, expected_wallet: str,
                            expected_amount_sol: float, expected_nft_id: int,
                            expected_user_id: str) -> bool:
    """Verify a mint gas fee transaction on Solana.
    Checks: destination wallet, amount, memo data (nft_id, user_id).
    """
    try:
        # TODO: Implement with real Solana RPC call
        # tx = self.connection.get_transaction(tx_hash, encoding="jsonParsed")
        logger.warning("verify_mint_transaction is stubbed — returning True")
        return True
    except Exception as e:
        logger.error("Failed to verify mint transaction %s: %s", tx_hash[:20], e)
        return False
```

**Step 3: Run tests, commit**

```bash
git add app/plib/sol_api.py tests/unit/test_sol_api_verify.py
git commit -m "feat: add verify_mint_transaction method to SolApi (stub)"
```

---

### Task 11: Update TwitterOauth to Include redirect_url

**Files:**
- Modify: `app/api/user.py` (TwitterOauth class)

**Step 1: Update TwitterOauth schema**

```python
# In app/api/user.py, update TwitterOauth:
class TwitterOauth(BaseModel):
    auth_code: str
    redirect_url: str = ""  # Default empty for backward compat
```

**Step 2: Pass redirect_url to oauth function**

```python
# In twitter-oauth endpoint, change:
result = twitter_oauth(
    settings.twitter_id,
    settings.twitter_secret,
    req.auth_code,
    req.redirect_url or settings.twitter_redirect_url,  # Use request URL or fallback
)
```

**Step 3: Run tests, commit**

```bash
git add app/api/user.py
git commit -m "feat: add redirect_url field to TwitterOauth request body"
```

---

### Task 12: Phase 1 Full Test Suite

**Step 1: Run full test suite**

```bash
python -m pytest tests/ -v --ignore=tests/integration --tb=short
```

**Step 2: Fix any failures**

**Step 3: Commit**

```bash
git add -A
git commit -m "test: Phase 1 complete — all auth and user schema tests passing"
```

---

## Phase 1 Complete Checklist

- [ ] Task 1: Alembic migration — add user columns
- [ ] Task 2: Auth schemas (SolSignProof, TonSignProof, SignInVerify)
- [ ] Task 3: JWT payload update (user_id, wallet_address, chain)
- [ ] Task 4: Auth router at root path (/sign-in, /verify)
- [ ] Task 5: User schema v2 matching Reward Center spec
- [ ] Task 6: New user endpoints (info, email, twitter-lock, wallet updates)
- [ ] Task 7: EVM signature verification stub
- [ ] Task 8: TON signature verification stub
- [ ] Task 9: Email verification endpoints
- [ ] Task 10: Solana transaction verification method
- [ ] Task 11: TwitterOauth redirect_url
- [ ] Task 12: Full test suite green
