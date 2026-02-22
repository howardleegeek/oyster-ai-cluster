# GEM Sprint 3 Refined Spec — Marketplace & Buyback

## 0. Scope
- Sprint: Week 3
- Goal: 完成二级市场上架/购买/议价与平台回购流程，确保资产归属原子更新。

## 1. Subtask 拆分 (可独立 dispatch)

### S3-ST1 市场与议价数据模型 (复杂度: 中等)
- 文件范围 (3 files):
  - 新建: `app/models/market.py`
  - 新建: `app/schemas/market.py`
  - 修改: `app/models/enums.py`
- 不要碰:
  - `app/models/nft.py`
- Edge cases:
  - `E24`: 最低挂售价限制。
  - `E26`: offer 价不能高于挂售价。
  - `E31`: listing metadata 快照。
- 代码级处理:
  - model 增加 `metadata_snapshot_json` 字段。
  - schema validator: `offer_price < asking_price`。
  - `asking_price >= fmv * 0.5`。
- pytest（顺序: 正常/边界/异常）:
  - `test_listing_price_below_floor_rejected()`。
  - `test_offer_price_must_be_less_than_listing_price()`。
  - `test_listing_snapshot_preserves_metadata_when_nft_changes()`。
- 验收:
  - 表结构支持 listing + offers 全生命周期状态。

### S3-ST2 Marketplace Repository 原子事务 (复杂度: 复杂)
- 文件范围 (3 files):
  - 新建: `app/db/market.py`
  - 修改: `app/db/vault.py`
  - 修改: `app/db/__init__.py`
- 不要碰:
  - `app/db/nft.py`
- Edge cases:
  - `E22`: 卖家下架与买家付款冲突。
  - `E23`: 双买家并发购买。
  - `E29`: 售出后缓存脏读。
  - `E30`: 单用户单 listing 单 active offer。
- 代码级处理:
  - `buy_listing_atomic()` 内部 `SELECT listing FOR UPDATE` + `status == ACTIVE` 再执行。
  - `vault_item.status` 与 `listing.status` 在同一事务更新。
  - offer 建唯一索引 `(listing_id, buyer_id, status in ACTIVE_SET)`。
- pytest（顺序: 正常/边界/异常）:
  - `test_concurrent_buy_only_one_success()`。
  - `test_delist_and_buy_race_results_in_single_terminal_state()`。
  - `test_same_buyer_cannot_create_second_active_offer()`。
- 验收:
  - 压测并发购买无双卖。
  - listing sold 后查询结果不再返回 ACTIVE。

### S3-ST3 Marketplace Service 业务规则 (复杂度: 复杂)
- 文件范围 (3 files):
  - 新建: `app/services/market.py`
  - 修改: `app/services/__init__.py`
  - 新建: `app/services/market_cron.py`
- 不要碰:
  - `app/services/pack_engine.py`
- Edge cases:
  - `E25`: offer 72h 自动过期。
  - `E27`: 接受议价后买家 24h 窗口。
  - `E28`: 禁止自买自卖。
- 代码级处理:
  - `if buyer_id == seller_id: raise UserError.INVALID_REQUEST`。
  - `expire_stale_offers(now_utc)` 定时将 `PENDING->EXPIRED`。
  - offer accepted 后写 `payment_due_at`，超时回滚 listing 状态。
- pytest（顺序: 正常/边界/异常）:
  - `test_self_offer_is_rejected()`。
  - `test_offer_auto_expires_after_72h()`。
  - `test_accepted_offer_expires_if_unpaid_24h()`。
- 验收:
  - cron job 可批量过期报价。
  - 自买行为 100% 拦截。

### S3-ST4 Marketplace API 路由 (复杂度: 中等)
- 文件范围 (3 files):
  - 新建: `app/api/market.py`
  - 修改: `app/app.py`
  - 修改: `app/schemas/market.py`
- 不要碰:
  - `app/api/nft.py`
- Edge cases:
  - `E30`: API 层也做 active offer 冲突提示。
  - `E59`: 全部时间返回 UTC ISO。
- 代码级处理:
  - `GET /market/listings` 支持分页和排序白名单。
  - `PUT /market/offers/{id}` 仅允许 seller 对应 listing 操作。
- pytest（顺序: 正常/边界/异常）:
  - `test_listings_endpoint_filters_status_and_price_range()`。
  - `test_offer_action_forbidden_for_non_seller()`。
  - `test_buy_endpoint_returns_409_when_listing_not_active()`。
- 验收:
  - API 覆盖 listing + buy + offer 全流程。

### S3-ST5 回购模型/Repo/Service (复杂度: 复杂)
- 文件范围 (3 files):
  - 新建: `app/models/buyback.py`
  - 新建: `app/db/buyback.py`
  - 新建: `app/services/buyback.py`
- 不要碰:
  - `app/models/nft.py`
- Edge cases:
  - `E32`: 同一 NFT 不能同时回购和上架。
  - `E33`: 回购价锁定申请时 FMV。
  - `E34`: 每日回购上限。
  - `E35`: 打款失败重试 3 次。
  - `E36`: PENDING 可取消。
