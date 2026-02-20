# Puffy Backend-Frontend Integration Design

**Date**: 2026-02-20
**Status**: Draft (6 rounds of deep analysis complete)
**Approach**: Extend existing puffy-backend to implement Reward Center API spec, then frontend re-generates types via Orval
**Sections**: 31 (covering architecture, security, concurrency, deployment, operations)

---

## Problem

Frontend (`puffy-frontend2`) was built against a Reward Center API at `puffy-dev-2wkdas1.getpuffy.ai`. Backend (`puffy-backend`) is an independent e-commerce system. The two have different routes, schemas, and data models. They have never successfully integrated.

## Solution

Extend `puffy-backend` to implement the full Reward Center OpenAPI spec (28 endpoints) + Device/Pods purchase endpoints (6 endpoints). Frontend then points Orval at the new backend's openapi.json and regenerates all types.

---

## 1. Route Changes

### 1.1 Existing Routes to Modify

| Current Route | New Route | Change |
|---|---|---|
| `GET /user/sign-in` | `GET /sign-in` | Move to root router |
| `POST /user/verify` | `POST /verify` | Move to root router + change request body |
| `GET /user/me` | `GET /user/info` | Rename path |
| `POST /user/update-email` | `POST /user/email` | Rename path |
| `POST /user/twitter-oauth` | `POST /user/twitter-oauth` | Keep + add `redirect_url` field |
| `GET /user/eligible-products` | Keep as-is | Internal use |

### 1.2 New Routes to Implement

**Auth (root router, no prefix):**
| Route | Method | Auth | Description |
|---|---|---|---|
| `/sign-in` | GET | No | Generate session + sign message |
| `/verify` | POST | No | Verify signature, create user, return JWT |
| `/eligible-first` | POST | No | Check eligibility across multiple campaigns |

**Campaign Router (`/campaigns` prefix):**
| Route | Method | Auth | Description |
|---|---|---|---|
| `/campaigns` | GET | No | List all campaigns |
| `/campaigns/{campaign}` | GET | No | Get single campaign |
| `/campaigns/{campaign}/check-eligible` | GET | Yes | Check user eligibility for campaign |
| `/campaigns/{campaign}/check-eligible-dryrun` | GET | No | Dry-run eligibility (query param: wallet) |
| `/campaigns/{campaign}/info` | GET | Yes | Get user's campaign info (returns User) |
| `/campaigns/{campaign}/p` | GET | Yes | Get campaign promotions |
| `/campaigns/{campaign}/referral-relation` | GET | Yes | Get referral relationships |
| `/campaigns/{campaign}/referral` | POST | Yes | Set referral relationship |
| `/campaigns/{campaign}/referral-dryrun` | GET | No | Dry-run referral validation |
| `/campaigns/{campaign}/promotion/{id}/already-paid` | GET | Yes | Check if promotion already paid |
| `/campaigns/{campaign}/promotion/{id}/promote-complete` | GET | Yes | Get promotion completion details |
| `/campaigns/{campaign}/promotion/{id}/promote-mint-gas` | POST | Yes | Record mint gas transaction |
| `/campaigns/{campaign}/discord-auth-code` | GET | No | Generate Discord auth code |
| `/campaigns/{campaign}/discord-auth` | POST | Yes | Authenticate Discord code |
| `/campaigns/{campaign}/discord-auth-dryrun` | POST | No | Dry-run Discord auth |
| `/campaigns/{campaign_id}/eligible-sign-in` | GET | Yes | Eligible user sign-in |
| `/campaigns/{campaign_id}/eligible-verify` | POST | Yes | Verify eligible sign-in |

**Group Campaigns Router:**
| Route | Method | Auth | Description |
|---|---|---|---|
| `/group-campaigns/{group_id}` | GET | No | Get campaigns by group |

**Referral Router (root):**
| Route | Method | Auth | Description |
|---|---|---|---|
| `/referral-relation` | GET | Yes | Get all referral relationships |

**User Router (`/user` prefix):**
| Route | Method | Auth | Description |
|---|---|---|---|
| `/user/info` | GET | Yes | Get current user info |
| `/user/email` | POST | Yes | Update email |
| `/user/twitter-oauth` | POST | Yes | Twitter OAuth |
| `/user/twitter-lock` | GET | Yes | Get Twitter lock status |
| `/user/update-eth-wallet` | POST | Yes | Update ETH wallet |
| `/user/update-ton-wallet` | POST | Yes | Update TON wallet |

**Device/Pods Router (non-Orval, direct axios):**
| Route | Method | Auth | Description |
|---|---|---|---|
| `/device-pass/summary` | GET | Yes | Get device pass summary |
| `/device-pass` | POST | Yes | Create device pass |
| `/device-pass/validate` | POST | Yes | Validate device pass code |
| `/device/quote` | POST | Yes | Get device quote |
| `/device/orders` | POST | Yes | Create device order |
| `/pods/orders` | POST | Yes | Create pods order |

---

## 2. Schema Changes

### 2.1 JWT Token Payload

**Current:**
```python
{"id": "uuid", "address": "solana_pubkey", "exp": timestamp}
```

**New:**
```python
{"user_id": "uuid", "wallet_address": "solana_pubkey", "chain": "sol", "exp": timestamp}
```

Frontend reads `wallet_address` from JWT. This change is required.

### 2.2 Verify Request Body

**Current (flat):**
```python
class UserVerify(BaseModel):
    session_id: str
    address: str
    signature: str
```

**New (nested, matching spec):**
```python
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
    data: SolSignProof | TonSignProof
```

### 2.3 User Schema

**Current (store-focused):**
```python
class User(BaseModel):
    id: str
    address: str
    address_hex: Optional[str]
    twitter_id: Optional[str]
    twitter_name: Optional[str]
    balance: Optional[Balance]
    records: Optional[List[RewardRecord]]
    referral_code: Optional[ReferralCode]
    pass_code: Optional[PassCode]
    promote_nfts: Optional[List[PromoteNft]]
    nfts: Optional[List[Nft]]
```

**New (matching Reward Center spec):**
```python
class User(BaseModel):
    user_id: str
    wallet_address: str
    wallet_address_hex: Optional[str]
    eth_wallet_address: Optional[str]
    ton_wallet_address: Optional[str]
    twitter_id: Optional[str]
    twitter_name: Optional[str]
    twitter_icon_url: Optional[str]
    twitter_locked: Optional[bool]
    email: Optional[str]
    chain: Chain
    points: Optional[int]
    referral_code: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    user_activities: List[UserActivity] = []
    referrals: List[Referral] = []
    nfts: List[PromoteNft] = []
    eligibles: List[UserCampaignEligible] = []
    user_campaign_activities: List[UserCampaignActivity] = []
    products: List[UserProduct] = []
```

Field mapping (DB column -> API field):
- `id` -> `user_id`
- `address` -> `wallet_address`
- `address_hex` -> `wallet_address_hex`
- New: `eth_wallet_address`, `ton_wallet_address`, `twitter_icon_url`, `twitter_locked`, `email`, `chain`, `points`
- Removed from API: `balance`, `records`, `pass_code` (store-internal)
- Added: `user_activities`, `referrals`, `eligibles`, `user_campaign_activities`, `products`

