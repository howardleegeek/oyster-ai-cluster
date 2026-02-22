# GEM Sprint 2 Refined Spec — Pack Engine (Server-authoritative)

## 0. Scope
- Sprint: Week 2
- Goal: 完成盲盒定义、服务端抽卡、支付确认、开包入库 (`user_vault`)。
- 原则: 前端只负责展示动画，结果由后端决定。

## 1. Subtask 拆分 (可独立 dispatch)

### S2-ST1 Pack/Vault 数据模型与 schema (复杂度: 中等)
- 文件范围 (3 files):
  - 新建: `app/models/pack.py`
  - 新建: `app/schemas/pack.py`
  - 修改: `app/models/enums.py`
- 不要碰:
  - `app/models/nft.py`
- Edge cases:
  - `E4`: drop_rate 总和必须等于 100。
  - `E5`: pack status 自动进入 `SOLD_OUT`。
  - `E60`: 金额字段统一 `DECIMAL`。
- 代码级处理:
  - `@validates('drop_rate')` + service 层二次校验总和。
  - `current_supply >= max_supply` 时 status 置 `SOLD_OUT`。
- pytest（顺序: 正常/边界/异常）:
  - `test_drop_table_sum_must_equal_100()`。
  - `test_pack_status_becomes_sold_out_when_supply_reaches_max()`。
  - `test_pack_price_decimal_roundtrip()`。
- 验收:
  - 表结构可迁移创建成功。
  - schema 对非法 `drop_rate` 返回 422。

### S2-ST2 Pack/Vault Repository (复杂度: 复杂)
- 文件范围 (3 files):
  - 新建: `app/db/pack.py`
  - 新建: `app/db/vault.py`
  - 修改: `app/db/__init__.py`
- 不要碰:
  - `app/db/nft.py`
- Edge cases:
  - `E6`: 并发扣库存 `SELECT ... FOR UPDATE`。
  - `E7`: 稀有度池空时降级分配。
  - `E11`: 用户级并发购买锁。
- 代码级处理:
  - `reserve_pack_supply(pack_id, quantity)` 使用事务锁 pack 行。
  - `pick_collection_for_rarity()` 若空池，按 `LEGENDARY->EPIC->RARE->COMMON` 降级。
  - Redis 锁 key: `pack:user:{user_id}` TTL 10s。
- pytest（顺序: 正常/边界/异常）:
  - `test_reserve_supply_rejects_when_insufficient_stock()`。
  - `test_rarity_fallback_when_target_pool_empty()`。
  - `test_user_lock_prevents_parallel_openings()`。
- 验收:
  - 并发 50 请求无超卖。
  - 空稀有度池可稳定回退。

### S2-ST3 抽卡引擎 Service (复杂度: 复杂)
- 文件范围 (3 files):
  - 新建: `app/services/pack_engine.py`
  - 修改: `app/services/__init__.py`
  - 新建: `app/services/pack.py`
- 不要碰:
  - `app/services/nft.py`
- Edge cases:
  - `E1`: 支付成功但未开包，重启补偿。
  - `E8`: 防连点重复开包。
  - `E12`: 随机不可预测。
- 代码级处理:
  - RNG 固定 `secrets.SystemRandom().uniform(0, 100)`。
  - `open_pack_if_paid(opening_id)` 幂等: 若 status 已 `OPENED` 直接返回历史结果。
  - 启动补偿任务扫描 `status=PAID and opened_at is null`。
- pytest（顺序: 正常/边界/异常）:
  - `test_open_pack_is_idempotent_for_same_opening()`。
  - `test_engine_uses_secrets_random_not_math_random()`。
  - `test_recovery_job_opens_paid_unopened_records()`。
- 验收:
  - 抽卡结果无法由前端参数控制。
  - 同一 opening 重放返回同一结果。

### S2-ST4 支付确认 Service (复杂度: 复杂)
- 文件范围 (3 files):
  - 新建: `app/services/payment.py`
  - 新建: `app/db/payment.py`
  - 修改: `app/models/nft.py`  (仅扩展 `nft_payment` 访问索引，不改既有语义)
- 不要碰:
  - `app/plib/web3_ton.py`
- Edge cases:
  - `E2`: tx hash 唯一防重放。
  - `E9`: 交易确认超时进入 `PENDING_CONFIRMATION`。
  - `E13`: 报价锁定 5 分钟。
  - `E14`: 金额容差校验 ±0.5%。
  - `E15`: 多 RPC fallback。
  - `E19`: 定时对账扫 pending。
- 代码级处理:
  - `if repo.exists_tx_hash(tx_hash): return existing_result`。
  - 交易确认失败不直接失败订单，转 pending + async retry。
  - `abs(onchain_amount - expected_amount) > expected*0.005` 则标记异常。
- pytest（顺序: 正常/边界/异常）:
  - `test_tx_hash_duplicate_is_idempotent()`。
  - `test_amount_mismatch_outside_tolerance_rejected()`。
  - `test_rpc_fallback_tries_secondary_endpoint()`。
- 验收:
  - 重复 tx hash 不会重复开包。
  - RPC 主节点故障时可自动切到备节点。

