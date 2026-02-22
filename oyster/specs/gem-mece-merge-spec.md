# GEM Backend MECE 合并规范

> **原则**: MECE (Mutually Exclusive, Collectively Exhaustive)
> - **ME (互斥)**: 每个功能模块只从一个代码库取，不混搭同一层逻辑
> - **CE (穷尽)**: 两个代码库的所有功能都被覆盖，零遗漏

**日期**: 2026-02-11
**基础**: gem-platform/backend (B) — 以此为主干
**移植源**: gema-backend-main (A) — 选择性取模块

---

## MECE 模块划分

### 总览矩阵

| # | 模块 | 来源 | 理由 | 状态 |
|---|------|------|------|------|
| M1 | **认证 (Auth)** | ✅ B | B 有 Wallet + Email OTP + JWT Refresh + Twitter Bind + Rate Limit | B 完整 |
| M2 | **用户 (User)** | ✅ B | B 有 Profile CRUD + Role + Admin 管理 | B 完整 |
| M3 | **盲盒引擎 (Pack)** | ✅ B | B 有保底 (pity)、扁平概率表、Pack 分级 | B 完整 |
| M4 | **抽卡算法 (Lottery Core)** | 🔀 A→B | A 有树形策略引擎 (unpack_strategies)，B 只有扁平 | 需移植 |
| M5 | **NFT 管理** | ✅ B | B 有预铸造 + Vault + 元数据 | B 完整 |
| M6 | **Marketplace** | ✅ B | A 没有 Marketplace | B 独有 |
| M7 | **回购 (Buyback)** | ✅ B | A 没有 Buyback | B 独有 |
| M8 | **钱包/支付 (Wallet)** | ✅ B | B 有 SOL + USDC + Stripe + Ledger | B 完整 |
| M9 | **排行榜 (Leaderboard)** | ✅ B | A 没有 | B 独有 |
| M10 | **推荐 (Referral)** | ✅ B（补强） | B 有完整推荐链，A 有基础 referral 表 | B 为主 |
| M11 | **物流 (Shipping)** | 🔀 B+A | B 有兑换流程，A 有 shipping_address 独立表 | 合并 |
| M12 | **Admin** | ✅ B | A 没有 Admin | B 独有 |
| M13 | **Telegram 集成** | 🔀 A→B | A 有 ext_service/tg.py，B 没有 | 需移植 |
| M14 | **Twitter OAuth 完整流程** | 🔀 A→B | A 有完整 OAuth callback，B 只有绑定 | 需移植 |
| M15 | **货币系统 (Currency)** | ✅ B | B 有 GEM Coin + 充值 + 兑换 | B 独有 |
| M16 | **错误处理 (Error)** | ✅ B | B 有分层 Error Code + global handler | B 完整 |
| M17 | **数据库层 (DB/Repository)** | ✅ B | B 用 Repository 模式，A 用简单 DAO | B 更规范 |
| M18 | **工具库 (plib)** | ✅ B（含 A） | B 已复制 A 的 plib，保持 B 版本 | 已合并 |
| M19 | **配置 (Config)** | ✅ B（扩展） | B 为基础 + 加入 A 独有的 config 项 | 需扩展 |
| M20 | **测试 (Test)** | 🔀 A→B | A 有 test_lottery，B 无测试。以 A 为种子扩展 | 需移植+扩展 |

---

## ME 检验：互斥性验证

| 冲突风险模块 | A 的实现 | B 的实现 | 决策 | 冲突处理 |
|-------------|---------|---------|------|---------|
| **用户表 (users)** | sol_address, twitter_id, twitter_name | wallet_address, twitter_handle, email, role | **用 B** | B 字段更全，A 的字段可映射 |
| **NFT 表** | nfts (简单) | nft + user_vault (双表) | **用 B** | B 支持 Vault 托管分离 |
| **订单表** | orders (统一) | pack_opening + marketplace_listing + buyback_request (分表) | **用 B** | B 按业务类型拆表，更 MECE |
| **抽卡逻辑** | lottery.py (树形) | pack_engine.py (扁平) | **共存** | B 为默认，A 的树形作为高级策略插件 |
| **错误码** | error.py (UserError only) | error.py (UserError + ServerError + .http()) | **用 B** | B 更完整 |
| **Solana 签名验证** | 手写 Ed25519 verify | 手写 Ed25519 verify | **用 B** | 逻辑相同，B 集成度更高 |
| **Redis 用法** | session 存储 | OTP + Rate Limit + Session | **用 B** | B 用途更广 |

**结论**: 无模块需要从两个源混合同一层逻辑。每个模块有且仅有一个权威来源。✅ ME 通过。

---

## CE 检验：穷尽性验证

### A 独有功能（必须移植，否则遗漏）

| A 独有 | 文件 | 移植目标 | 优先级 |
|--------|------|---------|--------|
| 树形抽卡策略引擎 | `services/lottery.py` (unpack_strategies) | `services/pack_engine.py` 新增插件接口 | P1 |
| Telegram 通知 | `ext_service/tg.py` | `services/notification.py` 新建 | P2 |
| Twitter OAuth 完整回调 | `services/oauth.py` | `services/auth.py` 扩展 | P1 |
| Alchemy NFT API | config `alchemy_api_key` | `services/nft.py` 扩展 | P3 |
| 单元测试种子 | `test/test_lottery_service.py` | `tests/` 新建目录 | P1 |

