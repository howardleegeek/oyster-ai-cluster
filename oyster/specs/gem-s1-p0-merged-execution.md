# GEM Sprint 1 + P0 Security — Merged Execution Spec

> **目标**: 一次性完成用户系统 + 6 个 P0 安全修复。交付物: 可运行的完整认证链路 + 安全加固。
> **Codebase**: `/Users/howardli/Downloads/gem-platform/`
> **Backend**: `backend/app/` (FastAPI + MySQL + Redis)
> **Frontend**: `/Users/howardli/Downloads/lumina-source-code/`
> **部署**: GCP codex-node-1 (35.203.150.12:8000)

---

## 批次 A: 后端核心 (串行, 4 个 GLM 任务)

### A1. 安全加固 + Config 修复 (P0-SEC)
**优先级**: BLOCKING — 所有其他任务依赖此完成
**文件**:
- 修改: `backend/app/config.py`
- 修改: `backend/app/services/auth.py`
- 修改: `backend/app/services/security.py`
- 修改: `backend/app/services/admin_auth.py`
- 修改: `backend/app/app.py`

**具体要求**:

1. **P0-1: JWT Secret 加强**
   - `config.py:18` 现在是 `secret: str = "change-me-in-production"`
   - 改为: 启动时如果 `env != "DEV"` 且 `secret == "change-me-in-production"`，抛 `RuntimeError("JWT secret must be set in production")`
   - 增加 `jwt_algorithm: str = "HS256"` 到 Settings (已用 HS256，显式声明)
   - 删除 `config.py:36-37` 的 `print("#########settings", Settings())` 调试语句

2. **P0-2: Admin API 认证**
   - `backend/app/api/admin.py` 所有端点必须检查 `current_user.role == "admin"`
   - 在 `services/admin_auth.py` 实现 `require_admin` FastAPI dependency
   - 如果 `admin_auth.py` 已有骨架，补全实现；否则新建
   - Admin 用户标识: `users.role` 字段 (如缺失需加到 User model)

3. **P0-3: Wallet 签名验证**
   - 检查 `services/auth.py` 中 `verify_wallet_signature` 方法
   - 如果是 TODO/placeholder，实现真实的 Solana Ed25519 签名验证:
     ```python
     from nacl.signing import VerifyKey
     from nacl.exceptions import BadSignatureError
     import base58

     verify_key = VerifyKey(base58.b58decode(wallet_address))
     try:
         verify_key.verify(message.encode(), base58.b58decode(signature))
     except BadSignatureError:
         raise UserError.INVALID_SIGNATURE
     ```
   - 依赖: `PyNaCl`, `base58` (检查 requirements.txt)

4. **P0-4: CORS 生产白名单**
   - `app.py` 中 CORS 当 `env != "DEV"` 时:
     ```python
     allow_origins=[settings.frontend_url]  # 不再是 ["*"]
     ```

5. **P0-5: Rate Limiting 启用**
   - 检查现有 rate limiting 代码是否被注释/禁用
   - 启用或实现基于 Redis 的 rate limiting middleware
   - 关键端点限制: `/auth/*` = 20 req/min, `/packs/open` = 5 req/min, 全局 = 100 req/min

6. **P0-6: 错误信息不泄露内部细节**
   - 全局异常处理器: 非 DEV 环境下 500 错误只返回 `{"detail": "Internal server error"}`
   - 不暴露 traceback、SQL 错误、文件路径

**验收**:
- `ENV=PROD` 启动时无 JWT default secret → 报错退出
- Admin 端点无 token → 401, 非 admin token → 403
- 伪造签名 → 拒绝
- CORS 非白名单 origin → 被拒
- 暴力请求 → 429 Too Many Requests

---

### A2. User Model + Schema + Repo 完善 (S1-ST1/ST2/ST3 合并)
**依赖**: A1 完成
**文件**:
- 修改: `backend/app/models/user.py` — 增加 `role`, `pity_counter_legendary`, `is_active`, `last_login_at` 字段
- 修改: `backend/app/schemas/` — 确保 `user.py` 有完整的 request/response schemas
- 修改: `backend/app/db/user.py` — UserRepo 完整 CRUD
- 修改: `backend/app/db/auth_cache.py` — OTP + nonce Redis 操作

