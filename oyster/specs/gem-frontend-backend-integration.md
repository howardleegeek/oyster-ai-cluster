# GEM 前后端对接 Spec — 全量修复

> 目标: 让前端 (Lumina) 和后端 (gem-platform/backend) 完全跑通
> 优先级: 登录 > 浏览 > 购买 > 其他

---

## 问题总览

前后端分开开发，API 路径、请求体、响应格式全面不匹配。
前端有两套 API 客户端 (api.ts fetch + gemApi.ts axios)，token 存储也不统一。

---

## 修复策略

**以后端为准，修改前端适配后端。** 理由：
1. 后端已部署运行，56 个端点验证通过
2. 后端 challenge-verify 两步认证更安全
3. 改前端比改后端风险低

---

## Task 1: 统一 API 客户端 (前端)

**问题**: 两套客户端 api.ts (fetch) + gemApi.ts (axios)，token 存储不一致。

**修复**: 删除 api.ts，全部用 gemApi.ts (axios)，统一 token 管理。

文件: `services/api.ts`
- 删除此文件

文件: `services/authService.ts`
- 重写，全部改用 gemApi.ts 的 post/get
- import { post, get } from './gemApi'
- 删除 localStorage 的 auth_token/user_data/user_role (改用 gemApi 的 in-memory token)

文件: `pages/LoginPageNoRouter.tsx`
- 改用 AuthContext 的 loginWithWallet / sendOtp / loginWithEmail 方法
- 不再直接调 authService 的 walletLogin / requestOTP / verifyOTP

---

## Task 2: 修复钱包登录 (最关键)

**问题**: 前端一步登录 POST /auth/wallet，后端两步 challenge + verify

**后端流程**:
1. POST /auth/wallet/challenge  body: {wallet_address}  → {nonce, message, expires_at}
2. 前端用 Phantom 对 message 签名
3. POST /auth/wallet/verify  body: {wallet_address, signature, nonce}  → {access_token, refresh_token, user}

**修复**:

文件: `contexts/AuthContext.tsx` 的 loginWithWallet()
```
改为两步:
1. const challenge = await post('/auth/wallet/challenge', { wallet_address: walletAddress })
2. // 用 Phantom 签名 challenge.message
3. const result = await post('/auth/wallet/verify', {
     wallet_address: walletAddress,
     signature: signature,
     nonce: challenge.nonce
   })
4. setAccessToken(result.access_token)
5. setRefreshToken(result.refresh_token)
6. setUser(result.user)
```

文件: `pages/LoginPageNoRouter.tsx` 的 handleWalletLogin()
```
改为:
1. await connectWallet()
2. // 调 AuthContext 的 loginWithWallet，传 walletAddress
3. // loginWithWallet 内部处理 challenge → sign → verify 两步流
4. setView('PACKS')

签名部分: 不再自己生成 message
- 删掉: const message = `Sign this message to login...`
- 改为: 从 challenge 响应拿 message
- 签名: provider.signMessage(new TextEncoder().encode(challenge.message), 'utf8')
- base64 编码签名: btoa(String.fromCharCode(...signedMessage.signature))
```

---

## Task 3: 修复 Email OTP 登录

**前端调用** → **后端实际端点**:
- `POST /auth/email/send-otp` → `POST /auth/email/otp/send`
- `POST /auth/email/login` → `POST /auth/email/otp/verify`
- `POST /auth/email/otp` → `POST /auth/email/otp/send`
- `POST /auth/email/verify` → `POST /auth/email/otp/verify`

**修复**:

文件: `contexts/AuthContext.tsx`
```
sendOtp(): POST /auth/email/send-otp → 改为 POST /auth/email/otp/send
  body: { email } (不变)

loginWithEmail(): POST /auth/email/login → 改为 POST /auth/email/otp/verify
  body: { email, otp_code } → 改为 { email, otp }
  响应: { access_token, refresh_token, user }
```

文件: `services/authService.ts` (如果还保留)
```
requestOTP(): POST /auth/email/otp → 改为 POST /auth/email/otp/send
verifyOTP(): POST /auth/email/verify → 改为 POST /auth/email/otp/verify
  body: { email, otp } (不变)
```

---

## Task 4: 修复 User API

**前端**: GET /user/me
**后端**: GET /users/me (注意是 users 复数)

文件: `services/authService.ts`
```
getProfile(): GET /user/me → 改为 GET /users/me
```

也检查 Dashboard.tsx 是否直接调 /user/ 路径。

---

## Task 5: 修复 Leaderboard API

**前端**: GET /api/rank/leaderboard?period={period}
**后端**: GET /rank (无 /api 前缀，无 /leaderboard 子路径)

