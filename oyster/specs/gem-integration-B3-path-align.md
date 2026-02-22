# Task B3: 前端 API 路径对齐后端

## 目标
修改前端所有 service 文件中的 API 路径，使其与后端路由完全匹配。
后端已添加 `/api/v1` 前缀（Task A1），gemApi.ts 的 baseURL 已包含 `/api/v1`，所以 service 文件中只需要写相对路径（不含 `/api/v1`）。

## 前提
Task A1 已完成（后端路由带 `/api/v1` 前缀）。

## 文件修改清单

### 1. `lumina/services/walletApi.ts`

| 当前路径 | 改为 | 说明 |
|---------|------|------|
| `/wallet/stripe/checkout` | `/wallet/deposit/stripe/intent` | 后端是 deposit/stripe/intent |
| `/wallet/usdc/deposit` | `/wallet/deposit/usdc/confirm` | 后端是 deposit/usdc/confirm |
| `/wallet/ledger` | `/wallet/history` | 后端是 history |
| `/wallet/withdraw` | `/wallet/withdraw` | 保留（需后端 A3 补齐） |

同时检查请求体字段名是否与后端 schema 匹配。

### 2. `lumina/services/orderApi.ts`

| 当前路径 | 改为 | 说明 |
|---------|------|------|
| `/order/nfts/available` | 删除此方法或改为 `/vault?status=VAULTED` | 后端无此端点，用 vault 列表代替 |
| `/order/create` (POST) | `/orders/redeem` (POST) | 后端是 /orders/redeem |
| `/order/{id}` (GET) | `/orders/{id}` (GET) | 复数 orders |
| `/order/list` (GET) | `/orders` (GET) | 后端是 GET /orders |
| `/order/{id}/track` (GET) | `/orders/{id}` (GET) | 暂用 order detail 代替，tracking 信息在 detail 中 |
| `/order/{id}/cancel` (POST) | 删除或注释 | 后端暂无此端点 |

### 3. `lumina/services/referralApi.ts`

| 当前路径 | 改为 | 说明 |
|---------|------|------|
| `/referral/bind` (POST) | `/referral/use` (POST) | 后端是 /referral/use |
| `/referral/stats` (GET) | `/referral/history` (GET) | 后端无 stats，用 history 代替 |
| `/referral/rewards` (GET) | `/referral/history` (GET) | 同上 |
| `/referral/claim` (POST) | 删除或注释 | 后端暂无此端点 |
| `/referral/code` (GET) | `/referral/code` (GET) | 保持不变 |

### 4. `lumina/services/rankApi.ts`

| 当前路径 | 改为 | 说明 |
|---------|------|------|
| `/rank/${period}` (GET) | `/rank?period=${period}` (GET) | 后端用 query param |
| `/rank/user` (GET) | 删除或注释 | 后端暂无此端点 |

### 5. `lumina/services/marketApi.ts`

| 当前路径 | 改为 | 说明 |
|---------|------|------|
| `/vault/${vaultItemId}/list` (POST) | `/market/vault/${vaultItemId}/list` (POST) | 需加 /market 前缀 |
| `/vault/${vaultItemId}/buyback` (POST) | `/buyback/vault/${vaultItemId}/buyback` (POST) | 需加 /buyback 前缀 |
| `/buyback/${requestId}/cancel` (POST) | `/buyback/requests/${requestId}/cancel` (POST) | 需加 /requests/ |
| `/vault/${vaultItemId}/buyback/quote` (GET) | `/buyback/vault/${vaultItemId}/quote` (GET) | 路径调整 |

### 6. `lumina/services/packApi.ts`
检查 `/packs/{packId}/odds` 路径。如果后端在 pack detail 中包含 odds 数据，改为从 detail 提取。

## 验证
1. TypeScript 编译: `cd lumina && npx tsc --noEmit`
2. 搜索确认无旧路径残留
