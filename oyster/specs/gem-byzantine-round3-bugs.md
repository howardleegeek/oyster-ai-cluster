# GEM Byzantine Round 3 — Consolidated Bug Report

> Generated: 2026-02-12 | 5 audit agents | Scope: full backend + frontend
> Base commit: 980c285 (S2 bug fixes)

---

## Summary

| Severity | Count | Status |
|----------|-------|--------|
| CRITICAL | 7 | Fix immediately |
| HIGH | 12 | Fix this sprint |
| MEDIUM | 10 | Next sprint |
| LOW | ~30 | Backlog |

---

## CRITICAL Bugs (7) — Runtime Crashes / Data Corruption

### C-1: payment.py missing `select` import
- **File**: `app/services/payment.py:276-277`
- **Bug**: `select(models.NftPayment)` used but `select` not imported from sqlalchemy
- **Impact**: `NameError: name 'select' is not defined` — reconciliation endpoint crashes
- **Fix**: Add `from sqlalchemy import select` to imports (line 6)

### C-2: referral.py missing `and_` import
- **File**: `app/services/referral.py:128`
- **Bug**: `and_(...)` used but `and_` not imported from sqlalchemy
- **Impact**: `NameError` — referral reward check crashes when user redeems order
- **Fix**: Add `from sqlalchemy import and_, select` to imports

### C-3: User model missing `is_disabled` field
- **File**: `app/models/user.py`
- **Bug**: `admin_ops.py:363` reads `user.is_disabled`, `db/admin_ops.py:187` sets `user.is_disabled = True` — field doesn't exist on model
- **Impact**: Admin disable user endpoint crashes with `AttributeError`
- **Fix**: Add `is_disabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)` to User model

### C-4: User model missing `status` field (if referenced)
- **File**: `app/models/user.py`
- **Bug**: `AdminUserDetail` schema has `status` field but User model has no `status` column
- **Impact**: Admin user detail endpoint returns wrong/missing data
- **Fix**: Verify if `status` is derived from `is_active`/`is_disabled` or needs its own column. If derived, fix schema to compute it. If needed, add column.
- **Verify**: Check `schemas/admin_ops.py` for how `status` is populated

### C-5: Frontend vite.config.ts uses `process.env` (Node.js API)
- **File**: `lumina/vite.config.ts:20-22`, `lumina/services/geminiService.ts:4`, `lumina/components/AuthGate.tsx:25`
- **Bug**: Vite client code uses `process.env.X` instead of `import.meta.env.VITE_X`
- **Impact**: `process.env` is `undefined` in browser — all env vars silently fail
- **Fix**: Replace `process.env.REACT_APP_API_URL` → `import.meta.env.VITE_API_BASE_URL`, `process.env.API_KEY` → `import.meta.env.VITE_GEMINI_API_KEY`
- **Note**: vite.config.ts `define` block is correct (it injects at build time), but geminiService.ts and AuthGate.tsx runtime references are broken

### C-6: Enum casing inconsistency — NftStatus.PAID vs PackOpeningStatus.PAID
- **File**: `app/models/enums.py`
- **Bug**: `NftStatus.PAID = "paid"` (lowercase) vs `PackOpeningStatus.PAID = "PAID"` (uppercase)
- **Impact**: DB lookups with wrong casing return empty results — payment flow may silently fail
- **Fix**: Standardize all enum values to UPPERCASE (DB migration needed for existing data)

### C-7: AdminPackResp schema fields don't match Pack model
- **File**: `app/schemas/admin_ops.py` vs `app/models/pack.py`
- **Bug**: `AdminPackResp.series_id: int` but `Pack.series_id: String(255)`. `AdminPackResp.version` doesn't exist on Pack. `AdminPackResp.price_sol: Decimal` (required) but `Pack.price_sol: Optional[Decimal]`
- **Impact**: Pydantic validation error when returning admin pack data
- **Fix**: Align schema types with model: `series_id: str`, `price_sol: Optional[Decimal]`, remove or make `version` optional

---

## HIGH Bugs (12) — Logic Errors / Security Issues

### H-1: Dual balance tracking — Wallet.balance vs User.credit_balance
- **File**: `app/services/wallet_payment.py`, `app/db/wallet.py`
- **Bug**: Balance stored in both `Wallet.balance` and `User.credit_balance`. Some code reads one, some the other. They can desync.
- **Impact**: Users see inconsistent balances, potential double-spend
- **Fix**: Designate ONE source of truth (recommend `Wallet.balance` + ledger), deprecate `User.credit_balance`

### H-2: Race condition in ledger balance calculation
- **File**: `app/services/wallet_payment.py:282-283, 354-355`
- **Bug**: Balance computed by summing all ledger entries without row-level locking
- **Impact**: Concurrent transactions can both pass balance check → overdraft
- **Fix**: Add `SELECT ... FOR UPDATE` on wallet row before balance check

### H-3: Non-atomic withdrawal
- **File**: `app/services/wallet_payment.py:640-645`
- **Bug**: Balance deduction and withdrawal record creation not in single transaction scope
- **Impact**: Crash between deduction and record → funds vanish
- **Fix**: Ensure both operations in same `db.begin()` block