### 2.4 SessionInfo Response

**Current:**
```python
class SessionInfo(BaseModel):
    session_id: str
    message: Optional[str]
```

**New:**
```python
class SessionInfo(BaseModel):
    session_id: str
    message: Optional[str]
    chain: Chain = Chain.SOL
```

### 2.5 TwitterOauth Request

**Current:**
```python
class TwitterOauth(BaseModel):
    auth_code: str
```

**New:**
```python
class TwitterOauth(BaseModel):
    auth_code: str
    redirect_url: str
```

---

## 3. New Database Tables

### 3.1 Campaign System Tables

```sql
-- Core campaign table
CREATE TABLE campaigns (
    campaign_id INT AUTO_INCREMENT PRIMARY KEY,
    campaign_group_id INT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT NULL,
    edition VARCHAR(255) NULL,
    requirement VARCHAR(255) NULL,
    collection_address VARCHAR(255) NOT NULL,
    collection_name VARCHAR(255) NULL,
    chain ENUM('ton','sol','eth','soon','berachain') DEFAULT 'sol',
    vm_type ENUM('svm','evm','tvm') NULL,
    start_date DATETIME NULL,
    end_date DATETIME NULL,
    start_date_timestamp DOUBLE NULL,
    end_date_timestamp DOUBLE NULL,
    `limit` INT DEFAULT 0,
    video_url VARCHAR(512) NULL,
    logo_url VARCHAR(512) NULL,
    promote_image_url VARCHAR(512) NULL,
    nft_gas_fee VARCHAR(50) NULL,
    x_post_url VARCHAR(512) NULL,
    video_poster_url VARCHAR(512) NULL,
    eligible_method VARCHAR(255) NULL,
    is_ready BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NULL
);

-- Activity definitions
CREATE TABLE activities (
    activity_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NULL,
    parameter VARCHAR(255) NULL,
    initiated_by_user BOOLEAN NULL,
    activity_type ENUM('global','campaign') NOT NULL
);

-- Campaign-Activity junction
CREATE TABLE campaign_activities (
    campaign_activity_id INT AUTO_INCREMENT PRIMARY KEY,
    campaign_id INT NOT NULL,
    activity_id INT NOT NULL,
    quantity INT NOT NULL,
    points INT NULL,
    is_required BOOLEAN NULL,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id),
    FOREIGN KEY (activity_id) REFERENCES activities(activity_id)
);

-- Promotions
CREATE TABLE promotions (
    promotion_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NULL,
    description TEXT NULL,
    image_url VARCHAR(512) NULL,
    video_url VARCHAR(512) NULL,
    nft_name VARCHAR(255) NULL,
    nft_symbol VARCHAR(50) NULL,
    nft_description TEXT NULL,
    nft_meta_url VARCHAR(512) NULL,
    nft_collection_id VARCHAR(255) NULL
);

-- Campaign-Promotion junction
CREATE TABLE campaign_promotions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    campaign_id INT NOT NULL,
    promotion_id INT NOT NULL,
    nft_merkletree_id VARCHAR(255) NULL,
    nft_image_url VARCHAR(512) NULL,
    nft_collection_image_url VARCHAR(512) NULL,
    nft_video_url VARCHAR(512) NULL,
    nft_on_chain_image_url VARCHAR(512) NULL,
    nft_text_front_image_url VARCHAR(512) NULL,
    nft_text_front_video_url VARCHAR(512) NULL,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id),
    FOREIGN KEY (promotion_id) REFERENCES promotions(promotion_id)
);

-- User-Campaign eligibility
CREATE TABLE user_campaign_eligibles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    campaign_id INT NOT NULL,
    is_eligible BOOLEAN NULL,
    eligible_method ENUM('eth','sol','ton','soon','berachain','referral','c_referral','bypass','discord') NULL,
    eligible_wallet VARCHAR(255) NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
);

-- User activities (completed tasks)
CREATE TABLE user_activities (
    user_activity_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    activity_id INT NOT NULL,
    points INT NULL,
    campaign_id INT NULL,
    completed_at DATETIME NULL,
    activity_data JSON NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (activity_id) REFERENCES activities(activity_id),
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
);

-- Promote NFTs (campaign-scoped, replaces existing promote_nfts)
CREATE TABLE promote_nfts_v2 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    campaign_id INT NOT NULL,
    promotion_id INT NOT NULL,
    seq INT NULL,
    name VARCHAR(255) NULL,
    symbol VARCHAR(50) NULL,
    image_url VARCHAR(512) NULL,
    video_url VARCHAR(512) NULL,
    on_chain_image_url VARCHAR(512) NULL,
    minted BOOLEAN NULL,
    minted_times INT NULL,
    is_on_chain BOOLEAN NULL,
    token_address VARCHAR(255) NULL,
    collection_address VARCHAR(255) NULL,
    x_post_url VARCHAR(512) NULL,
    referral_id INT NULL,
    referral_code VARCHAR(255) NULL,
    created_at DATETIME NULL,
    status ENUM('new','paid','payment_confirmed','minted','mint_failed','payment_expired') NULL,
    minted_at DATETIME NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id),
    FOREIGN KEY (promotion_id) REFERENCES promotions(promotion_id)
);

-- Campaign referrals (replaces existing referral_codes for campaign context)
CREATE TABLE campaign_referrals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NULL,
    enabled BOOLEAN NULL,
    code_type ENUM('limited','unlimited','gunlimited') NOT NULL,
    code_level INT DEFAULT 1,
    campaign_id INT NOT NULL,
    max_uses INT NOT NULL,
    current_uses INT NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
);

-- Referral relations (who referred whom)
CREATE TABLE referral_relations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    referrer_id VARCHAR(255) NOT NULL,
    referee_id VARCHAR(255) NOT NULL,
    campaign_id INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (referrer_id) REFERENCES users(id),
    FOREIGN KEY (referee_id) REFERENCES users(id),
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
);

-- User products (campaign rewards)
CREATE TABLE user_products (
    id VARCHAR(255) PRIMARY KEY,
    product_id INT NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    source VARCHAR(255) NULL,
    created_at DATETIME NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Campaign products (simple, id=int for Reward Center)
CREATE TABLE rc_products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NULL,
    image_url VARCHAR(512) NULL,
    video_url VARCHAR(512) NULL
);

-- Discord auth codes
CREATE TABLE discord_auth_codes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    campaign_id INT NOT NULL,
    discord_id VARCHAR(255) NOT NULL,
    code VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    used_at DATETIME NULL,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
);

-- Campaign eligible methods (many-to-many)
CREATE TABLE campaign_eligible_methods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    campaign_id INT NOT NULL,
    method ENUM('eth','sol','ton','soon','berachain','referral','c_referral','bypass','discord') NOT NULL,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
);
```

### 3.2 Users Table Changes

