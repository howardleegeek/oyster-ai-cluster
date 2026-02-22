# GEM Sprint 5 Refined Spec — Leaderboard, Admin, Launch Hardening

## 0. Scope
- Sprint: Week 5
- Goal: 排行榜上线、Admin 后台完整 CRUD、生产发布前安全与配置收口。

## 1. Subtask 拆分 (可独立 dispatch)

### S5-ST1 排行榜数据聚合层 (复杂度: 中等)
- 文件范围 (3 files):
  - 新建: `app/db/rank.py`
  - 新建: `app/services/rank.py`
  - 新建: `app/schemas/rank.py`
- 不要碰:
  - `app/services/market.py`
- Edge cases:
  - `E59`: 时间窗口按 UTC 周/月切分。
  - `E60`: 总价值聚合用 Decimal。
- 代码级处理:
  - 周榜 `date_trunc('week', acquired_at_utc)`。
  - 缓存 key: `rank:{period}:{date_anchor}` TTL 300s。
- pytest（顺序: 正常/边界/异常）:
  - `test_weekly_rank_uses_utc_week_boundary()`。
  - `test_monthly_rank_excludes_previous_month_items()`。
  - `test_rank_total_value_uses_decimal_sum()`。
- 验收:
  - 周/月/全时间榜单结果稳定且可分页。

### S5-ST2 排行榜 API + 前端页面 (复杂度: 中等)
- 文件范围 (3 files):
  - 新建: `app/api/rank.py`
  - 修改: `app/app.py`
  - 新建: `components/Leaderboard.tsx`
- 不要碰:
  - `components/PackOpening.tsx`
- Edge cases:
  - `E59`: 前端仅做展示本地化，不改后端时间语义。
- 代码级处理:
  - API `period` 仅允许 `weekly|monthly|all`。
  - 前端支持 period 切换 + handle 搜索。
- pytest（顺序: 正常/边界/异常）:
  - `test_rank_api_rejects_invalid_period()`。
  - `test_rank_api_returns_sorted_desc_by_total_value()`。
  - `test_leaderboard_component_switches_period_query()`。
- 验收:
  - `/rank` 接口与页面联通。

### S5-ST3 Admin 鉴权与审计 (复杂度: 复杂)
- 文件范围 (3 files):
  - 修改: `app/models/user.py`
  - 新建: `app/services/admin_auth.py`
  - 新建: `app/models/admin_audit.py`
- 不要碰:
  - `app/services/auth.py`（仅调用 token 解析）
- Edge cases:
  - `E58`: Admin 权限泄露。
  - `E66`: 管理后台 origin 白名单。
- 代码级处理:
  - user 增加 `role` 字段 (`USER|ADMIN|SUPER_ADMIN`)。
  - `require_admin()` 校验 JWT role + IP 白名单。
  - admin 操作全量写 `admin_audit_logs`。
- pytest（顺序: 正常/边界/异常）:
  - `test_non_admin_cannot_access_admin_routes()`。
  - `test_admin_ip_whitelist_enforced()`。
  - `test_admin_action_writes_audit_log()`。
- 验收:
  - `/admin/*` 全路由受 RBAC 保护。

### S5-ST4 Admin NFT 管理 + 批量导入 (复杂度: 复杂)
- 文件范围 (3 files):
  - 新建: `app/db/admin_nft.py`
  - 新建: `app/services/admin_nft.py`
  - 新建: `app/schemas/admin_nft.py`
- 不要碰:
  - `app/db/nft.py`
- Edge cases:
  - `E55`: JSON 导入格式错误需整批回滚。
  - `E56`: 下架不影响已持有资产。
- 代码级处理:
  - batch import 使用单事务，任何一条失败则 rollback。
  - 下架逻辑只修改 `is_active_for_new_drop`。
- pytest（顺序: 正常/边界/异常）:
  - `test_admin_batch_import_rolls_back_on_schema_error()`。
  - `test_admin_disable_collection_does_not_modify_user_vault()`。
  - `test_admin_nft_crud_validates_required_fields()`。
- 验收:
  - admin 可执行 NFT CRUD 与批量导入，失败时无脏数据。

### S5-ST5 Admin Pack 配置版本化 (复杂度: 复杂)
- 文件范围 (3 files):
  - 新建: `app/db/admin_pack.py`
  - 新建: `app/services/admin_pack.py`
  - 新建: `app/models/pack_version.py`
- 不要碰:
  - `app/services/pack_engine.py`（仅读取生效版本）
