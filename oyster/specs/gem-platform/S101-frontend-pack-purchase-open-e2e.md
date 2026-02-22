---
task_id: S101-frontend-pack-purchase-open-e2e
project: gem-platform
priority: 1
depends_on:
  - S100-backend-pack-purchase-open-e2e
modifies:
  - lumina/App.tsx
  - lumina/components/PackOpening.tsx
  - lumina/services/packApi.ts
  - lumina/services/solanaTransactionService.ts
  - lumina/components/
executor: glm
---

## Goal
Make the frontend pack purchase/open experience fully wired to the backend (no local RNG / no placeholder flow) and buildable for production.

User journey:
1) connect wallet + login (wallet-sign)
2) browse packs from backend
3) purchase N packs -> send SOL to backend-provided receiver wallet -> confirm -> reveal items
4) see revealed items in PackOpening UI without runtime errors

## Constraints
- Preserve the existing UI visual style and layout.
- Do not add heavy new dependencies.
- Do not hardcode recipient wallets; always use backend `receiver_wallet`.
- Keep all env config in `.env.example` (no secrets committed).

## Required Changes
- Update `sendSolPayment(...)` so it can send SOL to a dynamic `toWallet` address coming from backend purchase response.
- Update the purchase flow (App / PackStore) to:
  1) call backend `purchasePack(packId, quantity)`
  2) call `sendSolPayment(receiver_wallet, amount_sol)`
  3) call backend `confirmPayment(opening_id, tx_hash, chain)`
  4) pass `revealed_items` into `PackOpening`
- Fix `PackOpening` props/usages so it renders backend-provided revealed items.
- Normalize chain value to match backend expectation (prefer `sol` unless backend specifies otherwise).

## Acceptance Criteria
- `cd lumina && npm ci`
- `cd lumina && npm run build`
- `cd lumina && npx tsc --noEmit`
- Manual smoke (document steps in a short note):
  - with a valid backend running, user can start purchase flow without runtime exception

## Do Not Do
- Do not keep any hardcoded recipient wallet constants in production code.
- Do not leave PackOpening in a state where it requires props that callers do not pass.