```sql
ALTER TABLE users
    ADD COLUMN eth_wallet_address VARCHAR(255) NULL,
    ADD COLUMN ton_wallet_address VARCHAR(255) NULL,
    ADD COLUMN twitter_icon_url VARCHAR(512) NULL,
    ADD COLUMN twitter_locked BOOLEAN NULL DEFAULT FALSE,
    ADD COLUMN email VARCHAR(255) NULL,
    ADD COLUMN chain ENUM('ton','sol','eth','soon','berachain') DEFAULT 'sol';
```

Note: `points` is computed from `balances.points`, no new column needed.

### 3.3 Device/Pods Tables

```sql
-- Device passes
CREATE TABLE device_passes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    code VARCHAR(255) NOT NULL UNIQUE,
    is_used BOOLEAN DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

Device/Pods orders reuse the existing `orders` + `order_items` tables with new product types.

---

## 4. New Backend File Structure

```
app/
├── api/
│   ├── user.py          # Modified: /user/info, /user/email, /user/twitter-oauth, etc.
│   ├── auth.py          # NEW: /sign-in, /verify, /eligible-first
│   ├── campaign.py      # NEW: /campaigns/*, /group-campaigns/*
│   ├── referral.py      # NEW: /referral-relation
│   ├── device.py        # NEW: /device-pass/*, /device/*, /pods/*
│   ├── product.py       # Keep existing
│   └── order.py         # Keep existing
├── models/
│   ├── user.py          # Modified: add new columns
│   ├── campaign.py      # NEW: Campaign, CampaignActivity, CampaignPromotion
│   ├── activity.py      # NEW: Activity
│   ├── promotion.py     # NEW: Promotion, PromoteNftV2
│   ├── eligibility.py   # NEW: UserCampaignEligible
│   ├── user_activity.py # NEW: UserActivity
│   ├── referral.py      # NEW: CampaignReferral, ReferralRelation
│   ├── discord.py       # NEW: DiscordAuthCode
│   ├── device.py        # NEW: DevicePass
│   ├── product.py       # Keep existing
│   └── order.py         # Keep existing
├── schemas/
│   ├── user.py          # Modified: new User schema matching spec
│   ├── auth.py          # NEW: SignInVerify, SolSignProof, TonSignProof, SessionInfo
│   ├── campaign.py      # NEW: Campaign, CampaignActivity, CampaignPromotion
│   ├── activity.py      # NEW: Activity
│   ├── promotion.py     # NEW: Promotion, PromoteNft, PromoteCompleteResp
│   ├── eligibility.py   # NEW: EligibleResp, EligibleResult, EligibleFirstReq, UserCampaignEligible
│   ├── referral.py      # NEW: Referral, ReferralResp, PromoteReferralReq
│   ├── discord.py       # NEW: DiscordAuthCode
│   ├── device.py        # NEW: DevicePass, DeviceQuote, DeviceOrder, PodsOrder
│   └── ...existing...
├── services/
│   ├── campaign.py      # NEW: CampaignService
│   ├── eligibility.py   # NEW: EligibilityService
│   ├── promotion.py     # NEW: PromotionService
│   ├── referral_v2.py   # NEW: CampaignReferralService
│   ├── discord.py       # NEW: DiscordService
│   ├── device.py        # NEW: DeviceService
│   └── ...existing...
├── db/
│   ├── campaign.py      # NEW: CampaignRepo
│   ├── activity.py      # NEW: ActivityRepo
│   ├── promotion.py     # NEW: PromotionRepo
│   ├── eligibility.py   # NEW: EligibilityRepo
│   ├── referral_v2.py   # NEW: CampaignReferralRepo
│   ├── discord.py       # NEW: DiscordRepo
│   ├── device.py        # NEW: DeviceRepo
│   └── ...existing...
├── enums.py             # Modified: add ActivityType, CodeType, EligibleMethod, NftStatus (v2)
└── puffy.py             # Modified: register new routers
```

---

## 5. Enums to Add/Modify

```python
# New enums
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

# Modified: NftStatus (Reward Center version has different values)
class RCNftStatus(str, Enum):
    NEW = "new"
    PAID = "paid"
    PAYMENT_CONFIRMED = "payment_confirmed"
    MINTED = "minted"
    MINT_FAILED = "mint_failed"
    PAYMENT_EXPIRED = "payment_expired"