- Edge cases:
  - `E54`: 修改概率需新版本，不影响已购买 opening。
  - `E57`: 多 admin 并发修改冲突。
- 代码级处理:
  - pack 配置表新增 `version` + `is_active`。
  - 更新时 `WHERE version = expected_version`，失败返回 409。
- pytest（顺序: 正常/边界/异常）:
  - `test_pack_probability_update_creates_new_version()`。
  - `test_existing_opening_uses_original_pack_version()`。
  - `test_optimistic_lock_conflict_returns_409()`。
- 验收:
  - 概率配置可回溯到版本。
  - 并发编辑不会静默覆盖。

### S5-ST6 Admin 订单/回购/用户运营接口 (复杂度: 复杂)
- 文件范围 (3 files):
  - 新建: `app/db/admin_ops.py`
  - 新建: `app/services/admin_ops.py`
  - 新建: `app/api/admin.py`
- 不要碰:
  - `app/api/order.py`
- Edge cases:
  - `E37`: 回购批量审核二次确认。
  - `E58`: 所有运营动作写审计日志。
- 代码级处理:
  - `approve_buyback_batch(req, require_confirm_token=True)`。
  - 用户禁用仅置 `is_disabled`，不删数据。
- pytest（顺序: 正常/边界/异常）:
  - `test_admin_bulk_buyback_requires_confirm_token()`。
  - `test_admin_order_status_update_validates_transition()`。
  - `test_admin_disable_user_prevents_new_orders_not_data_loss()`。
- 验收:
  - Admin 可处理订单、回购审核、用户禁用。

### S5-ST7 前端 Admin Panel 对接 (复杂度: 复杂)
- 文件范围 (3 files):
  - 新建: `components/AdminPanel.tsx`
  - 新建: `services/adminApi.ts`
  - 修改: `App.tsx`
- 不要碰:
  - `components/GemCard.tsx`
- Edge cases:
  - `E55`: 批量导入失败展示逐条错误。
  - `E57`: 并发编辑冲突后提示“需要刷新最新版本”。
- 代码级处理:
  - `/admin` 路由仅 admin 用户可见。
  - 支持 JSON 导入预校验与服务端错误回显。
- pytest（顺序: 正常/边界/异常）:
  - `test_admin_route_hidden_for_non_admin()`。
  - `test_admin_batch_import_error_rows_rendered()`。
  - `test_admin_pack_edit_conflict_shows_refresh_prompt()`。
- 验收:
  - Admin 前端可覆盖 NFT/Pack/Order/Buyback/User 管理核心路径。

### S5-ST8 上线前安全硬化与主网切换 (复杂度: 复杂)
- 文件范围 (3 files):
  - 修改: `app/config.py`
  - 修改: `app/app.py`
  - 新建: `app/services/security.py`
- 不要碰:
  - `app/plib/web3_sol.py`（仅读取新 RPC 配置）
- Edge cases:
  - `E63`: rate limit + WAF 对接。
  - `E64`: 输入校验与 ORM 参数化。
  - `E65`: 输出转义策略。
  - `E66`: 生产 CORS 收紧。
  - `E67`: 支付 token 独立。
  - `E68`: 移动端 deep link 失败容错（前端配合）。
- 代码级处理:
  - 全局 middleware: IP + user 维度限流。
  - `Settings` 新增 `sol_rpc_primary/secondary/tertiary`。
  - 生产环境 `allow_origins` 仅白名单域名。
- pytest（顺序: 正常/边界/异常）:
  - `test_rate_limit_blocks_excessive_requests()`。
  - `test_prod_cors_rejects_unknown_origin()`。
  - `test_security_headers_present_on_all_responses()`。
- 验收:
  - 生产配置切 mainnet 并通过 smoke test。
  - 安全基线（限流、CORS、输入验证）开启。

## 2. 新增函数签名 (完整)