### B 独有功能（已在主干，确认无遗漏）

| B 独有 | 确认 |
|--------|------|
| Email OTP 认证 | ✅ |
| JWT Refresh Token | ✅ |
| Rate Limiting (slowapi) | ✅ |
| Marketplace (挂单/交易) | ✅ |
| Buyback (回购/审批) | ✅ |
| GEM Coin 货币系统 | ✅ |
| Wallet 充值 (SOL/USDC/Stripe) | ✅ |
| Leaderboard 排行榜 | ✅ |
| Admin 后台 | ✅ |
| 审计日志 | ✅ |
| 全局异常处理 | ✅ |
| Pack 保底机制 (pity) | ✅ |
| NFT 预铸造 + Vault | ✅ |
| Redemption 兑换流程 | ✅ |

**结论**: A 的 5 个独有功能 + B 的 14 个独有功能 = 19 个模块全覆盖。✅ CE 通过。

---

## 执行计划 (MECE Sprint)

### Sprint M1: 基础设施对齐 (2天)
```
目标: B 能跑起来 + config 穷尽
任务:
  1. B 的 config.py 加入 A 独有配置项:
     - TELEGRAM_BOT_TOKEN
     - TELEGRAM_CHAT_ID
     - ALCHEMY_API_KEY
     - TWITTER_CLIENT_ID / TWITTER_CLIENT_SECRET / TWITTER_REDIRECT_URI
  2. requirements.txt 合并 (B 为主 + A 独有依赖)
  3. 验证 B 在 GCP 双节点正常启动
验收: 56+ 端点加载，0 warning
```

### Sprint M2: 移植 A 独有模块 (5天)
```
目标: CE 穷尽 — A 的所有独有功能进入 B
任务:
  M4: 树形抽卡引擎 → B 的 pack_engine.py 新增 StrategyPlugin 接口 (2天)
  M13: Telegram 通知 → 新建 services/notification.py (1天)
  M14: Twitter OAuth 完整流程 → 扩展 services/auth.py (1天)
  M20: 测试种子 → 新建 tests/ + 移植 test_lottery + 新增 test_auth (1天)
验收: 所有 A 独有功能可调用 + 测试通过
```

### Sprint M3: Bug 修复 + 安全审计 (3天)
```
目标: 两个源的已知 bug 全清零
任务:
  1. 修 A 源码中的 typos (ogger, module_validate, prodabilities) — 虽然不用 A，但移植的代码要干净
  2. 审计 B 的抽卡概率计算 (pack_engine.py)
  3. 审计 B 的 Stripe Webhook 签名验证
  4. 审计 B 的 Buyback 85% 价格计算
  5. 补全 B 的测试覆盖: auth, pack, marketplace, buyback, wallet
验收: pytest 全绿 + 安全审计报告
```

### Sprint M4: 前端适配 + 部署 (5天)
```
目标: Lumina 前端对接合并后的 B 后端
任务:
  1. 前端 API 调用更新 (如果有 A 的遗留调用)
  2. 新增页面: Marketplace, Buyback, Wallet, Redemption
  3. GCP 双节点部署 (拜占庭验证)
  4. Vercel 前端更新
验收: 端到端流程通: 注册 → 购买 → 开盒 → 交易 → 回购
```

---

## 数据模型 MECE 映射 (如果 A 有生产数据)

| A 表 | B 表 | 映射 |
|------|------|------|
| `users` | `users` | sol_address→wallet_address, twitter_id+twitter_name→twitter_handle |
| `nfts` | `nft` + `user_vault` | nft→nft, 持有关系→user_vault |
| `nft_categories` | `nft.rarity` + `nft.category` | 展平到 nft 字段 |
| `orders` | `pack_opening` / `redemption_order` | 按 order_type 分流 |
| `balances` | `users.credit_balance` | 金额直接映射 |
| `referral_relationships` | `users.referred_by` | 关系扁平化 |
| `shipping_addresses` | `redemption_order.shipping_*` | 内联到兑换订单 |
| (无) | `marketplace_listing` | B 独有，无需迁移 |
| (无) | `buyback_request` | B 独有，无需迁移 |
| (无) | `wallet_transaction` | B 独有，无需迁移 |
| (无) | `leaderboard_entry` | B 独有，无需迁移 |
| (无) | `admin_audit_log` | B 独有，无需迁移 |

---

## 风险 MECE

| 风险类别 | 具体风险 | 缓解 |
|---------|---------|------|
| **ME 违反** | 同一功能从两个源取导致逻辑冲突 | 严格按模块矩阵，code review 检查 |
| **CE 违反** | 遗漏 A 的某个功能 | 移植完后用 diff 确认 A 的所有 service 都被覆盖 |
| **接口冲突** | A 和 B 的同名函数签名不同 | 以 B 为准，移植时适配 B 的签名 |
| **数据冲突** | A/B 同名表字段不兼容 | 以 B 的 schema 为准，迁移脚本做映射 |

---

## 总结

```
MECE 合并 = 以 B 为骨架 + A 的 5 个独有模块移植
  - 20 个模块，每个有且仅有一个来源 (ME ✅)
  - A 的 5 个独有 + B 的 14 个独有 = 全覆盖 (CE ✅)
  - 4 个 Sprint，共 ~15 天
  - 0 模块需要混合两个源的同层逻辑
```