文件: `pages/LeaderboardPage.tsx`
```
GET /api/rank/leaderboard?period={period} → 改为 GET /rank?period={period}
```

检查后端 rank.py 是否支持 period 参数，如果不支持需要加。

---

## Task 6: 修复 Referral API

**前端**: GET /api/referral/stats 和 GET /api/referral/list
**后端**: GET /referral/code 和 GET /referral/history

文件: `pages/ReferralPage.tsx`
```
GET /api/referral/stats → 改为 GET /referral/code
  响应映射: { referralCode → code, totalReferrals, totalRewards, activeReferrals }

GET /api/referral/list → 改为 GET /referral/history
  响应映射: { referrals → history items }
```

---

## Task 7: Pack 购买流程对接

**前端当前流程** (App.tsx):
1. 直接调 Phantom sendSolPayment() 转 SOL 到硬编码地址
2. 没有调后端 API

**后端流程** (pack.py):
1. GET /packs → 获取盲盒列表
2. GET /packs/{pack_id} → 获取详情+价格
3. POST /packs/{pack_id}/purchase → 创建购买订单 (返回 opening_id + payment_info)
4. POST /packs/openings/{opening_id}/confirm-payment → 确认支付 (传 tx_hash)

**修复**: 前端购买流程需要大改

文件: `App.tsx` 的 handlePurchasePack()
```
改为:
1. const opening = await post('/packs/{packId}/purchase', { quantity })
2. // 用返回的 payment_info 构造 SOL 交易
3. const txHash = await sendSolPayment(walletAddress, opening.payment_info.amount_sol)
4. await post(`/packs/openings/${opening.id}/confirm-payment`, { tx_hash: txHash })
5. // 更新 UI 显示开盒结果
```

---

## Task 8: Marketplace 对接

**前端当前**: 纯前端 mock 数据
**后端端点**:
- GET /market/listings → 获取市场挂单列表
- POST /market/vault/{vault_item_id}/list → 挂单
- POST /market/listings/{listing_id}/buy → 购买
- POST /market/listings/{listing_id}/delist → 下架
- POST /market/listings/{listing_id}/offers → 出价
- PUT /market/offers/{offer_id} → 更新出价
- GET /market/offers/mine → 我的出价

文件: `components/Marketplace.tsx`
```
需要对接后端 API 替换 mock 数据
```

---

## Task 9: Vault / Inventory 对接

**后端端点**:
- GET /vault → 获取用户保险箱 (NFT 列表)
- GET /vault/{vault_item_id} → 获取单个 NFT 详情

前端 inventory 数据当前可能是 mock，需要对接。

---

## Task 10: Buyback 对接

**后端端点**:
- GET /buyback/vault/{vault_item_id}/quote → 获取回购报价 (85% FMV)
- POST /buyback/vault/{vault_item_id}/buyback → 发起回购
- GET /buyback/requests → 我的回购请求
- POST /buyback/requests/{request_id}/cancel → 取消回购

---

## Task 11: Wallet/Balance 对接

**后端端点**:
- GET /wallet/balance → 获取平台余额
- GET /wallet/history → 交易历史
- POST /wallet/deposit/stripe/intent → Stripe 充值
- POST /wallet/deposit/usdc/confirm → USDC 充值确认

---

## 执行分配

### Node-1 (codex-node-1): Auth + Core (最紧急)
修改前端代码:
- Task 1: 统一 API 客户端 (删 api.ts，全用 gemApi.ts)
- Task 2: 钱包登录两步流 (challenge → sign → verify)
- Task 3: Email OTP 路径修复
- Task 4: User API 路径修复
- Task 7: Pack 购买流程对接后端

### Node-2 (glm-node-2): Pages + Features
修改前端代码:
- Task 5: Leaderboard 对接
- Task 6: Referral 对接
- Task 8: Marketplace 对接后端 API
- Task 9: Vault/Inventory 对接
- Task 10: Buyback 对接
- Task 11: Wallet 对接

---

## 验收标准

1. **钱包登录**: 点击 Connect Wallet → Phantom 弹窗 → 签名 → 登录成功 → 跳转主页
2. **Email 登录**: 输入邮箱 → 收到 OTP → 输入 → 登录成功
3. **浏览 Packs**: 主页显示盲盒列表 (从后端拉数据)
4. **购买 Pack**: 选择盲盒 → 支付 SOL → 后端确认 → 显示开盒结果
5. **Marketplace**: 能看到市场挂单列表
6. **Leaderboard**: 能看到排行榜
7. **Referral**: 能看到推荐码和历史
8. **Profile**: 能看到用户信息
9. **所有页面不报 CORS / 401 / 404 错误**
