# GEM 前端全面审计 + 修复 Spec

> 目标: 找出并修复前端所有类似的 API 调用问题，确保每个功能都能正常工作

## 审计维度

### 1. API 客户端一致性
- 确认所有文件都 import from 'gemApi' 而不是旧的 'api'
- 确认没有硬编码的 http://35.203.150.12:8000 或 http://localhost:8000
- 确认所有 fetch() 直接调用都改成了 gemApi 的方法
- 确认没有残留的 api.ts import

### 2. HTTP 方法正确性
- GET 端点不能用 post() 调用
- POST 端点不能用 get() 调用
- 检查每个 API 调用的 HTTP 方法是否与后端端点匹配

### 3. API 路径匹配
检查每个前端 API 调用路径是否与后端完全匹配:

后端端点清单 (prefix + path):
- Auth: /auth/wallet/challenge, /auth/wallet/verify, /auth/email/otp/send, /auth/email/otp/verify, /auth/twitter/bind, /auth/twitter/callback, /auth/refresh
- User: /users/me (GET, PATCH)
- Packs: /packs (GET), /packs/{id} (GET), /packs/{id}/odds (GET), /packs/{id}/purchase (POST), /packs/openings/{id}/confirm-payment (POST)
- Vault: /vault (GET), /vault/{id} (GET)
- Market: /market/listings (GET), /market/vault/{id}/list (POST), /market/listings/{id}/delist (POST), /market/listings/{id}/buy (POST), /market/listings/{id}/offers (POST), /market/offers/{id} (PUT), /market/offers/mine (GET)
- Buyback: /buyback/vault/{id}/buyback (POST), /buyback/requests/{id}/cancel (POST), /buyback/requests (GET), /buyback/vault/{id}/quote (GET)
- Wallet: /wallet/balance (GET), /wallet/history (GET), /wallet/deposit/stripe/intent (POST), /wallet/deposit/usdc/confirm (POST)
- Referral: /referral/code (GET), /referral/use (POST), /referral/history (GET)
- Rank: /rank (GET)
- Orders: /orders/redeem (POST), /orders (GET), /orders/{id} (GET), /orders/{id}/address (PUT)
- Admin: /admin/* (多个端点)
- Webhooks: /webhooks/stripe (POST)
- Notifications: /notifications/telegram/* (POST)

### 4. 请求体/响应体匹配
- 确认前端发送的 request body 字段名与后端 Pydantic schema 匹配
- 确认前端解析 response 的字段名正确

### 5. Token 管理
- 确认所有需要认证的请求都有 Authorization header
- 确认 token refresh 逻辑正确
- 确认 401 处理一致

### 6. 错误处理
- 确认 API 失败时有 fallback 或错误提示
- 确认不会白屏

### 7. Build 验证
- 用 `npx vite build` 确认无编译错误
- 用 `npx tsc --noEmit` 检查类型错误 (记录但不需要全部修复)

## 产出
1. 写审计报告到 ~/audit-report.txt: 列出每个问题 + 修复方案
2. 直接修复所有发现的问题
3. 修复后 `npx vite build` 确认能 build
4. 写修复清单到 ~/fix-summary.txt