### H-4: Vault items marked DELIVERED prematurely
- **File**: `app/db/order.py:191`
- **Bug**: Vault items set to DELIVERED status on order creation, before actual shipping
- **Impact**: Users see "delivered" before they receive items
- **Fix**: Set to REDEEMED on order creation, DELIVERED only when shipping confirms

### H-5: Referral code uses `random.choice()` instead of `secrets`
- **File**: `app/db/referral.py:32-48`
- **Bug**: Non-cryptographic random for referral code generation
- **Impact**: Predictable codes → potential abuse
- **Fix**: Use `secrets.choice()` instead of `random.choice()`

### H-6: O(N) scan for referral code lookup
- **File**: `app/db/referral.py:98-112`
- **Bug**: Iterates all users to find referral code owner
- **Impact**: Slow at scale (10K+ users)
- **Fix**: Add DB index on referral_code column, use indexed query

### H-7: 4 files import enums from pack.py instead of enums.py
- **Files**: `schemas/market.py`, `schemas/pack.py`, `db/pack.py`, `services/lottery_strategy.py`
- **Bug**: Import `Rarity, PackStatus, PackOpeningStatus` from `app.models.pack` (re-export) instead of `app.models.enums` (canonical)
- **Impact**: Tight coupling, breaks if pack.py stops re-exporting
- **Fix**: Change imports to `from app.models.enums import ...`

### H-8: Float multiplication precision loss
- **File**: `app/services/wallet_payment.py:213`
- **Bug**: Uses float multiplication for financial calculation
- **Impact**: Rounding errors in dollar amounts
- **Fix**: Use `Decimal` multiplication throughout

### H-9: Token revocation is O(N) scan
- **File**: `app/services/auth.py`
- **Bug**: Revocation checks scan list/table linearly
- **Impact**: Slow logout/session invalidation at scale
- **Fix**: Use Redis SET or indexed DB table for revoked tokens

### H-10: Frontend type mismatch — RevealedItem vs Gem
- **File**: `lumina/components/PackStoreView.tsx:195`
- **Bug**: Backend returns `RevealedItem` (snake_case fields), frontend expects `Gem` type (camelCase)
- **Impact**: Property access fails silently, UI shows undefined values
- **Fix**: Add proper type mapping function or align types

### H-11: Frontend DashboardUpdates has duplicate GemStatus enum
- **File**: `lumina/components/DashboardUpdates.tsx`
- **Bug**: Defines its own `GemStatus` with extra values not in backend
- **Impact**: Status comparisons may silently fail
- **Fix**: Use single canonical enum, import from shared types

### H-12: Credits state never loads from backend
- **File**: `lumina/` (wallet/credits components)
- **Bug**: Credits/balance shown but never fetched from backend wallet API
- **Impact**: Always shows 0 or stale mock data
- **Fix**: Call GET /wallet/balance on mount, update state

---

## MEDIUM Bugs (10) — Partial Functionality

| ID | File | Bug | Fix |
|----|------|-----|-----|
| M-1 | wallet_payment.py | Hardcoded "GEM_PLATFORM_WALLET_ADDRESS" placeholder | Use env var |
| M-2 | market.py | Missing listing expiry check | Add timestamp filter |
| M-3 | buyback.py | No max quote amount validation | Add business rule |
| M-4 | order.py | Shipping address not validated | Add address schema validation |
| M-5 | admin_ops.py | Incorrect admin fallback for unknown operations | Return 400 not 500 |
| M-6 | Frontend | FMV calculation does string concatenation | Use Number/Decimal |
| M-7 | Frontend | Pack purchase flow not fully integrated | Wire remaining API calls |
| M-8 | Frontend | Mock data still used in some components | Replace with API calls |
| M-9 | notification.py | Telegram webhook has no retry logic | Add retry with backoff |
| M-10 | Frontend | No error boundaries around API calls | Add try/catch + user feedback |

---

## Fix Dispatch Plan

### Phase 1: CRITICAL (immediate — 2 agents)

**Agent Fix-1 (Backend CRITICAL)**: C-1 through C-4, C-6, C-7
```
Target files:
- app/services/payment.py (add select import)
- app/services/referral.py (add and_, select imports)
- app/models/user.py (add is_disabled field)
- app/schemas/admin_ops.py (fix AdminPackResp types)
- app/models/enums.py (standardize casing — verify DB impact first)
```

**Agent Fix-2 (Frontend CRITICAL)**: C-5
```
Target files:
- lumina/services/geminiService.ts (process.env → import.meta.env)
- lumina/components/AuthGate.tsx (process.env → import.meta.env)
```

### Phase 2: HIGH (same sprint — 2 agents)

**Agent Fix-3 (Backend HIGH)**: H-1 through H-9
**Agent Fix-4 (Frontend HIGH)**: H-10 through H-12

### Phase 3: MEDIUM (next sprint)
Manual review and batch fix