### 2.1 API Endpoint
```python
# app/api/rank.py
@router.get("/rank", response_model=schemas.RankPageResp)
def get_rankings(
    period: schemas.RankPeriod,
    page: int,
    page_size: int,
    keyword: str | None,
    rank_service: RankServiceDep,
) -> schemas.RankPageResp

# app/api/admin.py
@router.get("/admin/nfts", response_model=schemas.AdminNftPageResp)
def admin_list_nfts(
    page: int,
    page_size: int,
    current_admin: schemas.UserPrincipal,
    admin_ops_service: AdminOpsServiceDep,
) -> schemas.AdminNftPageResp

@router.post("/admin/nfts/batch-import", response_model=schemas.AdminBatchImportResp)
def admin_batch_import_nfts(
    req: schemas.AdminBatchImportReq,
    current_admin: schemas.UserPrincipal,
    admin_nft_service: AdminNftServiceDep,
) -> schemas.AdminBatchImportResp

@router.put("/admin/packs/{pack_id}", response_model=schemas.AdminPackResp)
def admin_update_pack(
    pack_id: str,
    req: schemas.AdminPackUpdateReq,
    current_admin: schemas.UserPrincipal,
    admin_pack_service: AdminPackServiceDep,
) -> schemas.AdminPackResp

@router.put("/admin/packs/{pack_id}/drop-table", response_model=schemas.AdminPackResp)
def admin_update_drop_table(
    pack_id: str,
    req: schemas.AdminDropTableUpdateReq,
    current_admin: schemas.UserPrincipal,
    admin_pack_service: AdminPackServiceDep,
) -> schemas.AdminPackResp

@router.get("/admin/orders", response_model=schemas.AdminOrderPageResp)
def admin_list_orders(
    status: str | None,
    page: int,
    page_size: int,
    current_admin: schemas.UserPrincipal,
    admin_ops_service: AdminOpsServiceDep,
) -> schemas.AdminOrderPageResp

@router.put("/admin/orders/{order_id}/status", response_model=schemas.AdminOrderResp)
def admin_update_order_status(
    order_id: str,
    req: schemas.AdminOrderStatusUpdateReq,
    current_admin: schemas.UserPrincipal,
    admin_ops_service: AdminOpsServiceDep,
) -> schemas.AdminOrderResp

@router.get("/admin/buyback", response_model=schemas.AdminBuybackPageResp)
def admin_list_buyback_requests(
    status: str | None,
    page: int,
    page_size: int,
    current_admin: schemas.UserPrincipal,
    admin_ops_service: AdminOpsServiceDep,
) -> schemas.AdminBuybackPageResp

@router.put("/admin/buyback/{request_id}/approve", response_model=schemas.AdminBuybackResp)
def admin_approve_buyback(
    request_id: str,
    req: schemas.AdminBuybackApproveReq,
    current_admin: schemas.UserPrincipal,
    admin_ops_service: AdminOpsServiceDep,
) -> schemas.AdminBuybackResp

@router.put("/admin/buyback/{request_id}/reject", response_model=schemas.AdminBuybackResp)
def admin_reject_buyback(
    request_id: str,
    req: schemas.AdminBuybackRejectReq,
    current_admin: schemas.UserPrincipal,
    admin_ops_service: AdminOpsServiceDep,
) -> schemas.AdminBuybackResp

@router.get("/admin/users", response_model=schemas.AdminUserPageResp)
def admin_list_users(
    page: int,
    page_size: int,
    keyword: str | None,
    current_admin: schemas.UserPrincipal,
    admin_ops_service: AdminOpsServiceDep,
) -> schemas.AdminUserPageResp

@router.put("/admin/users/{user_id}/disable", response_model=schemas.AdminUserResp)
def admin_disable_user(
    user_id: str,
    req: schemas.AdminDisableUserReq,
    current_admin: schemas.UserPrincipal,
    admin_ops_service: AdminOpsServiceDep,
) -> schemas.AdminUserResp
```

### 2.2 Service
```python
class RankService:
    def get_rankings(self, period: schemas.RankPeriod, page: int, page_size: int, keyword: str | None) -> schemas.RankPageResp

class AdminAuthService:
    def require_admin(self, principal: schemas.UserPrincipal, request_ip: str) -> None
    def log_admin_action(self, admin_id: str, action: str, resource_type: str, resource_id: str, payload: dict[str, Any]) -> None

class AdminNftService:
    def create_nft(self, req: schemas.AdminNftCreateReq, admin_id: str) -> schemas.AdminNftResp
    def update_nft(self, nft_id: str, req: schemas.AdminNftUpdateReq, admin_id: str) -> schemas.AdminNftResp
    def batch_import(self, req: schemas.AdminBatchImportReq, admin_id: str) -> schemas.AdminBatchImportResp

class AdminPackService:
    def update_pack(self, pack_id: str, req: schemas.AdminPackUpdateReq, admin_id: str) -> schemas.AdminPackResp
    def update_drop_table_versioned(self, pack_id: str, req: schemas.AdminDropTableUpdateReq, admin_id: str) -> schemas.AdminPackResp

class AdminOpsService:
    def list_orders(self, req: schemas.AdminOrderQueryReq) -> schemas.AdminOrderPageResp
    def update_order_status(self, order_id: str, req: schemas.AdminOrderStatusUpdateReq, admin_id: str) -> schemas.AdminOrderResp
    def approve_buyback(self, request_id: str, req: schemas.AdminBuybackApproveReq, admin_id: str) -> schemas.AdminBuybackResp
    def reject_buyback(self, request_id: str, req: schemas.AdminBuybackRejectReq, admin_id: str) -> schemas.AdminBuybackResp
    def disable_user(self, user_id: str, req: schemas.AdminDisableUserReq, admin_id: str) -> schemas.AdminUserResp
```