**User Model 增补字段**:
```python
role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)  # user/admin
pity_counter_legendary: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
last_login_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)
```

**UserRepo 必须实现** (检查 db/user.py 已有的，补全缺失):
- `get_user_by_id(user_id) -> User | None`
- `get_user_by_wallet(wallet_address) -> User | None`
- `get_user_by_email(email) -> User | None`
- `create_user(payload) -> User`
- `update_user_profile(user_id, payload) -> User`
- `bind_twitter_handle(user_id, handle) -> User`
- `set_referred_by(user_id, referrer_id) -> User` (WHERE referred_by IS NULL)
- `increment_wallet_version(user_id) -> None`

**AuthCacheRepo 必须实现** (检查 db/auth_cache.py 已有的，补全缺失):
- `save_wallet_nonce(wallet, nonce, ttl=300)`
- `consume_wallet_nonce(wallet, nonce) -> bool` (原子 get+delete)
- `save_email_otp_hash(email, hash, ttl=600)`
- `get_email_otp_hash(email) -> str | None`
- `incr_email_otp_fail(email, threshold=5, lock_sec=900) -> int`
- `is_email_locked(email) -> bool`
- `clear_email_otp(email)`
- `store_refresh_token(user_id, token_id, expires_at)`
- `revoke_refresh_token(token_id)`
- `is_refresh_token_revoked(token_id) -> bool`

**Schemas 必须有**:
- `WalletLoginChallengeReq(wallet_address: str)`
- `WalletLoginChallengeResp(nonce, message, expires_at)`
- `WalletLoginVerifyReq(wallet_address, signature, nonce, message)`
- `AuthTokenResp(access_token, refresh_token, expires_in, token_type="bearer")`
- `EmailOtpSendReq(email)`
- `EmailOtpVerifyReq(email, otp_code, wallet_address?)`
- `TwitterBindReq(oauth_code, redirect_url)`
- `RefreshTokenReq(refresh_token)`
- `UserProfileResp(id, email, wallet_address, twitter_handle, avatar_seed, credit_balance, role, created_at)`
- `UserProfileUpdateReq(avatar_seed?, twitter_handle?)`
- `UserPrincipal(user_id, email, wallet_version, role)` — JWT 解析结果

**Edge Cases**:
- `credit_balance` 使用 `DECIMAL(20,6)`, schema 序列化为 string 避免 JS 精度丢失
- `wallet_address` unique + base58 格式校验 (32-44 chars)
- `referred_by` 只能设一次 (WHERE IS NULL)
- OTP 暴力破解: 5 次失败 → 锁 15 分钟

**验收**:
- User model 有 role, pity_counter, is_active 字段
- UserRepo 所有方法可调用
- AuthCacheRepo nonce consume 原子性 (第二次返回 False)
- OTP 锁定逻辑生效

---

### A3. Auth Service 业务逻辑 (S1-ST4)
**依赖**: A2 完成
**文件**:
- 修改: `backend/app/services/auth.py`

**检查现有实现，补全以下方法** (AuthService class):

1. `issue_wallet_challenge(wallet_address, user_agent, ip) -> ChallengeResp`
   - 生成 `secrets.token_urlsafe(32)` nonce
   - 构造签名消息: `"Sign to log in to GEM Platform\nNonce: {nonce}\nWallet: {wallet_address}"`
   - Redis 存储 nonce, TTL 300s
   - 返回 nonce + message + expires_at

2. `verify_wallet_signature(wallet_address, signature, nonce, message, ...) -> AuthTokenResp`
   - consume_wallet_nonce (原子，防重放)
   - Ed25519 签名验证 (nacl)
   - 查找或创建 User (get_by_wallet, 没有则 create)
   - 更新 last_login_at
   - issue_tokens (access + refresh)

3. `send_email_otp(email) -> None`
   - 检查 is_email_locked → 抛错
   - 生成 6 位 OTP
   - SHA-256 hash 存 Redis, TTL 600s
   - 通过 SendGrid 发邮件

4. `verify_email_otp(email, otp_code, wallet_address?, ...) -> AuthTokenResp`
   - 检查 locked
   - 获取 stored hash, 比对 `secrets.compare_digest`
   - 失败 → incr_fail_count
   - 成功 → clear_otp, 查找/创建 User, issue_tokens

