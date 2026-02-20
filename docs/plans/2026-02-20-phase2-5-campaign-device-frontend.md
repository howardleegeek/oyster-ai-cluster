# Phase 2-5: Campaign System, NFT, Device/Pods, Frontend — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the complete Campaign/Promotion/Eligibility system, NFT minting flow, Device/Pods purchase endpoints, and integrate with frontend via Orval regeneration.

**Architecture:** Layer-by-layer (models → repos → services → API) for each domain. Alembic for all schema changes. TDD throughout.

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, pytest, Orval (frontend)

**Working Directory:** `/Users/howardli/Downloads/.claude/worktrees/modest-jennings/puffy-backend`

**Depends On:** Phase 0 + Phase 1 complete

---

## PHASE 2: Campaign System (13 tables, 17+ endpoints)

### Task 1: Alembic Migration — Create All Campaign Tables

**Files:**
- Create: 13 new SQLAlchemy models
- Create: Alembic migration

**Step 1: Create campaign models**

```python
# app/models/campaign.py — ALL campaign-related models
```

Models to create (reference design doc Section 3.1):
- `Campaign` — campaign_id (int PK auto), campaign_group_id, name, description, edition, requirement, collection_address, collection_name, chain (Enum), vm_type (Enum), start_date, end_date, start/end_date_timestamp, limit, video_url, logo_url, promote_image_url, nft_gas_fee, x_post_url, video_poster_url, eligible_method, is_ready, is_active
- `Activity` — activity_id (int PK auto), name, description, parameter, initiated_by_user, activity_type (Enum)
- `CampaignActivity` — campaign_activity_id (int PK auto), campaign_id (FK), activity_id (FK), quantity, points, is_required
- `Promotion` — promotion_id (int PK auto), name, description, image_url, video_url, nft_name, nft_symbol, nft_description, nft_meta_url, nft_collection_id
- `CampaignPromotion` — id (int PK auto), campaign_id (FK), promotion_id (FK), nft_merkletree_id, nft_image_url, nft_collection_image_url, nft_video_url, nft_on_chain_image_url, nft_text_front_image_url, nft_text_front_video_url
- `UserCampaignEligible` — id (int PK auto), user_id (FK), campaign_id (FK), is_eligible, eligible_method (Enum), eligible_wallet
- `UserActivity` — user_activity_id (int PK auto), user_id (FK), activity_id (FK), points, campaign_id (FK), completed_at, activity_data (JSON)
- `PromoteNftV2` — id (int PK auto), user_id (FK), campaign_id (FK), promotion_id (FK), seq, name, symbol, image/video urls, minted, minted_times, is_on_chain, token_address, collection_address, x_post_url, referral_id, referral_code, created_at, status (RCNftStatus Enum), minted_at
- `CampaignReferral` — id (int PK auto), user_id (FK), enabled, code_type (Enum), code_level, campaign_id (FK), max_uses, current_uses
- `ReferralRelation` — id (int PK auto), referrer_id (FK), referee_id (FK), campaign_id (FK), created_at
- `UserProduct` — id (str PK), product_id (int FK), user_id (FK), source, created_at
- `RCProduct` — id (int PK auto), name, description, image_url, video_url
- `DiscordAuthCode` — id (int PK auto), campaign_id (FK), discord_id, code, user_id (FK nullable), created_at, used_at
- `CampaignEligibleMethod` — id (int PK auto), campaign_id (FK), method (EligibleMethod Enum)

**Step 2: Add new enums to app/enums.py**

```python
class ActivityType(str, Enum):
    GLOBAL = "global"
    CAMPAIGN = "campaign"

class CodeType(str, Enum):
    LIMITED = "limited"
    UNLIMITED = "unlimited"
    GUNLIMITED = "gunlimited"

class EligibleMethod(str, Enum):
    ETH = "eth"
    SOL = "sol"
    TON = "ton"
    SOON = "soon"
    BERACHAIN = "berachain"
    REFERRAL = "referral"
    C_REFERRAL = "c_referral"
    BYPASS = "bypass"
    DISCORD = "discord"

class RCNftStatus(str, Enum):
    NEW = "new"
    PAID = "paid"
    PAYMENT_CONFIRMED = "payment_confirmed"
    MINTED = "minted"
    MINT_FAILED = "mint_failed"
    PAYMENT_EXPIRED = "payment_expired"
```

**Step 3: Generate and apply migration**

```bash
alembic revision --autogenerate -m "add campaign system tables (13 tables)"
alembic upgrade head
```

**Step 4: Run tests, commit**

```bash
git add app/models/campaign.py app/enums.py alembic/versions/
git commit -m "feat: add 13 campaign system tables and enums via Alembic"
```

