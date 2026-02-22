# GEM Sprint 4 Refined Spec — Currency, Redemption, Referral

## 0. Scope
- Sprint: Week 4
- Goal: 打通充值到账、平台余额、多 NFT 实物兑换、物流更新、推荐奖励。

## 1. Subtask 拆分 (可独立 dispatch)

### S4-ST1 Wallet/Deposit 数据模型 (复杂度: 中等)
- 文件范围 (3 files):
  - 修改: `app/models/wallet.py`
  - 新建: `app/schemas/wallet.py`
  - 修改: `app/models/enums.py`
- 不要碰:
  - `app/models/market.py`
- Edge cases:
  - `E17`: 入账与余额更新事务一致性。
  - `E20`: webhook 重复投递幂等。
  - `E60`: 金额精度。
- 代码级处理:
  - `deposits.external_tx_id` unique。
  - `users.credit_balance` 更新与 `deposit.status=CONFIRMED` 同事务提交。
- pytest（顺序: 正常/边界/异常）:
  - `test_confirm_deposit_updates_balance_atomically()`。
  - `test_duplicate_external_tx_id_rejected()`。
  - `test_wallet_balance_decimal_precision()`。
- 验收:
  - deposits 表支持 `CREDIT_CARD/SOLANA_USDC/CROSS_CHAIN_STABLE`。

### S4-ST2 Wallet Repository 与余额账本 (复杂度: 复杂)
- 文件范围 (3 files):
  - 新建: `app/db/wallet.py`
  - 新建: `app/db/ledger.py`
  - 修改: `app/db/__init__.py`
- 不要碰:
  - `app/db/market.py`
- Edge cases:
  - `E16`: Stripe 成功但 webhook 丢失需对账。
  - `E19`: pending 交易定时核对。
  - `E61`: 连接池压力下分页扫描。
- 代码级处理:
  - `reconcile_pending_deposits(limit)` 批次扫描，避免长事务。
  - ledger 记录 `before_balance/after_balance/reason`。
- pytest（顺序: 正常/边界/异常）:
  - `test_reconcile_marks_stripe_charge_confirmed()`。
  - `test_pending_deposits_batch_scan_limits_rows()`。
  - `test_ledger_written_for_every_balance_change()`。
- 验收:
  - 余额变动可审计追溯。
  - 对账任务可幂等重跑。

### S4-ST3 支付集成 Service (Stripe + USDC) (复杂度: 复杂)
- 文件范围 (3 files):
  - 新建: `app/services/wallet_payment.py`
  - 新建: `app/services/stripe_webhook.py`
  - 修改: `app/services/__init__.py`
- 不要碰:
  - `app/services/pack_engine.py`
- Edge cases:
  - `E13`: 报价锁定时间窗。
  - `E14`: 链上金额容差校验。
  - `E15`: RPC fallback。
  - `E18`: 收款地址固定不可输入。
  - `E21`: Phantom revoke 提示。
- 代码级处理:
  - `create_stripe_intent` 写 `deposit` 为 `PENDING`。
  - webhook 验签失败直接 400，不写库。
  - `confirm_usdc_deposit` 校验 token mint + recipient + amount。
- pytest（顺序: 正常/边界/异常）:
  - `test_stripe_webhook_signature_invalid_returns_400()`。
  - `test_usdc_confirm_rejects_wrong_recipient()`。
  - `test_quote_expired_requires_reprice()`。
- 验收:
  - 信用卡与 USDC 两条入账链路均可确认到账。

### S4-ST4 Wallet API Router (复杂度: 中等)
- 文件范围 (3 files):
  - 新建: `app/api/wallet.py`
  - 新建: `app/api/webhooks.py`
  - 修改: `app/app.py`
- 不要碰:
  - `app/api/market.py`
- Edge cases:
  - `E20`: webhook 幂等。
  - `E66`: webhook CORS/鉴权隔离（仅 server-to-server）。
- 代码级处理:
  - webhook endpoint 不走用户 JWT，走 Stripe 签名头。
  - `POST /wallet/deposit/usdc/confirm` 走 JWT + tx 校验。
- pytest（顺序: 正常/边界/异常）:
  - `test_get_wallet_balance_requires_auth()`。
  - `test_stripe_webhook_duplicate_event_is_idempotent()`。
  - `test_usdc_confirm_endpoint_rejects_invalid_tx_hash()`。