5. `bind_twitter(user_id, oauth_code, redirect_url) -> UserProfileResp`
   - 用 `twitter_oauth(code, redirect_url)` 换取用户名
   - 只存 `twitter_handle`, 不存 access_token
   - 返回更新后的 profile

6. `refresh_access_token(refresh_token) -> AuthTokenResp`
   - 解码 refresh token
   - 检查 is_revoked
   - 验证 wallet_version 匹配
   - 颁发新 access + refresh, 撤销旧 refresh

7. `parse_token(access_token) -> UserPrincipal`
   - JWT decode + 验证 expiry
   - 查 user wallet_version 匹配
   - 返回 UserPrincipal(user_id, email, wallet_version, role)

**`get_current_user` dependency** (用于 API router):
```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserPrincipal:
    return auth_service.parse_token(credentials.credentials)
```

**验收**:
- 钱包签名登录完整链路 (challenge → sign → verify → token)
- 邮箱 OTP 登录链路 (send → verify → token)
- Token refresh 链路
- 重放攻击防护 (nonce 消耗一次性)

---

### A4. Auth + User API Router (S1-ST5)
**依赖**: A3 完成
**文件**:
- 修改: `backend/app/api/auth.py` — 检查并补全端点
- 修改: `backend/app/api/user.py` — 检查并补全 /users/me
- 修改: `backend/app/app.py` — 确保 router 注册

**API 端点清单** (检查已有，补全缺失):
```
POST /auth/wallet/challenge     → issue_wallet_challenge
POST /auth/wallet/verify        → verify_wallet_signature
POST /auth/email/otp/send       → send_email_otp
POST /auth/email/otp/verify     → verify_email_otp
POST /auth/twitter/bind         → bind_twitter (需 Bearer token)
POST /auth/refresh              → refresh_access_token

GET  /users/me                  → get_profile (需 Bearer token)
PATCH /users/me                 → update_profile (需 Bearer token)
```

**要求**:
- 所有受保护端点用 `Depends(get_current_user)`
- `response_model` 必须定义，防字段泄露
- 统一错误映射: `UserError → 4xx`, `ServerError → 5xx`
- Access token 用于业务, Refresh token 只能用于 /auth/refresh

**验收**:
- `GET /docs` (OpenAPI) 可见所有新路由
- 无 token 访问 /users/me → 401
- 非法 token → 401
- 所有端点正确映射到 service 方法

---

## 批次 B: 前端 (并行, 2 个 GLM 任务)

### B1. AuthContext + AuthGate + Login Page (S1-ST6)
**依赖**: 可与 A3/A4 并行开发 (mock API)
**工作目录**: `/Users/howardli/Downloads/lumina-source-code/`
**文件**:
- 新建: `src/contexts/AuthContext.tsx`
- 新建: `src/components/AuthGate.tsx`
- 新建: `src/pages/LoginPage.tsx`
- 新建: `src/services/gemApi.ts`
- 修改: `src/App.tsx`

**AuthContext**:
- State: `user`, `accessToken`, `refreshToken`, `isAuthenticated`, `isLoading`
- Methods: `loginWithWallet()`, `loginWithEmail()`, `logout()`, `refreshSession()`
- Token 存储: `localStorage` (refresh_token), memory (access_token)
- Wallet change 监听: Phantom `accountChanged` → auto logout

**gemApi.ts**:
- axios/fetch wrapper
- 自动注入 `Authorization: Bearer`
- 401 interceptor → 单飞 refresh → 重试原请求 → 失败则 logout
- Base URL: 环境变量 `VITE_API_URL` (default: `http://35.203.150.12:8000`)

**AuthGate**:
- 包裹需要登录的路由
- 未登录 → redirect to `/login`
- 加载中 → spinner

**LoginPage**:
- 两种登录方式: Wallet Sign-in (主) + Email OTP (备)
- Wallet: Connect → Challenge → Sign → Verify → redirect to /packs
- Email: Input → Send OTP → Input Code → Verify → redirect

**App.tsx 改造**:
- 包裹 `<AuthProvider>`
- `/login` 公开路由
- `/packs`, `/marketplace`, `/vault`, `/profile` 包裹 `<AuthGate>`

**验收**:
- 未登录访问 /packs → 跳转 /login
- Wallet 签名登录后跳回 /packs
- 刷新页面保持登录态
- Wallet 断开 → 自动 logout