---

### Task 2: Campaign Schemas

**Files:**
- Create: `app/schemas/campaign.py`
- Create: `app/schemas/activity.py`
- Create: `app/schemas/promotion.py`
- Create: `app/schemas/eligibility.py`
- Create: `app/schemas/referral.py`
- Create: `app/schemas/discord.py`
- Test: `tests/unit/test_campaign_schemas.py`

Create Pydantic schemas matching the Orval-generated `fastAPI.schemas.ts` types exactly. Key schemas:

- `Campaign` — All 23 optional fields from frontend spec
- `CampaignActivity` — campaign_activity_id, activity, quantity, points, is_required
- `CampaignPromotion` — all NFT image/video URLs
- `EligibleResp` / `EligibleResult` — is_eligible, method, wallet
- `PromoteNft` (v2) — all minting fields
- `Referral` / `ReferralResp` — code, uses, relations
- `DiscordAuthCode` — code, discord_id

**Commit:** `feat: add campaign, activity, promotion, eligibility, referral schemas`

---

### Task 3: Campaign Repository Layer

**Files:**
- Create: `app/db/campaign.py`
- Create: `app/db/activity.py`
- Create: `app/db/promotion.py`
- Create: `app/db/eligibility.py`
- Create: `app/db/referral_v2.py`
- Create: `app/db/discord.py`
- Test: `tests/unit/test_campaign_repo.py`

Each repo follows the existing pattern (class with db: Session, CRUD methods, Annotated dependency).

Key methods:
- `CampaignRepo.get_campaigns()`, `get_campaign(name)`, `get_campaigns_by_group(group_id)`
- `ActivityRepo.get_activities(campaign_id)`
- `PromotionRepo.get_promotions(campaign_id)`, `get_promote_nft(user_id, campaign_id, promotion_id)`
- `EligibilityRepo.check_eligible(user_id, campaign_id)`, `create_eligible()`
- `ReferralV2Repo.get_referrals(user_id, campaign_id)`, `create_referral()`, `create_relation()`
- `DiscordRepo.create_code()`, `get_code()`, `use_code()`

**Commit:** `feat: add campaign system repository layer (6 repos)`

---

### Task 4: Campaign Service Layer

**Files:**
- Create: `app/services/campaign.py`
- Create: `app/services/eligibility.py`
- Create: `app/services/promotion.py`
- Create: `app/services/referral_v2.py`
- Create: `app/services/discord.py`
- Test: `tests/unit/test_campaign_service.py`

Services contain business logic:
- `CampaignService` — list/get campaigns, check ready/active
- `EligibilityService` — check eligibility across chains (call web3_sol, web3_evm, web3_ton), eligible-first (multi-campaign check)
- `PromotionService` — promote-complete (generate NFT metadata, return gas fee), promote-mint-gas (verify tx, update status)
- `ReferralV2Service` — create referral code, set relation, validate referral
- `DiscordService` — generate auth code, verify auth, dryrun

**Commit:** `feat: add campaign system service layer (5 services)`

---

### Task 5: Campaign API Router (17 endpoints)

**Files:**
- Create: `app/api/campaign.py`
- Modify: `app/puffy.py` (register router)
- Test: `tests/api/test_campaign_api.py`

Endpoints (all under `/campaigns` prefix):
1. `GET /campaigns` — list all campaigns
2. `GET /campaigns/{campaign}` — get single campaign
3. `GET /campaigns/{campaign}/check-eligible` — (auth) check eligibility
4. `GET /campaigns/{campaign}/check-eligible-dryrun` — query param `wallet`
5. `GET /campaigns/{campaign}/info` — (auth) get user's campaign info
6. `GET /campaigns/{campaign}/p` — (auth) get promotions
7. `GET /campaigns/{campaign}/referral-relation` — (auth) get referral tree
8. `POST /campaigns/{campaign}/referral` — (auth) set referral
9. `GET /campaigns/{campaign}/referral-dryrun` — query param `referral_code`
10. `GET /campaigns/{campaign}/promotion/{id}/already-paid` — query param `after`
11. `GET /campaigns/{campaign}/promotion/{id}/promote-complete` — (auth) NFT metadata + gas fee
12. `POST /campaigns/{campaign}/promotion/{id}/promote-mint-gas` — (auth) record mint tx
13. `GET /campaigns/{campaign}/discord-auth-code` — query param `discord_id`
14. `POST /campaigns/{campaign}/discord-auth` — (auth) verify discord
15. `POST /campaigns/{campaign}/discord-auth-dryrun` — dryrun discord
16. `GET /campaigns/{campaign_id}/eligible-sign-in` — (auth) eligible sign-in
17. `POST /campaigns/{campaign_id}/eligible-verify` — (auth) verify eligible