### S2-ST5 Pack/Vault API Router (复杂度: 中等)
- 文件范围 (3 files):
  - 新建: `app/api/pack.py`
  - 新建: `app/api/vault.py`
  - 修改: `app/app.py`
- 不要碰:
  - `app/api/nft.py`
- Edge cases:
  - `E3`: 后端忽略前端传价。
  - `E10`: 余额预检失败给明确错误码。
  - `E59`: UTC 返回。
- 代码级处理:
  - `purchase_pack` 仅接收 `pack_id/quantity`，价格全部 DB 计算。
  - 参数 `quantity` 限制 `1..10`。
- pytest（顺序: 正常/边界/异常）:
  - `test_purchase_pack_recomputes_price_from_db()`。
  - `test_purchase_pack_rejects_quantity_gt_10()`。
  - `test_confirm_payment_returns_opened_items()`。
- 验收:
  - OpenAPI 显示 `/packs/*` `/vault/*`。
  - 端到端支付确认后返回开包结果列表。

### S2-ST6 前端 Pack Store 对接后端 (复杂度: 复杂)
- 文件范围 (3 files):
  - 修改: `App.tsx`
  - 修改: `components/PackOpening.tsx`
  - 新建: `services/packApi.ts`
- 不要碰:
  - `components/GemCard.tsx`
- Edge cases:
  - `E3`: 前端不再传价格字段。
  - `E8`: `Purchase` 按钮 pending 时禁用。
  - `E9`: 展示“支付确认中”状态，支持轮询恢复。
- 代码级处理:
  - `handleOpenPack()` 改为: `POST /packs/{id}/purchase` -> `sendSolPayment` -> `POST /packs/openings/{id}/confirm-payment`。
  - `PackOpening` 改为渲染后端返回 `revealed_gems`，删除 `Math.random()` 生成逻辑。
- pytest（顺序: 正常/边界/异常）:
  - `test_handle_open_pack_calls_backend_before_wallet_transfer()`。
  - `test_pack_opening_uses_server_payload_not_local_rng()`。
  - `test_purchase_button_disabled_while_pending()`。
- 验收:
  - 前端刷新后可根据 opening_id 恢复结果页。
  - 本地 RNG 逻辑已移除。

### S2-ST7 Dashboard Vault 数据接入 (复杂度: 中等)
- 文件范围 (3 files):
  - 修改: `components/Dashboard.tsx`
  - 修改: `types.ts`
  - 新建: `services/vaultApi.ts`
- 不要碰:
  - `components/Marketplace.tsx`
- Edge cases:
  - `E59`: 日期使用 ISO UTC，前端 `toLocaleDateString()` 展示。
  - `E65`: metadata 字段仅文本渲染。
- 代码级处理:
  - Dashboard mount 时调用 `GET /vault`。
  - `GemStatus` 新增 `DELIVERED/BUYBACK` 等后端状态映射。
- pytest（顺序: 正常/边界/异常）:
  - `test_dashboard_maps_vault_status_from_api()`。
  - `test_dashboard_handles_empty_vault()`。
  - `test_vault_date_render_localized_from_utc()`。
- 验收:
  - Dashboard 标签页计数来自后端。
  - 刷新页面不丢失库存。

## 2. 新增函数签名 (完整)

### 2.1 API Endpoint
```python
# app/api/pack.py
@router.get("/packs", response_model=list[schemas.PackResp])
def list_packs(
    series_id: str | None,
    status: str | None,
    pack_service: PackServiceDep,
) -> list[schemas.PackResp]

@router.get("/packs/{pack_id}", response_model=schemas.PackDetailResp)
def get_pack_detail(pack_id: str, pack_service: PackServiceDep) -> schemas.PackDetailResp

@router.get("/packs/{pack_id}/odds", response_model=schemas.PackOddsResp)
def get_pack_odds(pack_id: str, pack_service: PackServiceDep) -> schemas.PackOddsResp

@router.post("/packs/{pack_id}/purchase", response_model=schemas.PackPurchaseResp)
def purchase_pack(
    pack_id: str,
    req: schemas.PackPurchaseReq,
    current_user: schemas.UserPrincipal,
    pack_service: PackServiceDep,
) -> schemas.PackPurchaseResp

@router.post("/packs/openings/{opening_id}/confirm-payment", response_model=schemas.PackOpenResultResp)
def confirm_pack_payment(
    opening_id: str,
    req: schemas.PackPaymentConfirmReq,
    current_user: schemas.UserPrincipal,
    pack_service: PackServiceDep,
) -> schemas.PackOpenResultResp

# app/api/vault.py
@router.get("/vault", response_model=list[schemas.VaultItemResp])
def list_my_vault(
    status: str | None,
    current_user: schemas.UserPrincipal,
    vault_service: VaultServiceDep,
) -> list[schemas.VaultItemResp]

@router.get("/vault/{vault_item_id}", response_model=schemas.VaultItemResp)
def get_vault_item(
    vault_item_id: int,
    current_user: schemas.UserPrincipal,
    vault_service: VaultServiceDep,
) -> schemas.VaultItemResp
```