- 代码级处理:
  - 申请前 `if vault.status != VAULTED: reject`。
  - `buyback_price = fmv_at_request * Decimal('0.85')` 写死入库。
  - 每日累计金额超阈值返回 `429 BUYBACK_DAILY_LIMIT`。
- pytest（顺序: 正常/边界/异常）:
  - `test_buyback_rejects_non_vaulted_item()`。
  - `test_buyback_price_locked_after_fmv_changes()`。
  - `test_buyback_payout_retries_three_times_then_flags_manual_review()`。
- 验收:
  - 回购申请状态流转完整。
  - 资金上限守卫生效。

### S3-ST6 回购 API 路由 (复杂度: 中等)
- 文件范围 (3 files):
  - 新建: `app/api/buyback.py`
  - 修改: `app/app.py`
  - 新建: `app/schemas/buyback.py`
- 不要碰:
  - `app/api/pack.py`
- Edge cases:
  - `E36`: 仅 PENDING 可取消。
  - `E37`: 审核动作写审计日志（admin 在 Sprint5 接入）。
- 代码级处理:
  - `POST /vault/{vault_item_id}/buyback` 创建申请。
  - `POST /buyback/{request_id}/cancel` 做状态机校验。
- pytest（顺序: 正常/边界/异常）:
  - `test_cancel_buyback_only_when_pending()`。
  - `test_buyback_quote_returns_85_percent_of_fmv()`。
  - `test_buyback_list_returns_user_scoped_data_only()`。
- 验收:
  - 用户可创建/取消/查询回购申请。

### S3-ST7 前端 Marketplace + Buyback 联调 (复杂度: 复杂)
- 文件范围 (3 files):
  - 修改: `components/Marketplace.tsx`
  - 修改: `components/ActionModals.tsx`
  - 新建: `services/marketApi.ts`
- 不要碰:
  - `components/PackOpening.tsx`
- Edge cases:
  - `E22/E23`: 购买失败返回 409 时提示“已售出/状态已变化”。
  - `E25`: UI 显示 offer 剩余时间。
  - `E32`: 非 `VAULTED` 资产禁用 Buyback 按钮。
- 代码级处理:
  - Marketplace 列表改为后端分页数据。
  - BuyModal 支付成功后调用 `/market/listings/{id}/buy` 完成所有权转移。
  - 新增 offer 创建/接受/拒绝入口。
- pytest（顺序: 正常/边界/异常）:
  - `test_marketplace_handles_409_listing_conflict_with_retry_prompt()`。
  - `test_offer_countdown_renders_from_server_expiry()`。
  - `test_buyback_button_disabled_for_listed_items()`。
- 验收:
  - 前端可真实买卖、议价、申请回购。
  - 交易完成后列表与库存同步更新。

## 2. 新增函数签名 (完整)

### 2.1 API Endpoint
```python
# app/api/market.py
@router.get("/market/listings", response_model=schemas.MarketListingPageResp)
def list_market_listings(
    page: int,
    page_size: int,
    rarity: str | None,
    min_price: Decimal | None,
    max_price: Decimal | None,
    sort_by: str,
    market_service: MarketServiceDep,
) -> schemas.MarketListingPageResp

@router.post("/vault/{vault_item_id}/list", response_model=schemas.MarketListingResp)
def create_listing(
    vault_item_id: int,
    req: schemas.CreateListingReq,
    current_user: schemas.UserPrincipal,
    market_service: MarketServiceDep,
) -> schemas.MarketListingResp

@router.post("/market/listings/{listing_id}/delist", response_model=SuccessResp)
def delist_listing(
    listing_id: str,
    current_user: schemas.UserPrincipal,
    market_service: MarketServiceDep,
) -> SuccessResp

@router.post("/market/listings/{listing_id}/buy", response_model=schemas.MarketTradeResp)
def buy_listing(
    listing_id: str,
    req: schemas.BuyListingReq,
    current_user: schemas.UserPrincipal,
    market_service: MarketServiceDep,
) -> schemas.MarketTradeResp

@router.post("/market/listings/{listing_id}/offers", response_model=schemas.MarketOfferResp)
def create_offer(
    listing_id: str,
    req: schemas.CreateOfferReq,
    current_user: schemas.UserPrincipal,
    market_service: MarketServiceDep,
) -> schemas.MarketOfferResp

@router.put("/market/offers/{offer_id}", response_model=schemas.MarketOfferResp)
def respond_offer(
    offer_id: str,
    req: schemas.RespondOfferReq,
    current_user: schemas.UserPrincipal,
    market_service: MarketServiceDep,
) -> schemas.MarketOfferResp

@router.get("/market/offers/mine", response_model=list[schemas.MarketOfferResp])
def list_my_offers(
    role: str,
    current_user: schemas.UserPrincipal,
    market_service: MarketServiceDep,
) -> list[schemas.MarketOfferResp]

# app/api/buyback.py
@router.post("/vault/{vault_item_id}/buyback", response_model=schemas.BuybackRequestResp)
def request_buyback(
    vault_item_id: int,
    current_user: schemas.UserPrincipal,
    buyback_service: BuybackServiceDep,
) -> schemas.BuybackRequestResp

@router.post("/buyback/{request_id}/cancel", response_model=SuccessResp)
def cancel_buyback(
    request_id: str,
    current_user: schemas.UserPrincipal,
    buyback_service: BuybackServiceDep,
) -> SuccessResp

@router.get("/buyback/requests", response_model=list[schemas.BuybackRequestResp])
def list_buyback_requests(
    current_user: schemas.UserPrincipal,
    buyback_service: BuybackServiceDep,
) -> list[schemas.BuybackRequestResp]
```