Additional routers:
- `GET /group-campaigns/{group_id}` — campaigns by group
- `GET /referral-relation` — (auth) all referral relations
- `POST /eligible-first` — multi-campaign eligibility check

**Commit:** `feat: add campaign API router with 17 endpoints`

---

### Task 6: Phase 2 Integration Tests

**Files:**
- Test: `tests/api/test_campaign_integration.py`

Test the full flow:
1. Create campaign in DB
2. Call /campaigns — see it listed
3. Call /campaigns/{name} — get details
4. Sign in, get token
5. Call check-eligible — get result
6. Call promotion endpoints

**Commit:** `test: Phase 2 campaign system integration tests`

---

## PHASE 3: Discord + NFT Minting

### Task 7: Discord Auth Service

**Files:**
- Already created in Phase 2 (Task 4: `app/services/discord.py`)
- Wire up: discord-auth-code, discord-auth, discord-auth-dryrun endpoints

Discord OAuth flow:
1. `/discord-auth-code?discord_id=xxx` — generate random code, store in DB
2. `/discord-auth` — verify code, link discord to user
3. `/discord-auth-dryrun` — validate without saving

**Commit:** `feat: implement Discord auth endpoints for campaign eligibility`

---

### Task 8: Promote-Complete Endpoint

**Files:**
- Modify: `app/services/promotion.py`
- Modify: `app/api/campaign.py`

Logic:
1. Look up user's PromoteNftV2 record
2. If none, create with status=NEW
3. Call NftApi.get_next_sequence()
4. Return: `{ network, name, symbol, nft_id, gas_fee, status }`

**Commit:** `feat: implement promote-complete endpoint (NFT metadata + gas fee)`

---

### Task 9: Promote-Mint-Gas Endpoint

**Files:**
- Modify: `app/services/promotion.py`
- Modify: `app/api/campaign.py`

Logic:
1. Receive `{ transaction_hash, nft_id }`
2. Call `sol_api.verify_mint_transaction()`
3. Update PromoteNftV2 status: NEW → PAID → PAYMENT_CONFIRMED
4. Call NftApi.submit_nft_to_api()
5. Update status: → MINTED

**Commit:** `feat: implement promote-mint-gas endpoint with Solana tx verification`

---

## PHASE 4: Device/Pods Purchase

### Task 10: DevicePass Table + Endpoints

**Files:**
- Create: `app/models/device.py` — DevicePass model
- Create: `app/schemas/device.py` — DevicePass, DeviceQuote, DeviceOrder, PodsOrder schemas
- Create: `app/db/device.py` — DeviceRepo
- Create: `app/services/device.py` — DeviceService
- Create: `app/api/device.py` — 6 endpoints
- Modify: `app/puffy.py` — register router
- Test: `tests/api/test_device_api.py`

Alembic migration for DevicePass table.

Endpoints:
1. `GET /device-pass/summary` — get user's device pass info
2. `POST /device-pass` — create device pass
3. `POST /device-pass/validate` — validate pass code
4. `POST /device/quote` — calculate device quote with discounts
5. `POST /device/orders` — create device order (reuse existing order system)
6. `POST /pods/orders` — create pods order

Key business rules from frontend `puffyRules.ts`:
- WL holders: 1st device free, "community" colorway only
- Non-WL: $99, black/white (vape) or silver (fresh)
- Pods: $9.99/box, 3 flavors, nicotine 0%/2% for vape only
- Vape: only in eligible countries

**Commit:** `feat: add device/pods purchase endpoints with pass validation and quoting`

---

## PHASE 5: Frontend Integration

### Task 11: Verify Backend OpenAPI Spec

**Files:**
- None (verification only)

**Step 1: Start backend locally**

```bash
cd /Users/howardli/Downloads/.claude/worktrees/modest-jennings/puffy-backend
uvicorn app.puffy:puffy --host 0.0.0.0 --port 8000
```

**Step 2: Fetch and compare OpenAPI specs**

```bash
# Backend spec
curl http://localhost:8000/apidoc/openapi.json > /tmp/backend_spec.json

# Reference spec (from frontend)
cp ../puffy-frontend2/openapi.json /tmp/reference_spec.json

# Diff key endpoints
python3 -c "
import json
backend = json.load(open('/tmp/backend_spec.json'))
reference = json.load(open('/tmp/reference_spec.json'))
backend_paths = set(backend.get('paths', {}).keys())
reference_paths = set(reference.get('paths', {}).keys())
missing = reference_paths - backend_paths
print('Missing from backend:', missing)
extra = backend_paths - reference_paths
print('Extra in backend:', extra)
"
```