### 2.2 Service
```python
# app/services/pack.py
class PackService:
    def list_packs(self, series_id: str | None, status: str | None) -> list[schemas.PackResp]
    def get_pack_detail(self, pack_id: str) -> schemas.PackDetailResp
    def get_pack_odds(self, pack_id: str) -> schemas.PackOddsResp
    def create_pack_purchase(self, user_id: str, pack_id: str, quantity: int) -> schemas.PackPurchaseResp
    def confirm_payment_and_open(self, user_id: str, opening_id: str, tx_hash: str, chain: models.Chain) -> schemas.PackOpenResultResp

# app/services/pack_engine.py
class PackEngineService:
    def validate_drop_table(self, pack_id: str) -> None
    def draw_rarity(self, drop_rows: list[models.PackDropTable]) -> models.Rarity
    def draw_nft_for_rarity(self, pack_id: str, rarity: models.Rarity) -> models.NftCollectionMeta
    def open_pack(self, opening_id: str) -> list[models.Nft]
    def recover_paid_unopened(self, batch_size: int = 100) -> int

# app/services/payment.py
class PaymentService:
    def lock_quote(self, opening_id: str, ttl_seconds: int = 300) -> schemas.PriceQuote
    def verify_onchain_payment(self, tx_hash: str, expected_amount: Decimal, chain: models.Chain) -> schemas.PaymentVerifyResult
    def reconcile_pending_payments(self, limit: int = 200) -> int
```

### 2.3 Repository
```python
# app/db/pack.py
class PackRepo:
    def list_packs(self, series_id: str | None, status: str | None) -> list[models.Pack]
    def get_pack_with_drop_table(self, pack_id: str) -> models.Pack | None
    def reserve_pack_supply(self, pack_id: str, quantity: int) -> models.Pack
    def create_pack_opening(self, payload: schemas.PackOpeningCreateReq) -> models.PackOpening
    def mark_opening_paid(self, opening_id: str, payment_id: int) -> models.PackOpening
    def mark_opening_opened(self, opening_id: str, opened_at: datetime) -> models.PackOpening

# app/db/vault.py
class VaultRepo:
    def create_vault_items_for_opening(self, user_id: str, opening_id: str, nft_ids: list[str]) -> list[models.UserVault]
    def list_vault_items(self, user_id: str, status: str | None) -> list[models.UserVault]
    def get_vault_item(self, user_id: str, vault_item_id: int) -> models.UserVault | None

# app/db/payment.py
class PaymentRepo:
    def create_payment_record(self, payload: schemas.PaymentCreateReq) -> models.NftPayment
    def get_by_tx_hash(self, tx_hash: str) -> models.NftPayment | None
    def mark_payment_confirmed(self, payment_id: int, confirmed_at: datetime) -> models.NftPayment
    def mark_payment_pending_confirmation(self, payment_id: int) -> models.NftPayment
    def list_pending_payments(self, limit: int) -> list[models.NftPayment]
```

## 3. 前端改造清单 (React)

### 3.1 修改点 (现有组件)
- `App.tsx`
  - `PACKS` 数据源切换为 `GET /packs`。
  - `handleOpenPack` 改为后端订单流，不再直接以 `getPackPriceInSOL` 为唯一依据。
- `components/PackOpening.tsx`
  - 删除 `Math.random()` 抽卡生成逻辑。
  - 新增 `props.revealedGemsFromServer`。
- `components/Dashboard.tsx`
  - inventory 来自 `/vault`。

### 3.2 新建前端模块
- `services/packApi.ts`
- `services/vaultApi.ts`

### 3.3 API 调用方式
```http
GET /packs?series_id=<optional>&status=ACTIVE
GET /packs/{pack_id}
GET /packs/{pack_id}/odds

POST /packs/{pack_id}/purchase
Body: { "quantity": 1, "pay_currency": "SOL" }
Resp: {
  "opening_id": "uuid",
  "amount_sol": "0.123456789",
  "receiver_wallet": "<base58>",
  "quote_expires_at": "2026-02-11T16:00:00Z"
}

POST /packs/openings/{opening_id}/confirm-payment
Body: { "tx_hash": "<signature>", "chain": "sol" }
Resp: {
  "opening_id": "uuid",
  "status": "OPENED",
  "revealed_items": [{ "vault_item_id": 123, "nft_id": "...", "rarity": "EPIC", "fmv": "300.00" }]
}

GET /vault?status=VAULTED
GET /vault/{vault_item_id}
```

## 4. Sprint 2 Edge Case 覆盖矩阵
- 覆盖: `E1 E2 E3 E4 E5 E6 E7 E8 E9 E10 E11 E12 E13 E14 E15 E19 E59 E60`
- 与本 Sprint 直接相关但仅预留: `E16 E17 E18 E20 E21`（Sprint4 完整落地）

## 5. 交付验收 (Sprint 级)
- 支付成功后开包结果仅由后端决定。
- 并发购买不超卖。
- 重放 tx hash 不重复开包。
- 前端已移除本地抽卡逻辑。
- 每个 subtask 至少 3 个 pytest 可跑通。
