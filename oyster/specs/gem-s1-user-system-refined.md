# GEM Sprint 1 Refined Spec — User System & Backend Skeleton

## 0. Scope
- Sprint: Week 1
- Goal: 在不重写现有 `nft-mgmt-api` 架构的前提下，补齐用户系统、认证链路、JWT 鉴权、基础 profile API。
- Codebase:
  - Backend: `/Users/howardli/Downloads/oyster-org/nft-mgmt-api`
  - Frontend: `/Users/howardli/Downloads/lumina-source-code`

## 1. Subtask 拆分 (可独立 dispatch)

### S1-ST1 补齐缺失模型文件 (复杂度: 简单)
- 目标: 修复 `models/__init__.py` 的缺失引用，解除启动阻塞。
- 文件范围 (3 files):
  - 新建: `app/models/order.py`
  - 新建: `app/models/wallet.py`
  - 新建: `app/models/community.py`
- 不要碰:
  - `app/models/nft.py`
  - `app/db/nft.py`
  - `app/api/nft.py`
- Edge cases:
  - `E61`: 模型导入失败导致连接池初始化被阻断；三文件必须定义最小可映射 ORM class，避免 `ImportError`。
  - `E62`: Redis 不可用时不应影响模型导入；模型文件中禁止直接初始化 Redis client。
- 代码级处理:
  - 文件仅保留 SQLAlchemy model 定义与 enum 引用，禁止执行期副作用。
  - 所有 FK 使用字符串表名，避免循环 import。
- pytest 用例（顺序: 正常/边界/异常）:
  - `test_models_import_order_wallet_community_success()`：验证 `from app.models import *` 不抛异常。
  - `test_base_metadata_contains_missing_tables()`：验证 `Base.metadata.tables` 含新表名。
  - `test_app_startup_no_model_import_error()`：`start_app()` 可正常实例化。
- 验收标准:
  - `uvicorn app.app:app` 可启动。
  - `Base.metadata.create_all` 不报 `NoReferencedTableError`。
  - CI 日志不再出现 `ModuleNotFoundError: app.models.order/wallet/community`。

### S1-ST2 用户模型与 schema (复杂度: 中等)
- 目标: 增加 `users` 表映射、请求/响应 schema。
- 文件范围 (3 files):
  - 新建: `app/models/user.py`
  - 新建: `app/schemas/user.py`
  - 修改: `app/models/__init__.py`
- 不要碰:
  - `app/models/nft.py`
  - `app/schemas/nft.py`
- Edge cases:
  - `E46`: `wallet_address` 唯一约束，防止一钱包多账号。
  - `E52`: `referred_by` 一次性写入，重复使用推荐码拒绝。
  - `E60`: `credit_balance` 使用 `DECIMAL(20,6)`。
- 代码级处理:
  - `wallet_address` 与 `email` 分别加 unique index。
  - `referred_by` 更新语句加入 `WHERE referred_by IS NULL`。
  - schema 对 `wallet_address` 做 base58 长度校验。
- pytest 用例（顺序: 正常/边界/异常）:
  - `test_create_user_with_duplicate_wallet_fails()`：mock 两次插入同钱包，期望 `IntegrityError` 转业务错误。
  - `test_referred_by_can_only_be_set_once()`：第二次设置返回拒绝。
  - `test_credit_balance_decimal_precision()`：余额写入 `Decimal('0.123456')` 精度保持。
- 验收标准:
  - MySQL 中 `users.wallet_address` 唯一索引存在。
  - `schemas.UserProfileResp` 可完整序列化 `id/email/twitter_handle/wallet_address/credit_balance`。

### S1-ST3 用户仓储 + OTP/nonce 存储 (复杂度: 复杂)
- 目标: 建立 DB repo + Redis repo，支持钱包 challenge 与邮箱 OTP。
- 文件范围 (3 files):
  - 新建: `app/db/user.py`
  - 新建: `app/db/auth_cache.py`
  - 修改: `app/db/__init__.py`
- 不要碰:
  - `app/db/nft.py`
  - `app/db/cache.py`
- Edge cases:
  - `E48`: OTP 暴力破解锁定 15 分钟。
  - `E61`: DB pool 爆满时快速失败并抛可重试错误。
  - `E62`: Redis 挂掉时 OTP 功能降级到 DB 临时表/错误提示，不允许 silent success。
- 代码级处理:
  - `incr_email_otp_fail(email)` 超过 5 次写 lock key (`otp:lock:{email}`)。
  - `consume_wallet_nonce` 使用 compare-and-delete (Lua/事务) 防重放。
  - repo 层捕获 `OperationalError` 并映射为 `ServerError.SERVER_BUSY`。