```

---

## 6. Frontend Changes (Minimal)

1. **Change `orval.config.js`:**
   ```javascript
   input: 'http://localhost:8000/apidoc/openapi.json'
   // was: 'https://puffy-dev-2wkdas1.getpuffy.ai/papidoc/openapi.json'
   ```

2. **Run `npm run generate-api`** to regenerate all types and hooks.

3. **Update `useWalletLogin.tsx`** if hook names change (unlikely since operationIds will match).

4. **Update `.env`:**
   ```
   NEXT_PUBLIC_BACKEND_BASE_URL=http://localhost:8000
   ```

5. **Device/Pods API (`puffyPurchaseApi.ts`)**: No Orval change needed, these are direct axios calls. Just need backend to implement the endpoints.

---

## 7. Migration Strategy

### Phase 1: Schema + Auth (Day 1-2)
- Add new DB columns to `users` table
- Create `SignInVerify`, `SolSignProof`, `TonSignProof` schemas
- Move sign-in/verify to root router
- Change JWT payload to use `user_id`/`wallet_address`
- Update `SessionInfo` to include `chain`
- Update `TwitterOauth` to include `redirect_url`
- Create `/user/info` endpoint (replaces `/user/me`)
- Create `/user/email` endpoint (replaces `/user/update-email`)
- Add `/user/update-eth-wallet`, `/user/update-ton-wallet`
- Add `/user/twitter-lock`

### Phase 2: Campaign System (Day 3-5)
- Create all campaign DB tables
- Implement Campaign, Activity, Promotion models + repos
- Implement CampaignService, EligibilityService, PromotionService
- Implement all 17 campaign endpoints
- Implement `/eligible-first`
- Implement `/referral-relation`
- Implement `/group-campaigns/{group_id}`

### Phase 3: Discord + NFT Minting (Day 6)
- Create DiscordAuthCode table + service
- Implement discord-auth endpoints
- Implement promote-complete and promote-mint-gas

### Phase 4: Device/Pods Purchase (Day 7)
- Create DevicePass table
- Implement `/device-pass/*` endpoints
- Implement `/device/quote`, `/device/orders`
- Implement `/pods/orders`

### Phase 5: Frontend Integration (Day 8)
- Backend OpenAPI spec verified against Reward Center spec
- Frontend Orval regenerate
- End-to-end testing

---

## 8. Existing Functionality Preserved

The following existing backend functionality stays intact:
- **Order system**: `/order/*` routes (create, get, update, pay, cancel)
- **Product catalog**: `/product/` route
- **Discount strategies**: promote_free, passcode
- **Shipping fee calculation**: country-based
- **Vape restriction**: country-based validation
- **Referral/passcode validation**: existing order flow
- **MySQL + Redis infrastructure**: connection pooling, session cache
- **Solana signature verification**: PyNaCl-based

These are internal/store features that the Reward Center frontend doesn't call directly but may be needed later.

---

## 9. Key Decisions

1. **JWT payload changes** (`id`->`user_id`, `address`->`wallet_address`): Required for frontend compatibility. Existing tokens will be invalidated (users re-login).

2. **Dual NftStatus enums**: Store uses `new/minted/mint_failed`, Reward Center uses `new/paid/payment_confirmed/minted/mint_failed/payment_expired`. Keep both as `NftStatus` (store) and `RCNftStatus` (reward center).

3. **Dual Product models**: Store `Product` has price/qty/type, Reward Center `Product` is simpler (id, name, description, image). Keep both: `products` table for store, `rc_products` for reward center.

4. **Campaign path parameter**: Spec uses `{campaign}` (string) not `{campaign_id}` (int) for most routes, but `{campaign_id}` (int) for eligible-sign-in/eligible-verify. Backend should accept both.

5. **TonSignProof support**: Backend currently only verifies Solana signatures. Need to add TON signature verification or stub it for future implementation.

---

## 10. Multi-Chain Wallet Support

Frontend supports three wallet ecosystems. Backend must handle all three for eligibility checks and signature verification.

### 10.1 Solana (Existing)

- **Library**: PyNaCl (`nacl.signing.VerifyKey`)
- **Signature format**: base58-encoded Ed25519
- **Status**: Fully implemented in `app/plib/web3_sol.py`

### 10.2 EVM / Ethereum / Berachain (NEW)

Frontend uses Wagmi + ReOwn AppKit for EVM chains. The airdrop eligibility check flow goes:
1. User connects MetaMask/WalletConnect
2. Frontend calls `/campaigns/{campaign}/check-eligible-dryrun?wallet=0x...`
3. Backend must query EVM chain (Ethereum or Berachain) for NFT holdings

**Needs**:
- EVM signature verification (`eth_sign` / EIP-191 personal_sign) — use `eth_account` or `web3.py`
- EVM RPC calls to check NFT balance (`balanceOf` on ERC-721 collection contract)
- New file: `app/plib/web3_evm.py`
- Config: `EVM_RPC_URL` (Ethereum mainnet), `BERACHAIN_RPC_URL`

### 10.3 TON (NEW — Stub Phase 1, Implement Phase 2)

Frontend uses TonConnect v2. The `TonSignProof` schema is already in the spec:
```python
class TonSignProof(BaseModel):
    signature: str
    state_init: str
    timestamp: int
    public_key: str
    wallet_address_hex: str
    wallet_address_base64: str
```

**Needs**:
- TON proof verification (validate `state_init` + `signature` against `public_key`)
- TON RPC for NFT holdings (TON NFT standard)
- New file: `app/plib/web3_ton.py`
- Library: `tonsdk` or `pytoniq`
- Config: `TON_API_URL`

### 10.4 Verify Endpoint Dispatch

The `/verify` endpoint receives `data: SolSignProof | TonSignProof`. Backend must detect which type and dispatch to the correct verifier:

```python
@router.post("/verify")
def verify(req: SignInVerify, ...):
    if hasattr(req.data, 'state_init'):
        # TonSignProof — dispatch to TON verifier
        result = ton.verify(req.data)
    else:
        # SolSignProof — dispatch to Solana verifier
        result = sol.verify(req.data.address, req.data.signature, message)
```

EVM verify is separate — EVM wallets go through the eligibility flow, not the sign-in/verify flow (EVM users sign in via Solana wallet, EVM wallet is just for NFT eligibility checks).

---

## 11. Orders System Gap

### 11.1 Problem

Frontend's order management (`/profile/orders`) is **entirely mock data from localStorage**:
- `useOrders()` reads from `localStorage` key `ORDERS_STORAGE_KEY`
- `useOrderById()` reads from same localStorage
- After checkout, orders are saved to localStorage only
- Backend's `GET /order/` and `GET /order/{id}` endpoints are never called

### 11.2 Fix Required

**Phase 5 (Frontend Integration)** must include:
1. Replace `useOrders()` to call `GET /order/` from backend
2. Replace `useOrderById()` to call `GET /order/{order_id}`
3. After device/pods checkout, the `POST /device/orders` and `POST /pods/orders` responses should include order IDs that map to real backend orders
4. Remove mock order generation code
5. Add order status polling (backend has no webhooks — frontend must poll)

### 11.3 Order Status Polling

Backend confirms payments via background job (60s interval). Frontend needs to poll:
```typescript
// After order creation, poll every 10 seconds for status change
useQuery({
  queryKey: ['order', orderId],
  queryFn: () => getOrder(orderId),
  refetchInterval: 10_000,  // 10 seconds
  enabled: order?.status === 'new' || order?.status === 'paid',
})
```

---

## 12. Known Backend Bugs to Fix First

These must be resolved before building new features (from `code_review_issues.md`):

### 12.1 Critical

| Bug | File | Impact |
|-----|------|--------|
| `create_user` race condition | `app/db/user.py` | Duplicate users under concurrency |
| Missing `wallet_db` dependency | `app/services/order.py` | `AttributeError` on wallet operations |
| Payment crawler is stubbed | `app/jobs/payment_crawler.py` | No real payment confirmation |

### 12.2 Important

| Bug | File | Impact |
|-----|------|--------|
| Deprecated `.from_orm()` | Multiple schemas | Pydantic v2 deprecation warnings |
| Hardcoded shipping fees | `app/services/order.py` | CN=50, US=50, default=40 not configurable |
| Redis TTL hardcoded | `app/db/cache.py` | 600s not configurable |

### 12.3 Fix Strategy

Add a **Phase 0** before Phase 1:
- Fix `create_user` with `SELECT FOR UPDATE` or DB unique constraint + retry
- Remove or stub `wallet_db` dependency
- Update Pydantic `.from_orm()` → `.model_validate()`
- Make Redis TTL configurable via settings

---

## 13. Database Migration Tooling

### 13.1 Problem

Backend uses `Base.metadata.create_all()` — this only creates tables that don't exist, it cannot:
- Add columns to existing tables
- Modify column types
- Create indices on existing tables

Adding 13 new tables + modifying the `users` table requires proper migration tooling.

### 13.2 Solution

Introduce **Alembic** for migration management:

```bash
pip install alembic
alembic init alembic
```

Migration workflow:
1. `alembic revision --autogenerate -m "add campaign system tables"`
2. Review generated migration
3. `alembic upgrade head` to apply

Add to **Phase 0**: Set up Alembic, create initial migration from current schema, then all new changes go through Alembic.

---

## 14. External Service Dependencies

### 14.1 Existing (Keep)

| Service | Purpose | Config Key |
|---------|---------|------------|
| SendGrid | Email notifications | `sender_account`, `sender_key` |
| Shippo | Address validation | Hardcoded API URL |
| Twitter OAuth | Social auth | `twitter_id`, `twitter_secret` |
| Solana RPC | Signature verify + NFT query | `sol_api_url`, `sol_key` |
| NFT Metadata API | Collection info | `nft_api_url`, `nft_api_key` |

### 14.2 New (Required)

| Service | Purpose | Config Key |
|---------|---------|------------|
| Ethereum RPC | EVM NFT eligibility check | `ETH_RPC_URL` (new) |
| Berachain RPC | Berachain NFT eligibility | `BERACHAIN_RPC_URL` (new) |
| TON API | TON NFT eligibility + proof verify | `TON_API_URL` (new) |
| Discord OAuth | Discord auth for campaigns | `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET` (new) |

### 14.3 Address Validation Gap

Frontend uses Google Places API for address autocomplete, but backend has Shippo for validation. These are not connected. Consider:
- Option A: Backend validates addresses via Shippo on order creation (recommended)
- Option B: Trust frontend-provided addresses (current behavior, less safe)

Decision: **Option A** — add Shippo validation in `POST /device/orders` and `POST /pods/orders` as a non-blocking warning (don't reject orders, just flag).

---

## 15. Health Check & Monitoring

### 15.1 Add Health Endpoint

```python
@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}
```

### 15.2 Add Readiness Check

```python
@app.get("/ready")
def ready(db: Session = Depends(get_db), cache: CacheDb = Depends(get_cache)):
    try:
        db.execute(text("SELECT 1"))
        cache.redis_client.ping()
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(503, detail=str(e))
```

---

## 16. CORS for Development

Current CORS config only applies in `DEV` mode. For frontend-backend integration testing:

```python
if settings.env in ("DEV", "TEST"):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,  # ADD: needed for cookies/auth headers
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

Note: `allow_credentials=True` is required when frontend sends `Authorization` headers.

---

## 17. Revised Migration Strategy

### Phase 0: Foundation (Day 1)
- Fix critical bugs (race condition, wallet_db, deprecated Pydantic)
- Set up Alembic migration tooling
- Add `/health` and `/ready` endpoints
- Fix CORS to include `allow_credentials=True`
- Add EVM/TON RPC config to `.env`

### Phase 1: Auth + User Schema (Day 2-3)
- Alembic migration: add columns to `users` table
- Create `SolSignProof`, `TonSignProof`, `SignInVerify` schemas
- Move sign-in/verify to root router with multi-chain dispatch
- Change JWT payload to `user_id`/`wallet_address`/`chain`
- Implement `/user/info`, `/user/email`, `/user/twitter-lock`
- Implement `/user/update-eth-wallet`, `/user/update-ton-wallet`
- Add `app/plib/web3_evm.py` (EVM signature verification)
- Stub `app/plib/web3_ton.py` (TON — returns True for now)
- Unit tests for all auth changes

### Phase 2: Campaign System (Day 4-6)
- Alembic migration: create 13 campaign tables
- Implement models, repos, services for Campaign/Activity/Promotion
- Implement all 17 `/campaigns/*` endpoints
- Implement `/eligible-first` with multi-chain eligibility check
- Implement `/referral-relation` and `/group-campaigns/{group_id}`
- Eligibility check: query Solana/EVM/TON for NFT holdings per campaign
- Unit + integration tests

### Phase 3: Discord + NFT Minting (Day 7)
- Create DiscordAuthCode table + service
- Implement discord-auth endpoints (3 endpoints)
- Implement promote-complete: generate NFT metadata, return gas fee
- Implement promote-mint-gas: validate SOL transaction hash via RPC, update NFT status
- Integration tests

### Phase 4: Device/Pods Purchase (Day 8)
- Create DevicePass table
- Implement 6 device/pods endpoints
- Wire into existing order system (reuse `orders` + `order_items` tables)
- Quote calculation with device pass / WL discounts
- Tests

### Phase 5: Frontend Integration (Day 9-10)
- Verify backend OpenAPI spec matches Reward Center spec field-by-field
- Frontend: change `orval.config.js` to local backend URL
- Frontend: `npm run generate-api`
- Frontend: replace localStorage orders with real API calls
- Frontend: add order status polling
- Frontend: update `.env` with backend URL
- End-to-end smoke test of all user flows:
  1. Connect wallet → sign-in → verify → authenticated
  2. Check eligibility → claim → mint NFT
  3. Browse products → add to cart → checkout → order created
  4. View profile → points, NFTs, orders

---

## 18. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| EVM NFT query complexity (different contracts per campaign) | High | Medium | Start with single `balanceOf` call, extend per campaign config |
| TON proof verification library maturity | Medium | Medium | Stub first, implement in Phase 2 after research |
| OpenAPI spec drift after regenerate | Medium | High | Diff generated spec against Reward Center spec before frontend regenerate |
| Payment gateway not implemented | High | High | Stub with test mode, real integration in separate project |
| Existing tests break after schema changes | High | Low | Run full test suite after Phase 0, fix before proceeding |

---

## 19. NFT Minting Transaction Flow (Critical Path)

The airdrop → mint NFT flow is the most complex integration point. Both frontend and backend must coordinate precisely.

### 19.1 Frontend Minting Flow (Exact)

1. User clicks "Mint WL NFT" on `/airdrop/step/claim/mint`
2. Frontend calls `GET /campaigns/{name}/promotion/{id}/promote-complete`
   - Backend returns: `{ network, name, symbol, nft_id, gas_fee, status }`
3. Frontend builds a **two-instruction Solana transaction**:
   - Instruction 1: `SystemProgram.transfer` — sends `gas_fee` SOL to `NEXT_PUBLIC_SOLANA_TO_WALLET`
   - Instruction 2: `createMemoInstruction` — JSON memo: `{"nft_id": <int>, "user_id": "<string>"}`
4. User signs and sends the transaction via Phantom/Solflare
5. Frontend waits for transaction confirmation
6. Frontend calls `POST /campaigns/{name}/promotion/{id}/promote-mint-gas`
   - Body: `{ transaction_hash: "<solana_tx_signature>", nft_id: <int> }`
7. Backend verifies the transaction on-chain and triggers NFT minting

### 19.2 Backend Must Implement

**`promote-complete` endpoint:**
- Look up user's NFT record in `promote_nfts_v2`
- If no record exists, create one with `status=new`
- Call internal NFT Metadata API (`get_next_sequence()`) to assign sequence number
- Return gas fee from campaign config (`campaigns.nft_gas_fee`)
- Return NFT metadata (name, symbol, network)

**`promote-mint-gas` endpoint:**
- Receive `transaction_hash` + `nft_id`
- **Verify transaction on Solana RPC** (MISSING in current `sol_api.py`):
  1. Call `getTransaction(tx_hash)` on Solana RPC
  2. Verify destination address matches backend wallet (`NEXT_PUBLIC_SOLANA_TO_WALLET`)
  3. Verify amount matches expected gas fee
  4. Parse memo instruction to extract `nft_id` and `user_id`
  5. Verify `nft_id` and `user_id` match the authenticated user's record
- Update NFT status: `new` → `paid` → trigger minting
- Call NFT Metadata API (`submit_nft_to_api()`) to register on-chain NFT

### 19.3 New: Transaction Verification Method

`sol_api.py` currently fetches transactions but lacks explicit verification. Add:

```python
def verify_mint_transaction(self, tx_hash: str, expected_wallet: str,
                            expected_amount_sol: float, expected_nft_id: int,
                            expected_user_id: str) -> bool:
    """Verify a mint gas fee transaction on Solana."""
    tx = self.connection.get_transaction(tx_hash, encoding="jsonParsed")
    if not tx or not tx.value:
        return False

    # 1. Check transfer instruction
    instructions = tx.value.transaction.message.instructions
    transfer = next((i for i in instructions if i.program == "system"), None)
    if not transfer:
        return False
    if transfer.parsed["info"]["destination"] != expected_wallet:
        return False
    if transfer.parsed["info"]["lamports"] != int(expected_amount_sol * 1e9):
        return False

    # 2. Check memo instruction
    memo_ix = next((i for i in instructions if i.program == "spl-memo"), None)
    if memo_ix:
        memo_data = json.loads(memo_ix.parsed)
        if memo_data.get("nft_id") != expected_nft_id:
            return False
        if memo_data.get("user_id") != expected_user_id:
            return False

    return True
```

### 19.4 Metaplex pNFT Minting (Dual Path)

Frontend also has a `mintSVMpNFT` function that mints **Programmable NFTs** directly on-chain using Metaplex:
- Uses UMI framework + `mpl-core` + `mpl-candy-machine`
- Supports both Solana mainnet and SOON network
- Checks for existing NFT in wallet before minting (dedup)
- Sets 5.5% seller fee (royalty)

This means the backend may need to support **two minting paths**:
1. **Gas fee path**: User pays SOL gas → backend mints via API (promote-mint-gas)
2. **Direct mint path**: Frontend mints pNFT on-chain → backend just records it

Backend needs a way to detect which path was used and update records accordingly.

---

## 20. Email Verification Flow (Missing from Design)

Frontend has email verification endpoints that weren't in the Reward Center OpenAPI spec:

### 20.1 Frontend Calls

```typescript
// POST /user/email/send-code
sendEmailVerificationCode({ email: "user@example.com" })
// Response: { success: boolean, message?: string }

// POST /user/email/verify-code
verifyEmailCode({ email: "user@example.com", code: "123456" })
// Response: { success: boolean, message?: string }
```

### 20.2 Backend Implementation Needed

These are **not** in the Reward Center OpenAPI spec, meaning:
- They won't be auto-generated by Orval
- Frontend calls them via direct axios (in `emailVerification.ts`)
- Backend must add these two endpoints
- Uses existing SendGrid integration for sending OTP codes
- Uses existing Redis/SessionStore for storing verification codes (600s TTL)

### 20.3 Add to Route Table

| Route | Method | Auth | Description |
|---|---|---|---|
| `/user/email/send-code` | POST | Yes | Send 6-digit verification code to email via SendGrid |
| `/user/email/verify-code` | POST | Yes | Verify code, update user email if valid |

---

## 21. Frontend Business Rules Backend Must Enforce

### 21.1 Vape Country Eligibility (CONFLICT)

**Frontend rule** (`puffyRules.ts`): Vape only in `US, CA, GB, DE, FR, AU, JP`

**Backend rule** (`app/services/order.py`): Vape restricted FROM `US, CA, AU, JP, SG, HK`

These are **contradictory**:
- Frontend says US is eligible for Vape
- Backend says US is restricted for Vape

**Decision needed**: Which rule is correct? The frontend rule is newer. Backend should be updated to match:
```python
# Backend should ALLOW vape in these countries (matching frontend):
VAPE_ELIGIBLE_COUNTRIES = {"US", "CA", "GB", "DE", "FR", "AU", "JP"}
# Instead of current RESTRICTED_COUNTRIES approach
```

### 21.2 Device Pricing Rules

Frontend hardcodes `$99` device price. Backend calculates from DB. These must agree:
- WL holders: 1st device free (both sides implement this)
- Device pass holders: device waived
- Regular: $99 USDT

### 21.3 Colorway Rules

WL holders get only "community" colorway. Non-WL get black/white (vape) or silver (fresh). Backend should enforce this when creating device orders.

### 21.4 Pods Options

Vape pods: Peach Oolong, Mint Ice, Watermelon Ice with 0% or 2% nicotine.
Fresh pods: Same flavors, no nicotine selector.
Price: $9.99/box. Backend must validate these constraints.

---

## 22. Session Management Architecture

Backend has **two** session stores that serve different purposes:

| Store | Type | TTL | Purpose |
|-------|------|-----|---------|
| `SessionStore` (in-memory) | Thread-local dict | 600s | OTP verification, sign-in messages |
| `CacheDb` (Redis) | Distributed | 600s (sessions), 12h (data) | JWT session tokens, shared state |

**Problem**: `SessionStore` is in-memory. With uvicorn running 3 workers (`run.sh`), sessions created in worker 1 won't be found by worker 2.

**Fix**: Use Redis (`CacheDb`) for ALL session storage. Remove `SessionStore` or make it a Redis wrapper. This is critical for the sign-in flow — if sign-in creates a session in worker 1 and verify hits worker 2, it fails.

Add to **Phase 0**.

---

## 23. Twitter OAuth PKCE Vulnerability

`app/plib/oauth.py` hardcodes `code_verifier='challenge'`:
```python
data = {
    'code': code,
    'grant_type': 'authorization_code',
    'redirect_uri': redirect_url,
    'code_verifier': 'challenge',  # HARDCODED — should be random
}
```

PKCE requires a random `code_verifier` per session. Frontend generates `code_challenge = SHA256(code_verifier)` and sends it in the authorize URL. Backend must use the **same** `code_verifier` when exchanging.

**Fix**: Store `code_verifier` in Redis when frontend initiates OAuth, retrieve it during callback. Or if frontend always sends the same challenge, document it as a known limitation.

Add to **Phase 0** or **Phase 1** (Twitter OAuth fix).

---

## 24. Revised Phase 0 (Complete List)

Phase 0 now covers all foundation work:

1. Fix `create_user` race condition (add unique constraint retry)
2. Remove `wallet_db` dependency from OrderService
3. Update deprecated `.from_orm()` → `.model_validate()`
4. Make Redis TTL configurable via settings
5. Set up Alembic migration tooling
6. Add `/health` and `/ready` endpoints
7. Fix CORS: add `allow_credentials=True`
8. Add EVM/TON/Discord config keys to `.env`
9. **Replace `SessionStore` with Redis** (fix multi-worker session issue)
10. **Fix Twitter OAuth PKCE** (use random code_verifier stored in Redis)
11. **Add transaction verification to `sol_api.py`** (`verify_mint_transaction()`)
12. **Fix `job_runner.py`** broken imports and context manager misuse
13. **Resolve vape eligibility country list conflict** (align backend with frontend)
14. Run full test suite, fix all broken tests

---

## 25. Updated Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| EVM NFT query complexity | High | Medium | Single `balanceOf` call per campaign |
| TON proof verification maturity | Medium | Medium | Stub first, research libraries |
| OpenAPI spec drift | Medium | High | Diff generated vs reference spec |
| Payment gateway missing | High | High | Stub with test mode |
| Tests break after schema changes | High | Low | Fix in Phase 0 |
| **Multi-worker session loss** | **High** | **Critical** | **Replace SessionStore with Redis** |
| **Vape country rule conflict** | **High** | **Medium** | **Align in Phase 0** |
| **Dual NFT minting paths** | **Medium** | **Medium** | **Document both, implement gas-fee path first** |
| **Email verification not in OpenAPI spec** | **Low** | **Low** | **Add as non-Orval endpoints** |
| **Twitter PKCE vulnerability** | **Medium** | **Low** | **Fix in Phase 0** |

---

## 26. Security Audit (Round 4)

### 26.1 Backend Security Issues

| # | Issue | Severity | File | Fix |
|---|-------|----------|------|-----|
| 1 | `print("#########settings", Settings())` exposes ALL secrets to stdout | 🔴 CRITICAL | app/config.py:44 | Remove print statement |
| 2 | Token logged in error messages: `logger.info("invalid token %s", token)` | 🟠 HIGH | app/services/token.py:44,47,50 | Log only token prefix |
| 3 | No rate limiting on ANY endpoint | 🔴 CRITICAL | All routes | Add SlowAPI middleware |
| 4 | No pagination on list endpoints (DoS vector) | 🔴 CRITICAL | app/api/order.py, product.py | Add limit/offset params |
| 5 | Session not invalidated after verify (signature replay window) | 🔴 CRITICAL | app/api/user.py:79-102 | Delete session after successful verify |
| 6 | Passcode increment not atomic (race condition) | 🟠 HIGH | app/db/order.py:62-66 | Use SQL `SET current_uses = current_uses + 1 WHERE current_uses < max_uses` |
| 7 | No JWT revocation/blacklist mechanism | 🟡 MEDIUM | app/services/token.py | Add Redis-based token blacklist |
| 8 | No refresh token mechanism | 🟡 MEDIUM | - | Consider adding for better UX |
| 9 | Email field accepts any string, no format validation | 🟡 LOW | app/schemas/order.py:46 | Add `EmailStr` validator |
| 10 | Twitter OAuth logs `client_id` at debug level | 🟡 MEDIUM | app/plib/oauth.py | Remove credential logging |

### 26.2 Frontend Security Issues

| # | Issue | Severity | File | Fix |
|---|-------|----------|------|-----|
| 1 | `rejectUnauthorized: false` disables TLS verification | 🔴 CRITICAL | src/lib/axios.ts:5 | Remove — use default `true` |
| 2 | Orval code injection vulnerability (GHSA-h526-wf6g-67jv) | 🔴 CRITICAL | package.json @orval/* | `npm audit fix` / upgrade orval |
| 3 | JWT stored in localStorage (XSS target) | 🟠 HIGH | useWalletLogin.tsx:112 | Consider httpOnly cookie |
| 4 | No 401 auto-logout handler | 🟠 HIGH | custom-instance.ts | Add axios response interceptor |
| 5 | CORS headers set to wildcard `*` on client-side | 🟠 HIGH | axios.ts:12 | Remove client-side CORS headers |
| 6 | Remote images allow wildcard hostname `**` | 🟠 HIGH | next.config.ts:13,17 | Restrict to `getpuffy.ai` domains |
| 7 | No server-side price validation (client-side only) | 🟠 HIGH | checkout/page.tsx | Backend must validate prices |
| 8 | Console.log exposes full API responses | 🟡 MEDIUM | axios.ts:36 | Remove in production |
| 9 | No global React error boundary | 🟡 MEDIUM | - | Add ErrorBoundary component |

### 26.3 ShippingAddress Field Name Mismatch (NEW)

Frontend sends:
```
{ name, email, phone, line1, line2, city, state, postal_code, country }
```

Backend expects:
```
{ id, name, email, phone_number, address_line_1, address_line_2, city, state, postal_code, country, pccc }
```

**Mismatched fields**: `phone` vs `phone_number`, `line1` vs `address_line_1`, `line2` vs `address_line_2`. Backend also requires `id` which frontend doesn't send.

**Fix**: Backend ShippingAddress schema must adopt frontend naming.

---

## 27. Concurrency & Race Conditions (Round 5)

### 27.1 Order State Machine — NO VALIDATION

Backend has **zero validation** for order state transitions:
- `update_order()` is generic, allows setting ANY status at ANY time
- Cancelled orders can be set back to PAID
- Payment crawler can confirm already-cancelled orders

**Fix**: Add state machine validation:
```python
VALID_TRANSITIONS = {
    OrderStatus.NEW: {OrderStatus.PAID, OrderStatus.CANCELLED},
    OrderStatus.PAID: {OrderStatus.CONFIRMED, OrderStatus.EXPIRED, OrderStatus.REFUNDED},
    OrderStatus.CONFIRMED: {OrderStatus.PROCESSING, OrderStatus.REFUNDED},
    OrderStatus.PROCESSING: {OrderStatus.SHIPPED},
    OrderStatus.SHIPPED: {OrderStatus.DELIVERED},
    OrderStatus.CANCELLED: set(),  # terminal
    OrderStatus.DELIVERED: set(),  # terminal
}
```

### 27.2 Referral/Passcode Double-Use Race Condition

`validate_referral_code()` reads `current_uses < max_uses` → TRUE for two concurrent requests → both succeed.

**Fix**: Use atomic SQL:
```sql
UPDATE referral_codes SET current_uses = current_uses + 1
WHERE code = ? AND current_uses < max_uses
-- Check rows_affected == 1
```

### 27.3 Payment Crawler Bugs

1. Two separate `db.commit()` calls (order + payment) — not atomic
2. No job deduplication — if crawler takes >60s, overlap occurs
3. Broken imports: `Annotated` not imported in payment_crawler.py
4. `time` not imported in job_runner.py

**Fix**: Single transaction for order+payment update, add Redis-based distributed lock for job, fix imports.

### 27.4 Multi-Wallet Identity Split

Same user with Solana + Ethereum wallets → two separate user accounts. No account linking mechanism.

**Fix (Phase 2)**: Primary wallet (Solana) creates user. `update-eth-wallet` and `update-ton-wallet` link secondary wallets to existing user by `user_id` (JWT-authenticated).

### 27.5 Twitter Account Double-Linking

No unique constraint on `twitter_id` column. Two users can link same Twitter account.

**Fix**: Add `UNIQUE` constraint on `users.twitter_id` and check before update.

### 27.6 ReferralCodeUsage / PassCodeUsage Tables Never Written To

Audit tables exist but are never populated. Cannot track who used which code.

**Fix**: Write usage records when codes are redeemed.

---

## 28. Frontend Edge Cases (Round 5)

### 28.1 Wallet Disconnect Mid-Flow

No abort mechanism if wallet changes during sign-in. In-flight mutations (`signinMutation`, `verifyEligible`) continue with stale wallet.

**Fix**: Add AbortController; cancel in-flight requests when `publicKey` changes.

### 28.2 Cart Multi-Tab Desync

Cart in localStorage; no cross-tab sync via `storage` event listener. User in Tab A may checkout with stale cart from Tab B.

**Fix**: Add `window.addEventListener('storage', syncCart)` in CartContext.

### 28.3 Stale Quote at Checkout

Device quote cached for 5 minutes (`gcTime: 5 * 60_000`). No timestamp validation. User could submit 2-hour-old quote.

**Fix**: Store quote timestamp; re-fetch if >30 seconds old before order submission.

### 28.4 No Route Protection Middleware

Client-side `useEffect` redirect with 500ms delay → flash of unauthenticated content.

**Fix**: Add `src/middleware.ts` for server-side auth check on `/profile/*`, `/checkout/*`.

### 28.5 No Axios Timeout

No `timeout` configured in axios — requests can hang indefinitely.

**Fix**: Add `timeout: 15000` to axios config.

### 28.6 Device + Pods Order Non-Atomic

Separate API calls for device and pods orders. If device succeeds but pods fails → partial order.

**Fix**: Backend should accept combined device+pods order in single endpoint, or frontend should handle rollback.

### 28.7 JWT Expiry Not Monitored

Token loaded from localStorage but never checked for expiry. Requests fail silently with 401 after 24h.

**Fix**: Decode JWT `exp` on load; set timer to logout/refresh before expiry.

---

## 29. Deployment & Operations (Round 6)

### 29.1 Backend Production Readiness: 3/10

| Component | Status | Issue |
|-----------|--------|-------|
| Process management | ⚠️ | Custom bash script, no graceful shutdown, no auto-restart |
| Health checks | ❌ | No `/health` or `/ready` endpoints |
| Logging | ⚠️ | Plain text, no structured JSON, no request IDs, no APM |
| DB migrations | ❌ | `create_all()` only, no Alembic |
| DB backups | ⚠️ | Template script only, not automated |
| Dependency pinning | ⚠️ | Most packages unpinned (`uvicorn`, `redis`, `PyJWT`, etc.) |
| CI/CD | ❌ | No pipeline, tests run manually |
| Error handling | ⚠️ | No circuit breakers, no retries for external services |
| Secrets | 🔴 | `.env` plaintext, `secret=abc` default, no vault |
| Rate limiting | ❌ | None |
| Response compression | ❌ | Not configured |
| Connection pool | ⚠️ | No `pool_pre_ping`, no timeout, max 10 connections |

### 29.2 Frontend Production Readiness: 3.4/10

| Component | Status | Issue |
|-----------|--------|-------|
| Build config | ✅ | Next.js 16, proper scripts |
| Testing | ❌ | Zero tests, no CI/CD |
| SEO | ❌ | Minimal meta tags, no sitemap, no OG tags |
| CSP | ❌ | No Content Security Policy headers |
| Security headers | ❌ | No X-Frame-Options, HSTS, etc. |
| Middleware | ❌ | No auth middleware for protected routes |
| Bundle size | ⚠️ | Dual UI libraries (antd + MUI), dual animation libs |
| Dependencies | ⚠️ | `@faker-js/faker` in production deps, all versions loose |
| Console logs | ⚠️ | Exposed in production builds |

### 29.3 Backend N+1 Query Pattern

In order creation (`app/services/order.py`):
```python
for item_create in order_create.order_items:
    product_db = self.product_db.get_product(item_create.product_id)  # N+1!
```

5-item order = 5 separate DB queries. Fix: batch load products in single query.

### 29.4 User Relationship Eager Loading

`get_user()` eagerly loads ALL relationships (balance, referral_code, pass_code, records, nfts). If user has 10K NFTs → memory explosion.

**Fix**: Use lazy loading by default; eager load only when needed.

---

## 30. Expanded Phase 0 (Complete List — All 6 Rounds)

Phase 0 must now cover ALL foundation work discovered across rounds 1-6:

### Security (CRITICAL)
1. Remove `print(Settings())` from config.py (exposes secrets)
2. Stop logging full JWT tokens in token.py
3. Add SlowAPI rate limiting middleware (sign-in: 5/min, verify: 10/min, email: 3/min)
4. Add pagination to all list endpoints (default limit=20, max=100)
5. Invalidate session after successful verify (prevent signature replay)
6. Make passcode/referral increment atomic (SQL-level)
7. Add `UNIQUE` constraint on `users.twitter_id`
8. Fix `rejectUnauthorized: false` in frontend axios.ts

### Bugs
9. Fix `create_user` race condition (unique constraint + retry)
10. Remove `wallet_db` dependency from OrderService
11. Update deprecated `.from_orm()` → `.model_validate()`
12. Fix broken imports in `payment_crawler.py` and `job_runner.py`
13. Fix `payment.success` NOT NULL without default

### Infrastructure
14. Set up Alembic migration tooling
15. Add `/health` and `/ready` endpoints
16. Fix CORS: add `allow_credentials=True`
17. Replace in-memory `SessionStore` with Redis
18. Fix Twitter OAuth PKCE (random code_verifier in Redis)
19. Add Solana transaction verification method (`verify_mint_transaction()`)
20. Make Redis TTL configurable via settings
21. Add `pool_pre_ping=True` to SQLAlchemy engine
22. Pin all Python dependency versions in requirements.txt
23. Add axios `timeout: 15000` in frontend

### Data Integrity
24. Add order state machine validation (valid transitions only)
25. Resolve vape eligibility country list conflict (align with frontend)
26. Fix ShippingAddress field name mismatch (adopt frontend naming)
27. Write to ReferralCodeUsage/PassCodeUsage audit tables
28. Run full test suite, fix all broken tests

---

## 31. Final Risk Assessment (All 6 Rounds)

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **Settings printed to stdout (secrets leak)** | **Certain** | **Critical** | **Remove print() — Phase 0 #1** |
| **No rate limiting (brute force/DoS)** | **High** | **Critical** | **Add SlowAPI — Phase 0 #3** |
| **TLS disabled in frontend** | **Certain** | **Critical** | **Remove rejectUnauthorized:false — Phase 0 #8** |
| **Orval code injection CVE** | **High** | **Critical** | **npm audit fix** |
| **Signature replay window** | **High** | **High** | **Delete session after verify — Phase 0 #5** |
| **Order state machine bypass** | **High** | **High** | **Add transition validation — Phase 0 #24** |
| **Referral double-use race** | **High** | **High** | **Atomic SQL — Phase 0 #6** |
| **Payment crawler non-atomic** | **Medium** | **High** | **Single transaction** |
| **Multi-worker session loss** | **High** | **Critical** | **Redis sessions — Phase 0 #17** |
| **N+1 queries in order creation** | **High** | **Medium** | **Batch product loading** |
| EVM NFT query complexity | High | Medium | Single `balanceOf` per campaign |
| TON proof verification maturity | Medium | Medium | Stub first |
| OpenAPI spec drift | Medium | High | Diff generated vs reference |
| Payment gateway missing | High | High | Stub with test mode |
| Frontend no tests | Certain | Medium | Add Vitest in Phase 5 |
| JWT in localStorage (XSS) | Medium | High | Consider httpOnly cookie |
| Cart multi-tab desync | Medium | Medium | Add storage event listener |
| No auth middleware (flash) | High | Low | Add Next.js middleware |
| No structured logging | High | Medium | Add JSON logging in Phase 0 |