- 验收:
  - `/wallet/balance` `/wallet/deposit/*` 可用。

### S4-ST5 Redemption Model/Repo/Service (复杂度: 复杂)
- 文件范围 (3 files):
  - 修改: `app/models/order.py`
  - 新建: `app/db/order.py`
  - 新建: `app/services/order.py`
- 不要碰:
  - `app/models/nft.py`
- Edge cases:
  - `E38`: 非 `VAULTED` 禁止兑换。
  - `E39`: 国家黑名单拦截。
  - `E40`: 运费锁定 30 分钟。
  - `E41`: Shippo 地址校验。
  - `E42`: 发货后 NFT 状态变更。
  - `E44`: item 级状态聚合订单状态。
  - `E45`: 发货后禁止改地址。
- 代码级处理:
  - `create_redemption_order` 事务锁定所有 `vault_item_id`。
  - `validate_address` false 时直接拒绝下单。
  - `update_order_status` 时同步更新 `user_vault.status`。
- pytest（顺序: 正常/边界/异常）:
  - `test_redeem_rejects_listed_vault_items()`。
  - `test_shipping_fee_quote_expires_after_30min()`。
  - `test_shipped_order_cannot_change_address()`。
- 验收:
  - 支持多 NFT 单订单兑换。
  - 地址校验失败不会扣除资产。

### S4-ST6 Redemption API Router (复杂度: 中等)
- 文件范围 (3 files):
  - 新建: `app/api/order.py`
  - 新建: `app/schemas/order.py`
  - 修改: `app/app.py`
- 不要碰:
  - `app/api/nft.py`
- Edge cases:
  - `E43`: 海关扣件状态 `CUSTOMS_HOLD`。
  - `E44`: order/item 状态一致性展示。
- 代码级处理:
  - `POST /orders/redeem` 支持 `vault_item_ids: list[int]`。
  - `GET /orders/{id}` 返回 item 级 tracking。
- pytest（顺序: 正常/边界/异常）:
  - `test_redeem_endpoint_accepts_multiple_vault_items()`。
  - `test_order_detail_includes_item_level_status()`。
  - `test_customs_hold_status_supported()`。
- 验收:
  - 用户可查询订单明细与物流状态。

### S4-ST7 Referral Repo/Service/API (复杂度: 中等)
- 文件范围 (3 files):
  - 新建: `app/db/referral.py`
  - 新建: `app/services/referral.py`
  - 新建: `app/api/referral.py`
- 不要碰:
  - `app/services/auth.py`（仅调用其用户数据）
- Edge cases:
  - `E51`: 禁止自用推荐码。
  - `E52`: 一个用户仅可使用一次。
  - `E53`: 奖励在首单消费后发放。
- 代码级处理:
  - `if referrer_id == referred_id: reject`。
  - `if user.referred_by is not null: reject`。
  - `issue_reward_if_first_paid_order()` 监听首单事件。
- pytest（顺序: 正常/边界/异常）:
  - `test_use_referral_code_rejects_self_referral()`。
  - `test_user_can_apply_referral_code_only_once()`。
  - `test_reward_issued_only_after_first_paid_order()`。
- 验收:
  - 推荐码生成/使用/历史查询可用。

### S4-ST8 前端充值+兑换+推荐联调 (复杂度: 复杂)
- 文件范围 (3 files):
  - 修改: `components/ActionModals.tsx`
  - 修改: `components/Dashboard.tsx`
  - 新建: `services/walletApi.ts`
- 不要碰:
  - `components/PackOpening.tsx`
- Edge cases:
  - `E39`: 国家黑名单前端实时提示。
  - `E40`: 运费报价倒计时。
  - `E45`: SHIPPED 订单禁编辑地址。
- 代码级处理:
  - RedeemModal 改为多选 NFT + 地址表单 + 费用预估。
  - Dashboard 新增余额充值入口 + 推荐码面板。
- pytest（顺序: 正常/边界/异常）:
  - `test_redeem_modal_blocks_blacklisted_country()`。
  - `test_shipping_quote_countdown_expiry_triggers_requote()`。
  - `test_dashboard_referral_panel_loads_history()`。
- 验收:
  - 充值后余额实时更新。
  - 多 NFT 兑换流程可完成下单。

## 2. 新增函数签名 (完整)