- pytest 用例（顺序: 正常/边界/异常）:
  - `test_email_otp_locked_after_five_failures()`：mock Redis 计数后返回 locked。
  - `test_wallet_nonce_can_only_be_consumed_once()`：第二次消费返回 False。
  - `test_repo_operational_error_maps_to_server_busy()`：mock `Session.commit` 抛错后校验错误类型。
- 验收标准:
  - nonce TTL 生效 (默认 300s)。
  - OTP 错误 5 次后第 6 次请求直接拒绝。
  - Redis 不可用时 API 返回明确 503/业务码。

### S1-ST4 Auth Service (复杂度: 复杂)
- 目标: 实现钱包签名登录、邮箱 OTP 登录、Twitter 绑定、JWT 发行与刷新。
- 文件范围 (3 files):
  - 新建: `app/services/auth.py`
  - 新建: `app/schemas/auth.py`
  - 修改: `app/services/__init__.py`
- 不要碰:
  - `app/services/nft.py`
  - `app/plib/web3_ton.py`
- Edge cases:
  - `E47`: 钱包切换后旧 token 失效。
  - `E48`: OTP 防爆破。
  - `E49`: Twitter OAuth code 一次性使用，不落库存 token。
  - `E51`: 禁止自己用自己的推荐码。
  - `E53`: 奖励仅在首单后结算（Sprint4 落地，但 S1 预留状态字段）。
  - `E67`: 支付操作 token 与普通访问 token 分离。
- 代码级处理:
  - `verify_wallet_signature`: `if not sol_wrapper.verify(...): raise UserError.INVALID_SIGNATURE`。
  - JWT payload 包含 `wallet_version`; wallet 变更时 version++，旧 token 拒绝。
  - Twitter 绑定只保存 `username`，不保存 access token。
- pytest 用例（顺序: 正常/边界/异常）:
  - `test_wallet_verify_rejects_invalid_signature()`：mock `SolWrapper.verify=False`。
  - `test_refresh_token_revoked_after_wallet_change()`：wallet_version 不一致返回 401。
  - `test_twitter_bind_stores_handle_only()`：断言 DB 未写 access_token 字段。
- 验收标准:
  - 钱包签名登录返回 `access_token + refresh_token + expires_in`。
  - 邮箱 OTP 登录 10 分钟过期。
  - Twitter 绑定成功后 `GET /users/me` 可见 `twitter_handle`。

### S1-ST5 Auth/User API Router (复杂度: 中等)
- 目标: 提供 `/auth/*` 和 `/users/me*` API。
- 文件范围 (3 files):
  - 新建: `app/api/auth.py`
  - 新建: `app/api/user.py`
  - 修改: `app/app.py`
- 不要碰:
  - `app/api/nft.py`
- Edge cases:
  - `E59`: 统一 UTC 时间字段返回。
  - `E66`: CORS 非 DEV 环境禁止 `*`。
  - `E67`: refresh 与 access token 鉴权逻辑分离。
- 代码级处理:
  - `HTTPBearer` + `get_current_user` dependency 统一鉴权。
  - `response_model` 全量定义，避免字段泄露。
  - `try/except` 仅在边界处做错误映射，service 抛业务错误。
- pytest 用例（顺序: 正常/边界/异常）:
  - `test_wallet_challenge_endpoint_returns_nonce()`。
  - `test_user_profile_requires_bearer_token()`。
  - `test_refresh_endpoint_rejects_access_token_as_refresh()`。
- 验收标准:
  - OpenAPI 出现 `/auth/wallet/challenge` 等新路由。
  - 未携带 token 访问 `/users/me` 返回 401。
  - 非 DEV 环境 CORS origin 白名单生效。

### S1-ST6 前端 AuthContext + 路由保护 (复杂度: 复杂)
- 目标: 用 JWT 用户态替换“钱包=登录态”的逻辑。
- 文件范围 (3 files):
  - 新建: `contexts/AuthContext.tsx`
  - 新建: `components/AuthGate.tsx`
  - 修改: `App.tsx`
- 不要碰:
  - `components/GemCard.tsx`
  - `services/geminiService.ts`
- Edge cases:
  - `E47`: 监听 `accountChanged` 后触发 `logout()`。
  - `E68`: 移动端 Phantom 深链接失败时 fallback 到邮箱 OTP 流。
  - `E67`: 支付时 access token 过期自动 refresh，一次重试。
- 代码级处理:
  - `if (walletAddressChanged) await api.post('/auth/wallet/challenge')` 重新签名登录。
  - axios/fetch interceptor：401 时串行 refresh（单飞锁）。
  - `AuthGate` 未登录统一跳到 `/login`。
- pytest 用例（顺序: 正常/边界/异常）:
  - `test_auth_context_refreshes_token_once_for_parallel_401()`。
  - `test_auth_gate_redirects_when_no_token()`。
  - `test_wallet_change_triggers_logout()`。
