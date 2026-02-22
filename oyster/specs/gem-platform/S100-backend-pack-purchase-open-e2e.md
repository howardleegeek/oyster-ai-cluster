---
task_id: S100-backend-pack-purchase-open-e2e
project: gem-platform
priority: 1
depends_on: []
modifies:
  - backend/app/api/pack.py
  - backend/app/services/pack_engine.py
  - backend/app/db/pack.py
  - backend/app/schemas/pack.py
  - backend/app/services/wallet_payment.py
  - backend/tests/
executor: glm
---

## Goal
Make the backend pack flow production-ready and truly end-to-end:

1) authenticated user purchases a pack -> gets a payment quote
2) user pays on-chain (SOL)
3) backend confirms payment, opens the pack, creates vault items, and returns revealed items

This must work via the HTTP API with correct idempotency and without placeholder behavior.

## Constraints
- Do not add new paid services or infrastructure.
- Do not commit secrets (.env, keys). Use env vars and .env.example only.
- Keep changes scoped to pack + payment confirmation path; avoid unrelated refactors.
- Prefer backward-compatible responses if feasible; if you must change a response shape, update docs/tests.

## Required Behavior
### Purchase
- Endpoint: `POST /api/v1/packs/{pack_id}/purchase`
- Validates pack exists and is purchasable.
- Returns:
  - `opening_id`
  - `receiver_wallet` MUST be the platform wallet (NOT the user's wallet)
  - `amount_sol` (string or decimal-safe, no float rounding issues)
  - `quote_expires_at` (UTC ISO)
- Reserves supply safely (no oversell). If you reserve on purchase, ensure the system has a way to release reservations on expiry (minimal acceptable: treat expired openings as invalid and allow an admin cleanup; best: automated cleanup).

### Confirm Payment + Open
- Endpoint: `POST /api/v1/packs/openings/{opening_id}/confirm-payment`
- Must be idempotent:
  - If called multiple times for the same opening_id after success, return the same revealed items.
  - If the tx hash is re-submitted, do not re-open / do not double-mint vault items.
- Must actually open packs (call PackEngine / create `user_vault` rows) and return revealed items.
- `chain` parsing must accept common inputs from clients (at minimum: `sol`, `SOL`, `SOLANA`). Normalize internally.
- Transaction verification:
  - In DEV, allow a safe bypass (explicitly logged).
  - In non-DEV, verify via Solana RPC that the transaction is confirmed and matches:
    - recipient = platform receiver_wallet
    - amount ~= expected amount (use a small tolerance appropriate for SOL decimals)

## Implementation Notes
- Prefer Decimal end-to-end for monetary amounts.
- Ensure the API returns at least these fields for each revealed item:
  - `vault_item_id`
  - `nft_id`
  - `rarity`
  - `fmv`
  - optional `metadata` if available (ok to be null)

## Acceptance Criteria
- Tests:
  - Add/adjust backend tests so the pack purchase + confirm-payment flow is covered.
  - Must include at least:
    - success path (purchase -> confirm -> returns N items)
    - idempotency (repeat confirm does not duplicate)
    - invalid/expired opening rejected
    - chain normalization
- Verification commands (must pass):
  - `cd backend && python -m compileall -q app`
  - `cd backend && python -m pytest -q`

## Do Not Do
- Do not hardcode platform wallet address in code.
- Do not rely on floats for stored/returned money amounts.
- Do not introduce a new database or migrate to a new ORM.