---

### B2. Navbar + Dashboard 联调 (S1-ST7)
**依赖**: B1 完成
**文件**:
- 修改: `src/components/Navbar.tsx`
- 修改: `src/components/Dashboard.tsx`

**Navbar**:
- 登录后显示: 截断钱包地址 + credit_balance + avatar
- 未登录显示: "Connect & Sign In" 按钮
- 数据来源: `useAuth()` context → `/users/me` API

**Dashboard**:
- 挂载时调 `/users/me` 获取 profile
- 显示: email, twitter_handle, wallet, balance, 加入时间
- API 错误 → toast 提示

**验收**:
- Navbar 显示后端返回的真实数据
- Dashboard 不依赖本地 mock

---

## 批次 C: 安全补充 (可与 B 并行)

### C1. USDC 交易验证 + Stripe Webhook 加固 (P0-SEC-EXT)
**文件**:
- 修改: `backend/app/services/wallet_payment.py`
- 修改: `backend/app/services/stripe_webhook.py`
- 修改: `backend/app/api/webhooks.py`

**USDC 验证**:
- 当用户提交 `tx_hash` 声称完成 USDC 支付时:
  - 调 Solana RPC `getTransaction(tx_hash)` 验证交易存在
  - 检查: 收款地址 == 平台钱包, 金额 >= 应付金额, token == USDC mint
  - 如果是 devnet 且 `env == "DEV"`, 可以跳过验证但打 WARNING log

**Stripe Webhook 加固**:
- 检查 `stripe.Webhook.construct_event` 是否正确实现
- 添加幂等性检查: 记录 `event.id`, 重复事件 → 200 OK 但不重复处理
- 添加 timestamp 检查: 事件超 300s → 拒绝 (防重放)

**验收**:
- 假 tx_hash → 拒绝
- 重复 Stripe event → 幂等处理
- 过期 event → 拒绝

---

## Dispatch 计划

### 阶段 1: 并行启动 (3 个 GLM 节点同时)

| 任务 | 节点 | 预估 |
|------|------|------|
| A1 (安全加固) | GCP codex-node-1 | 20-30min |
| C1 (USDC+Stripe) | GCP glm-node-2 | 20-30min |
| B1 (前端 Auth) | GCP codex-node-1 (第2个session) | 25-35min |

### 阶段 2: A1 完成后 (串行后端)

| 任务 | 节点 | 预估 |
|------|------|------|
| A2 (Model+Repo) | GCP codex-node-1 | 20-30min |

### 阶段 3: A2 完成后

| 任务 | 节点 | 预估 |
|------|------|------|
| A3 (Auth Service) | GCP codex-node-1 | 25-35min |
| B2 (Navbar+Dashboard) | GCP glm-node-2 | 15-20min |

### 阶段 4: A3 完成后

| 任务 | 节点 | 预估 |
|------|------|------|
| A4 (API Router) | GCP codex-node-1 | 15-25min |

### 阶段 5: 验收
- 后端: `uvicorn` 启动 + `/health` + `/docs` 检查
- 前端: `npm run dev` + 登录流程手测
- 安全: 验证 CORS/JWT/Rate-limit/签名

---

## 不要碰的文件
- `backend/app/api/nft.py`, `backend/app/db/nft.py`, `backend/app/models/nft.py` — 现有 NFT 功能
- `backend/app/services/pack_engine.py` — Sprint 2 再改
- `lumina-source-code/src/components/PackOpening.tsx` — Sprint 2
- `lumina-source-code/src/components/GemCard.tsx` — 不动

## 测试要求
每个任务完成后至少 3 个 pytest:
- A1: `test_jwt_secret_enforcement`, `test_admin_auth_required`, `test_rate_limit_429`
- A2: `test_user_create_duplicate_wallet_fails`, `test_otp_lock_after_5_failures`, `test_nonce_consumed_once`
- A3: `test_wallet_login_full_flow`, `test_email_otp_full_flow`, `test_refresh_revokes_old_token`
- A4: `test_protected_endpoint_401`, `test_wallet_challenge_returns_nonce`, `test_refresh_rejects_access_token`
- C1: `test_fake_tx_hash_rejected`, `test_duplicate_stripe_event_idempotent`