- 验收标准:
  - 刷新页面后用户态可恢复（localStorage refresh_token）。
  - Wallet 断开后 UI 立即进入未登录态。
  - Packs/Marketplace/Profile 页面受 `AuthGate` 保护。

### S1-ST7 Navbar 与 profile 联调 (复杂度: 中等)
- 目标: 展示真实用户信息并对接 profile API。
- 文件范围 (3 files):
  - 修改: `components/Navbar.tsx`
  - 修改: `components/Dashboard.tsx`
  - 新建: `services/gemApi.ts`
- 不要碰:
  - `components/PackOpening.tsx`
- Edge cases:
  - `E59`: 时间显示本地化，接口传 UTC。
  - `E65`: 用户昵称/推特名渲染前走 React 安全转义（不使用 `dangerouslySetInnerHTML`）。
- 代码级处理:
  - `gemApi.ts` 统一注入 `Authorization: Bearer`。
  - Navbar 读取 `/users/me` 的 `avatar_seed/wallet_address/credit_balance`。
  - Dashboard 挂载时拉取 profile + vault summary（占位 API）。
- pytest 用例（顺序: 正常/边界/异常）:
  - `test_navbar_shows_truncated_wallet_from_profile()`。
  - `test_dashboard_handles_profile_fetch_500_with_toast()`。
  - `test_api_client_attaches_bearer_header()`。
- 验收标准:
  - Navbar 不再使用 `WalletContext` 的 USD balance 作为唯一身份来源。
  - Dashboard 能显示后端返回的用户余额与 handle。

## 2. 新增函数签名 (完整)

### 2.1 API Endpoint 签名
```python
# app/api/auth.py
@router.post("/auth/wallet/challenge", response_model=schemas.WalletLoginChallengeResp)
def create_wallet_login_challenge(
    req: schemas.WalletLoginChallengeReq,
    request: Request,
    auth_service: AuthServiceDep,
) -> schemas.WalletLoginChallengeResp

@router.post("/auth/wallet/verify", response_model=schemas.AuthTokenResp)
def verify_wallet_login(
    req: schemas.WalletLoginVerifyReq,
    request: Request,
    auth_service: AuthServiceDep,
) -> schemas.AuthTokenResp

@router.post("/auth/email/otp/send", response_model=SuccessResp)
def send_email_otp(
    req: schemas.EmailOtpSendReq,
    auth_service: AuthServiceDep,
) -> SuccessResp

@router.post("/auth/email/otp/verify", response_model=schemas.AuthTokenResp)
def verify_email_otp(
    req: schemas.EmailOtpVerifyReq,
    request: Request,
    auth_service: AuthServiceDep,
) -> schemas.AuthTokenResp

@router.post("/auth/twitter/bind", response_model=schemas.UserProfileResp)
def bind_twitter(
    req: schemas.TwitterBindReq,
    current_user: schemas.UserPrincipal,
    auth_service: AuthServiceDep,
) -> schemas.UserProfileResp

@router.post("/auth/refresh", response_model=schemas.AuthTokenResp)
def refresh_access_token(
    req: schemas.RefreshTokenReq,
    auth_service: AuthServiceDep,
) -> schemas.AuthTokenResp

# app/api/user.py
@router.get("/users/me", response_model=schemas.UserProfileResp)
def get_my_profile(
    current_user: schemas.UserPrincipal,
    user_service: UserServiceDep,
) -> schemas.UserProfileResp

@router.patch("/users/me", response_model=schemas.UserProfileResp)
def update_my_profile(
    req: schemas.UserProfileUpdateReq,
    current_user: schemas.UserPrincipal,
    user_service: UserServiceDep,
) -> schemas.UserProfileResp
```

### 2.2 Service 签名
```python
# app/services/auth.py
class Auth:
    def issue_wallet_challenge(
        self,
        wallet_address: str,
        user_agent: str | None,
        ip_address: str | None,
    ) -> schemas.WalletLoginChallengeResp

    def verify_wallet_signature(
        self,
        wallet_address: str,
        signature: str,
        nonce: str,
        message: str,
        user_agent: str | None,
        ip_address: str | None,
    ) -> schemas.AuthTokenResp

    def send_email_otp(self, email: str) -> None

    def verify_email_otp(
        self,
        email: str,
        otp_code: str,
        wallet_address: str | None,
        user_agent: str | None,
        ip_address: str | None,
    ) -> schemas.AuthTokenResp

    def bind_twitter(self, user_id: str, oauth_code: str, redirect_url: str) -> schemas.UserProfileResp

    def refresh_access_token(self, refresh_token: str) -> schemas.AuthTokenResp

    def parse_token(self, access_token: str) -> schemas.UserPrincipal

class User:
    def get_profile(self, user_id: str) -> schemas.UserProfileResp
    def update_profile(self, user_id: str, payload: schemas.UserProfileUpdateReq) -> schemas.UserProfileResp
```