### 2.2 Service
```python
class MarketService:
    def search_listings(self, query: schemas.MarketSearchReq) -> schemas.MarketListingPageResp
    def create_listing(self, user_id: str, vault_item_id: int, asking_price_usd: Decimal) -> schemas.MarketListingResp
    def delist_listing(self, user_id: str, listing_id: str) -> None
    def buy_listing(self, buyer_id: str, listing_id: str, tx_hash: str) -> schemas.MarketTradeResp
    def create_offer(self, buyer_id: str, listing_id: str, offer_price_usd: Decimal) -> schemas.MarketOfferResp
    def respond_offer(self, seller_id: str, offer_id: str, action: schemas.OfferAction) -> schemas.MarketOfferResp
    def expire_stale_offers(self, now_utc: datetime) -> int

class BuybackService:
    def get_quote(self, user_id: str, vault_item_id: int) -> schemas.BuybackQuoteResp
    def create_request(self, user_id: str, vault_item_id: int) -> schemas.BuybackRequestResp
    def cancel_request(self, user_id: str, request_id: str) -> None
    def process_pending_payouts(self, limit: int = 100) -> int
```

### 2.3 Repository
```python
class MarketRepo:
    def list_active_listings(self, query: schemas.MarketSearchReq) -> tuple[list[models.MarketListing], int]
    def get_listing_for_update(self, listing_id: str) -> models.MarketListing | None
    def create_listing(self, payload: schemas.CreateListingRepoReq) -> models.MarketListing
    def mark_listing_sold(self, listing_id: str, buyer_id: str, sold_at: datetime) -> models.MarketListing
    def mark_listing_cancelled(self, listing_id: str) -> models.MarketListing
    def create_offer(self, payload: schemas.CreateOfferRepoReq) -> models.MarketOffer
    def get_offer_for_update(self, offer_id: str) -> models.MarketOffer | None
    def expire_offers_before(self, cutoff: datetime, limit: int) -> int

class BuybackRepo:
    def create_request(self, payload: schemas.BuybackCreateRepoReq) -> models.BuybackRequest
    def get_request_for_update(self, request_id: str) -> models.BuybackRequest | None
    def list_user_requests(self, user_id: str) -> list[models.BuybackRequest]
    def sum_daily_approved_amount(self, date_utc: date) -> Decimal
    def mark_request_cancelled(self, request_id: str) -> models.BuybackRequest
```

## 3. 前端改造清单 (React)

### 3.1 现有组件修改
- `components/Marketplace.tsx`
  - 替换本地 `items` 过滤排序为后端查询参数。
  - `onBuy` 改为调用 `marketApi.buyListing`。
- `components/ActionModals.tsx`
  - `ListModal` 提交到 `/vault/{id}/list`。
  - `BuyModal` 成功后调用 `/market/listings/{id}/buy`。
  - 新增 Offer 与 Buyback 交互。
- `components/Dashboard.tsx`
  - 在 `VAULTED` 行新增 Buyback 按钮与报价预览。

### 3.2 新建组件/模块
- `services/marketApi.ts`
- 可选: `components/OfferModal.tsx` (若不复用 ActionModals)

### 3.3 API 调用方式
```http
GET /market/listings?page=1&page_size=20&rarity=EPIC&sort_by=PRICE_ASC

POST /vault/{vault_item_id}/list
Body: { "asking_price_usd": "120.00" }

POST /market/listings/{listing_id}/buy
Body: { "tx_hash": "<solana_signature>" }

POST /market/listings/{listing_id}/offers
Body: { "offer_price_usd": "95.00" }

PUT /market/offers/{offer_id}
Body: { "action": "ACCEPT" }

POST /vault/{vault_item_id}/buyback
Body: {}

POST /buyback/{request_id}/cancel
Body: {}
```

## 4. Sprint 3 Edge Case 覆盖矩阵
- 覆盖: `E22 E23 E24 E25 E26 E27 E28 E29 E30 E31 E32 E33 E34 E35 E36 E37 E59`

## 5. 交付验收 (Sprint 级)
- 上架、购买、议价、回购流程全可走通。
- 并发购买无双卖，状态机无非法跃迁。
- 回购价格锁定且具备失败重试。
- 每个 subtask 至少 3 个 pytest 用例通过。
