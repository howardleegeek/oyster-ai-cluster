# GEM 全面推进 — 20 Session 并行 Execution Spec

> 发现: 后端 66 个端点 S1-S5 全部已实现。瓶颈 = bug + 前端对接 + 测试。
> 执行层: MiniMax M2.5 × 4 节点 (Mac-1, Mac-2, codex-node-1, glm-node-2)

---

## 现状: 66 端点已就绪

### Auth (8 endpoints) ✅
- wallet challenge/verify, email OTP send/verify, token refresh, twitter bind/callback, user profile

### Pack Engine (5 endpoints) ✅ S2 已修复
- list packs, get pack, get odds, purchase, confirm-payment

### Vault (2 endpoints) ✅
- list vault, get vault item

### Marketplace (5 endpoints) ✅ 需验证
- list listings, create listing, delist, buy now, make offer

### Buyback (4 endpoints) ✅ 需验证
- get quote, submit request, cancel request, list requests

### Wallet (5 endpoints) ✅ 需验证
- get balance, history, stripe deposit, USDC confirm, withdraw

### Orders (4 endpoints) ✅ 需验证
- list orders, get order, redeem, update address

### Referral (3 endpoints) ✅ 需验证
- get code, use code, history

### Rank (1 endpoint) ✅ 需验证
- leaderboard

### Admin (11 endpoints) ✅ 需验证
- NFT CRUD + batch import, Pack CRUD + drop table, User disable, Order status, Buyback approve/reject

### Notifications (3 endpoints) ✅ 需验证
- Telegram webhook/verify/test

### Webhooks (1 endpoint) ✅ 需验证
- Stripe webhook

---

## 20 Session 分配计划

### Group A: 拜占庭验证 (8 sessions) — 找出所有 remaining bugs

| Session | 节点 | 任务 | 验证范围 |
|---------|------|------|---------|
| A1 | Mac-1 minimax | Market service + repo 深度审计 | market.py, db/market.py |
| A2 | Mac-1 minimax | Buyback service 深度审计 | buyback.py, db/buyback.py |
| A3 | Mac-2 minimax | Wallet + Payment 深度审计 | wallet_payment.py, web3_sol.py |
| A4 | Mac-2 minimax | Order + Referral 审计 | order.py, referral.py |
| A5 | codex-node-1 | Admin services 审计 | admin_*.py |
| A6 | codex-node-1 | Auth + Security 审计 | auth.py, security.py |
| A7 | glm-node-2 | Schema 一致性全面检查 | 前后端类型匹配 |
| A8 | glm-node-2 | API 路由 + 中间件审计 | 所有 api/*.py |

### Group B: 前端对接 (8 sessions) — mock → API

| Session | 节点 | 任务 | 组件 |
|---------|------|------|------|
| B1 | Mac-2 minimax | Marketplace 列表页接 API | Marketplace.tsx + marketApi.ts |
| B2 | Mac-2 minimax | Make Offer UI 接 API | OfferModal + offerApi.ts |
| B3 | codex-node-1 | Buy Now 流程接 API | BuyModal + 支付确认 |
| B4 | codex-node-1 | Buyback 功能接 API | Dashboard buyback 按钮 |
| B5 | glm-node-2 | Wallet 余额 + 充值页 | WalletPanel + walletApi.ts |
| B6 | glm-node-2 | 订单历史 + 兑换流程 | Orders page + orderApi.ts |
| B7 | Mac-1 minimax | 排行榜页面接 API | Leaderboard + rankApi.ts |
| B8 | Mac-1 minimax | 推荐系统 UI 接 API | Referral + referralApi.ts |

### Group C: 测试补全 (4 sessions) — pytest 覆盖

| Session | 节点 | 任务 |
|---------|------|------|
| C1 | Mac-2 minimax | market + buyback tests |
| C2 | codex-node-1 | wallet + order tests |
| C3 | glm-node-2 | auth + admin tests |
| C4 | Mac-1 minimax | referral + rank + notification tests |

---

## Dispatch 命令模板

```bash
# MiniMax 执行 (推荐)
~/.local/bin/minimax-code "任务 spec"

# 远程节点
ssh howard-mac2 'cd ~/gem-platform && ~/.local/bin/minimax-code "任务"'
gcloud compute ssh codex-node-1 --zone=us-west1-b --command='cd ~/gem-platform && ~/.local/bin/minimax-code "任务"'
gcloud compute ssh glm-node-2 --zone=us-west1-b --command='cd ~/gem-platform && ~/.local/bin/minimax-code "任务"'
```

## 约束 (全局)
1. **不动已验证的代码**: pack_engine.py, payment.py 已通过拜占庭，不改
2. **前端铁律**: 不动 CSS/Tailwind 样式，只改数据源
3. **每个 session 完成后**: 输出 verification_report.txt
4. **错误处理**: try/except + 用户友好错误消息
5. **类型安全**: 前端 TypeScript strict，后端 Pydantic validation