**Step 3: Fix any missing endpoints/schemas**

---

### Task 12: Frontend — Update Orval Config

**Files:**
- Modify: `../puffy-frontend2/orval.config.js`
- Modify: `../puffy-frontend2/.env` (or `env.example`)

**Step 1: Change Orval input URL**

```javascript
// orval.config.js
module.exports = {
  puffy: {
    input: 'http://localhost:8000/apidoc/openapi.json',
    // was: 'https://puffy-dev-2wkdas1.getpuffy.ai/papidoc/openapi.json'
    // ...rest stays same
  }
};
```

**Step 2: Update .env**

```
NEXT_PUBLIC_BACKEND_BASE_URL=http://localhost:8000
```

**Step 3: Regenerate API types**

```bash
cd /Users/howardli/Downloads/.claude/worktrees/modest-jennings/puffy-frontend2
npm run generate-api
```

**Step 4: Check for TypeScript errors**

```bash
npx tsc --noEmit
```

**Step 5: Fix any type mismatches**

**Step 6: Commit**

```bash
git add orval.config.js src/types/api/ .env
git commit -m "feat: point Orval at local backend, regenerate all API types"
```

---

### Task 13: Frontend — Replace localStorage Orders with Real API

**Files:**
- Modify: `../puffy-frontend2/src/hooks/` (useOrders, useOrderById)
- Modify: `../puffy-frontend2/src/app/profile/orders/` (order pages)

**Step 1: Replace useOrders()**

Replace localStorage reads with calls to `GET /order/` from Orval-generated hooks.

**Step 2: Replace useOrderById()**

Replace localStorage reads with calls to `GET /order/{orderId}`.

**Step 3: Add order status polling**

After checkout, poll order status every 10 seconds:
```typescript
useQuery({
  queryKey: ['order', orderId],
  queryFn: () => getOrder(orderId),
  refetchInterval: 10_000,
  enabled: order?.status === 'new' || order?.status === 'paid',
})
```

**Step 4: Remove mock order generation code**

**Step 5: Commit**

```bash
git add src/hooks/ src/app/profile/orders/
git commit -m "feat: replace localStorage orders with real backend API calls"
```

---

### Task 14: Frontend — Add 401 Interceptor

**Files:**
- Modify: `../puffy-frontend2/src/lib/custom-instance.ts`

**Step 1: Add response interceptor**

```typescript
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('puffy_token_campaign');
      window.location.href = '/sign-in';
    }
    return Promise.reject(error);
  }
);
```

**Step 2: Commit**

```bash
git add src/lib/custom-instance.ts
git commit -m "feat: add 401 auto-logout interceptor"
```

---

### Task 15: End-to-End Smoke Test

**Manual test checklist:**

1. ✅ Connect Phantom wallet → GET /sign-in → sign message → POST /verify → JWT received
2. ✅ GET /user/info → user profile with wallet_address, chain
3. ✅ GET /campaigns → list of campaigns
4. ✅ GET /campaigns/{name}/check-eligible → eligibility status
5. ✅ Browse products → add to cart → POST /device/quote → checkout
6. ✅ POST /device/orders → order created
7. ✅ GET /order/ → order appears in list
8. ✅ Profile → points, NFTs, orders all display

**Commit:**

```bash
git commit -m "feat: Phase 5 complete — frontend-backend integration verified"
```

---

## Summary: All Phases

| Phase | Tasks | Focus | Est. Days |
|-------|-------|-------|-----------|
| 0 | 25 | Foundation fixes (security, bugs, infra) | 1-2 |
| 1 | 12 | Auth + User Schema refactor | 2-3 |
| 2 | 6 | Campaign system (13 tables, 17 endpoints) | 3-4 |
| 3 | 3 | Discord auth + NFT minting flow | 1-2 |
| 4 | 1 | Device/Pods purchase (6 endpoints) | 1-2 |
| 5 | 5 | Frontend integration + E2E test | 2-3 |
| **Total** | **52** | | **10-16 days** |

## File Count Estimate

| Category | New Files | Modified Files |
|----------|-----------|----------------|
| Models | 3 | 2 |
| Schemas | 7 | 3 |
| Repos | 6 | 2 |
| Services | 6 | 2 |
| API Routes | 4 | 3 |
| Tests | 15+ | 5 |
| Migrations | 3-5 | 0 |
| Config | 2 | 3 |
| Frontend | 0 | 5 |
| **Total** | **~46** | **~25** |