### 2.3 Repository
```python
class RankRepo:
    def fetch_rankings(self, period: schemas.RankPeriod, page: int, page_size: int, keyword: str | None) -> tuple[list[schemas.RankRow], int]

class AdminNftRepo:
    def create_nft(self, payload: schemas.AdminNftCreateReq) -> models.Nft
    def update_nft(self, nft_id: str, payload: schemas.AdminNftUpdateReq) -> models.Nft
    def batch_insert_nfts(self, rows: list[schemas.AdminNftCreateReq]) -> list[models.Nft]

class AdminPackRepo:
    def get_pack_for_update(self, pack_id: str) -> models.Pack | None
    def create_pack_version(self, payload: schemas.PackVersionCreateReq) -> models.PackVersion
    def deactivate_pack_version(self, pack_id: str, version: int) -> None

class AdminOpsRepo:
    def list_orders(self, req: schemas.AdminOrderQueryReq) -> tuple[list[models.RedemptionOrder], int]
    def update_order_status(self, order_id: str, status: str, tracking_number: str | None) -> models.RedemptionOrder
    def list_buyback_requests(self, status: str | None, page: int, page_size: int) -> tuple[list[models.BuybackRequest], int]
    def update_buyback_status(self, request_id: str, status: str, tx_hash: str | None) -> models.BuybackRequest
    def list_users(self, page: int, page_size: int, keyword: str | None) -> tuple[list[models.User], int]
    def disable_user(self, user_id: str, reason: str) -> models.User
```

## 3. 前端改造清单 (React)

### 3.1 现有组件修改
- `App.tsx`
  - 新增 `/leaderboard` 与 `/admin` 路由状态。
  - Navbar 增加入口（仅 admin 显示 admin 入口）。
- `components/Navbar.tsx`
  - 新增 Rank/Admin 导航项。

### 3.2 新建组件/模块
- `components/Leaderboard.tsx`
- `components/AdminPanel.tsx`
- `services/adminApi.ts`

### 3.3 API 调用方式
```http
GET /rank?period=weekly&page=1&page_size=50&keyword=howard

GET /admin/nfts?page=1&page_size=20
POST /admin/nfts/batch-import
Body: { "rows": [{"id":"...","collection_meta_id":1,"fmv":"120.00", ...}] }

PUT /admin/packs/{pack_id}
Body: { "name": "Starter Pack", "price_usd": "29.00", "expected_version": 3 }

PUT /admin/packs/{pack_id}/drop-table
Body: {
  "expected_version": 3,
  "rows": [
    {"rarity":"COMMON","drop_rate":"60.00","nft_collection_meta_id":1},
    {"rarity":"RARE","drop_rate":"30.00","nft_collection_meta_id":2},
    {"rarity":"EPIC","drop_rate":"9.00","nft_collection_meta_id":3},
    {"rarity":"LEGENDARY","drop_rate":"1.00","nft_collection_meta_id":4}
  ]
}

PUT /admin/orders/{order_id}/status
Body: { "status": "SHIPPED", "tracking_number": "YT123..." }

PUT /admin/buyback/{request_id}/approve
Body: { "confirm_token": "2fa-or-confirmation-token" }

PUT /admin/users/{user_id}/disable
Body: { "reason": "abuse" }
```

## 4. Sprint 5 Edge Case 覆盖矩阵
- 覆盖: `E54 E55 E56 E57 E58 E59 E63 E64 E65 E66 E67 E68`

## 5. 交付验收 (Sprint 级)
- 排行榜周/月/总榜上线。
- Admin 面板可完成 NFT/Pack/User/Order/Buyback 管理。
- 概率配置版本化 + 并发冲突处理生效。
- 生产安全基线（RBAC、审计、限流、CORS）开启并通过 smoke test。
- 每个 subtask 至少 3 个 pytest 用例通过。