### 2.1 API Endpoint
```python
# app/api/wallet.py
@router.get("/wallet/balance", response_model=schemas.WalletBalanceResp)
def get_wallet_balance(
    current_user: schemas.UserPrincipal,
    wallet_service: WalletServiceDep,
) -> schemas.WalletBalanceResp

@router.post("/wallet/deposit/stripe/intent", response_model=schemas.StripeIntentResp)
def create_stripe_deposit_intent(
    req: schemas.StripeDepositIntentReq,
    current_user: schemas.UserPrincipal,
    wallet_service: WalletServiceDep,
) -> schemas.StripeIntentResp

@router.post("/wallet/deposit/usdc/confirm", response_model=schemas.DepositConfirmResp)
def confirm_usdc_deposit(
    req: schemas.UsdcDepositConfirmReq,
    current_user: schemas.UserPrincipal,
    wallet_service: WalletServiceDep,
) -> schemas.DepositConfirmResp

@router.post("/wallet/deposit/cross-chain/quote", response_model=schemas.CrossChainQuoteResp)
def create_cross_chain_quote(
    req: schemas.CrossChainQuoteReq,
    current_user: schemas.UserPrincipal,
    wallet_service: WalletServiceDep,
) -> schemas.CrossChainQuoteResp

# app/api/webhooks.py
@router.post("/webhooks/stripe", response_model=SuccessResp)
def stripe_webhook(
    request: Request,
    stripe_service: StripeWebhookServiceDep,
) -> SuccessResp

# app/api/order.py
@router.post("/orders/redeem", response_model=schemas.RedemptionOrderResp)
def create_redemption_order(
    req: schemas.RedemptionCreateReq,
    current_user: schemas.UserPrincipal,
    order_service: OrderServiceDep,
) -> schemas.RedemptionOrderResp

@router.get("/orders", response_model=list[schemas.RedemptionOrderResp])
def list_my_orders(
    current_user: schemas.UserPrincipal,
    order_service: OrderServiceDep,
) -> list[schemas.RedemptionOrderResp]

@router.get("/orders/{order_id}", response_model=schemas.RedemptionOrderDetailResp)
def get_order_detail(
    order_id: str,
    current_user: schemas.UserPrincipal,
    order_service: OrderServiceDep,
) -> schemas.RedemptionOrderDetailResp

@router.put("/orders/{order_id}/address", response_model=schemas.RedemptionOrderResp)
def update_order_address(
    order_id: str,
    req: schemas.ShippingAddressUpdateReq,
    current_user: schemas.UserPrincipal,
    order_service: OrderServiceDep,
) -> schemas.RedemptionOrderResp

# app/api/referral.py
@router.get("/referral/code", response_model=schemas.ReferralCodeResp)
def get_my_referral_code(
    current_user: schemas.UserPrincipal,
    referral_service: ReferralServiceDep,
) -> schemas.ReferralCodeResp

@router.post("/referral/use", response_model=SuccessResp)
def use_referral_code(
    req: schemas.UseReferralCodeReq,
    current_user: schemas.UserPrincipal,
    referral_service: ReferralServiceDep,
) -> SuccessResp

@router.get("/referral/history", response_model=list[schemas.ReferralHistoryResp])
def list_referral_history(
    current_user: schemas.UserPrincipal,
    referral_service: ReferralServiceDep,
) -> list[schemas.ReferralHistoryResp]
```

### 2.2 Service
```python
class WalletService:
    def get_balance(self, user_id: str) -> schemas.WalletBalanceResp
    def create_stripe_intent(self, user_id: str, amount_usd: Decimal) -> schemas.StripeIntentResp
    def confirm_usdc_deposit(self, user_id: str, tx_hash: str, amount_usd: Decimal) -> schemas.DepositConfirmResp
    def create_cross_chain_quote(self, user_id: str, source_chain: str, amount_usd: Decimal) -> schemas.CrossChainQuoteResp
    def reconcile_pending_deposits(self, limit: int = 200) -> int

class StripeWebhookService:
    def process_event(self, payload: bytes, sig_header: str) -> None

class OrderService:
    def create_redemption(self, user_id: str, req: schemas.RedemptionCreateReq) -> schemas.RedemptionOrderResp
    def list_orders(self, user_id: str) -> list[schemas.RedemptionOrderResp]
    def get_order_detail(self, user_id: str, order_id: str) -> schemas.RedemptionOrderDetailResp
    def update_shipping_address(self, user_id: str, order_id: str, req: schemas.ShippingAddressUpdateReq) -> schemas.RedemptionOrderResp
    def handle_shipping_webhook(self, tracking_number: str, status: str, payload: dict[str, Any]) -> None

class ReferralService:
    def get_or_create_code(self, user_id: str) -> schemas.ReferralCodeResp
    def apply_code(self, user_id: str, referral_code: str) -> None
    def list_history(self, user_id: str) -> list[schemas.ReferralHistoryResp]
    def issue_reward_if_first_paid_order(self, user_id: str, order_id: str) -> None
```