### 2.3 Repository 签名
```python
# app/db/user.py
class UserRepo:
    def get_user_by_id(self, user_id: str) -> models.User | None
    def get_user_by_wallet(self, wallet_address: str) -> models.User | None
    def get_user_by_email(self, email: str) -> models.User | None
    def create_user(self, payload: schemas.UserCreateReq) -> models.User
    def update_user_profile(self, user_id: str, payload: schemas.UserProfileUpdateReq) -> models.User
    def bind_twitter_handle(self, user_id: str, twitter_handle: str) -> models.User
    def set_referred_by(self, user_id: str, referrer_id: str) -> models.User
    def increment_wallet_version(self, user_id: str) -> None

# app/db/auth_cache.py
class AuthCacheRepo:
    def save_wallet_nonce(self, wallet_address: str, nonce: str, ttl_seconds: int = 300) -> None
    def consume_wallet_nonce(self, wallet_address: str, nonce: str) -> bool
    def save_email_otp_hash(self, email: str, otp_hash: str, ttl_seconds: int = 600) -> None
    def get_email_otp_hash(self, email: str) -> str | None
    def incr_email_otp_fail(self, email: str, lock_threshold: int = 5, lock_seconds: int = 900) -> int
    def is_email_locked(self, email: str) -> bool
    def clear_email_otp(self, email: str) -> None
    def store_refresh_token(self, user_id: str, token_id: str, expires_at: datetime) -> None
    def revoke_refresh_token(self, token_id: str) -> None
    def is_refresh_token_revoked(self, token_id: str) -> bool
```

## 3. 前端改造清单 (React)

### 3.1 需要修改的现有组件
- `App.tsx`
  - 替换 `useWallet()` 登录态依赖为 `useAuth()`。
  - `handleOpenPack()` 从“直接 `sendSolPayment`”改为“先走 `/auth` 与受保护 API”。
  - 新增 `/login` 视图与 `AuthGate` 包裹 `PACKS/MARKETPLACE/PROFILE`。
- `components/Navbar.tsx`
  - `handleWalletClick()` 拆分为“连接钱包”与“发起钱包签名登录”。
  - 展示字段改为后端 `UserProfileResp`。
- `components/Dashboard.tsx`
  - 初始数据从 profile/vault API 拉取，不再只依赖 props 本地 mock。
- `contexts/WalletContext.tsx`
  - 保留钱包连接能力；去除“钱包即登录”语义，仅提供链上能力。

### 3.2 新建前端组件/模块
- `contexts/AuthContext.tsx`
- `components/AuthGate.tsx`
- `services/gemApi.ts` (统一 fetch 包装 + token refresh)

### 3.3 API 调用方式
```http
POST /auth/wallet/challenge
Body: { "wallet_address": "<base58>" }
Resp: { "nonce": "...", "message": "Sign this message...", "expires_at": "2026-02-11T16:00:00Z" }

POST /auth/wallet/verify
Body: {
  "wallet_address": "<base58>",
  "signature": "<base58-signature>",
  "nonce": "<nonce>",
  "message": "Sign this message..."
}
Resp: { "access_token": "...", "refresh_token": "...", "expires_in": 86400 }

POST /auth/email/otp/send
Body: { "email": "user@example.com" }

POST /auth/email/otp/verify
Body: { "email": "user@example.com", "otp_code": "123456", "wallet_address": "<optional>" }

POST /auth/twitter/bind
Body: { "oauth_code": "...", "redirect_url": "https://app.example.com/auth/twitter/callback" }

GET /users/me
Header: Authorization: Bearer <access_token>

PATCH /users/me
Body: { "avatar_seed": "seed_v2", "twitter_handle": "optional_local_override" }
```

## 4. Sprint 1 Edge Case 覆盖矩阵
- 覆盖: `E46 E47 E48 E49 E51 E52 E53 E59 E60 E61 E62 E65 E66 E67 E68`
- 本 Sprint 明确不处理: `E1-E45, E54-E58, E63-E64`（进入后续 Sprint）。

## 5. 交付验收 (Sprint 级)
- 后端:
  - `/auth/*` + `/users/me*` 路由可用，OpenAPI 可见。
  - 钱包签名登录、邮箱 OTP 登录、Twitter 绑定可跑通。
  - `models/__init__.py` 缺失引用问题消失。
- 前端:
  - 未登录状态访问主页面自动跳转登录。
  - 登录后 Navbar 显示后端 profile 信息。
  - token 过期自动 refresh 后业务继续。
- 质量门槛:
  - 新增 pytest 覆盖每个 subtask >= 3 个。
  - 无 `random` 用于认证安全逻辑。