### 2.3 Repository
```python
class WalletRepo:
    def get_user_balance(self, user_id: str) -> Decimal
    def create_deposit(self, payload: schemas.DepositCreateReq) -> models.Deposit
    def confirm_deposit_and_credit(self, deposit_id: str, confirmed_at: datetime) -> models.Deposit
    def get_deposit_by_external_tx(self, external_tx_id: str) -> models.Deposit | None
    def list_pending_deposits(self, limit: int) -> list[models.Deposit]

class LedgerRepo:
    def append_entry(self, payload: schemas.LedgerEntryCreateReq) -> models.WalletLedger

class OrderRepo:
    def create_redemption_order(self, payload: schemas.RedemptionCreateRepoReq) -> models.RedemptionOrder
    def add_redemption_items(self, order_id: str, vault_item_ids: list[int]) -> list[models.RedemptionOrderItem]
    def list_orders_by_user(self, user_id: str) -> list[models.RedemptionOrder]
    def get_order_with_items(self, user_id: str, order_id: str) -> models.RedemptionOrder | None
    def update_order_status(self, order_id: str, status: models.RedemptionOrderStatus) -> models.RedemptionOrder

class ReferralRepo:
    def get_referral_code(self, user_id: str) -> str | None
    def set_referral_code(self, user_id: str, referral_code: str) -> None
    def get_user_by_referral_code(self, referral_code: str) -> models.User | None
    def apply_referral(self, user_id: str, referrer_id: str) -> None
    def create_reward(self, referrer_id: str, referred_id: str, reward_amount: Decimal) -> models.ReferralReward
    def list_rewards(self, user_id: str) -> list[models.ReferralReward]
```

## 3. 前端改造清单 (React)

### 3.1 修改现有组件
- `components/ActionModals.tsx`
  - `RedeemModal` 增加国家、电话、地址验证、多件选择。
- `components/Dashboard.tsx`
  - 增加充值入口、推荐码展示、订单追踪入口。
- `App.tsx`
  - 增加 Wallet/Orders/Referral 视图路由状态。

### 3.2 新建组件/模块
- `services/walletApi.ts`
- 可选: `components/DepositPanel.tsx`, `components/OrderTrackingTable.tsx`, `components/ReferralPanel.tsx`

### 3.3 API 调用方式
```http
GET /wallet/balance
POST /wallet/deposit/stripe/intent
Body: { "amount_usd": "200.00" }
Resp: { "client_secret": "...", "deposit_id": "uuid" }

POST /wallet/deposit/usdc/confirm
Body: { "tx_hash": "...", "amount_usd": "200.00" }

POST /orders/redeem
Body: {
  "vault_item_ids": [101, 102, 103],
  "shipping_address": {
    "shipping_name": "Howard Li",
    "shipping_address_line1": "...",
    "shipping_city": "San Francisco",
    "shipping_state": "CA",
    "shipping_postal_code": "94105",
    "shipping_country_code": "US",
    "shipping_phone": "+1..."
  }
}

GET /orders
GET /orders/{order_id}
PUT /orders/{order_id}/address

GET /referral/code
POST /referral/use
Body: { "referral_code": "GEMABCD1" }
GET /referral/history
```

## 4. Sprint 4 Edge Case 覆盖矩阵
- 覆盖: `E13 E14 E15 E16 E17 E18 E19 E20 E21 E38 E39 E40 E41 E42 E43 E44 E45 E51 E52 E53 E60`

## 5. 交付验收 (Sprint 级)
- Stripe 与 USDC 入账两条链路可用且幂等。
- 多 NFT 兑换+地址验证+物流状态更新可用。
- 推荐码规则符合“一次性使用 + 首单后奖励”。
- 每个 subtask 至少 3 个 pytest 通过。
