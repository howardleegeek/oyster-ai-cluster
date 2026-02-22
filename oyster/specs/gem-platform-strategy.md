# GEM 人造钻石 RWA 平台 — 全栈改造战略

> **目标**: 将现有 Lumina 前端 + nft-mgmt-api 后端改造为 PRD v0.1.3 定义的完整 GEM 平台
> **核心原则**: 保留前端 (React 19 + Vite + Tailwind)，后端从 nft-mgmt-api 扩展，不重写
> **日期**: 2026-02-11

---

## 1. 现状盘点

### 1.1 前端 (Lumina) — 28 文件, ~200KB
| 模块 | 状态 | 问题 |
|------|------|------|
| 卡包商店 (4 tier) | ✅ UI 完整 | 价格硬编码前端，无后端验证 |
| 抽卡动画 + 揭示 | ✅ UI 完整 | `Math.random()` 客户端抽奖，可被操控 |
| Vault/Dashboard | ✅ UI 完整 | 纯内存 state，刷新丢失 |
| Marketplace 二级市场 | ✅ 基础 UI | 只有 mock 数据，无真实交易 |
| 钱包连接 (Phantom) | ✅ 可用 | 指向 devnet，收款地址硬编码 |
| SOL 支付 | ✅ 可用 | 无后端确认，前端自行触发开包 |
| Gemini AI Lore | ✅ 可用 | 锦上添花功能，可保留 |
| 用户认证 | ❌ 缺失 | PRD 要求邮箱+Twitter+钱包三合一 |
| 排行榜 | ❌ 缺失 | PRD 要求周/月/全时间排名 |
| 货币系统 | ❌ 缺失 | PRD 要求 USDC/信用卡/跨链充值 |
| 推荐系统 | ❌ 缺失 | PRD 要求推荐码+奖励 |
| NFT 议价 (Make Offer) | ❌ 缺失 | PRD 要求买卖双方议价流程 |
| 实物兑换 (多选+物流) | ⚠️ 简化版 | 只有单个兑换，无多选/地址管理/物流追踪 |
| 后台管理系统 | ❌ 完全缺失 | PRD 要求 NFT/盲盒 CRUD 管理后台 |

### 1.2 后端 (nft-mgmt-api) — ~60KB Python, FastAPI
| 模块 | 状态 | 可复用 |
|------|------|--------|
| FastAPI + SQLAlchemy + MySQL | ✅ | 架构直接复用 |
| NFT Model (collection + mint + payment) | ✅ | 扩展字段即可 |
| Redis Session/Cache | ✅ | 直接复用 |
| Solana web3 (签名验证) | ✅ | 直接复用 |
| TON web3 | ✅ | 可能复用 |
| Twitter OAuth | ✅ | 直接复用 |
| SendGrid 邮件 | ✅ | 直接复用 |
| Shippo 地址解析 | ✅ | 实物兑换复用 |
| NFT 序列号生成 | ✅ | 盲盒 NFT 编号复用 |
| NftPayment (链上支付追踪) | ✅ | Pack 购买复用 |
| 用户系统 | ❌ | models/__init__ 引用了但文件缺失 |
| Order 系统 | ❌ | 同上，引用了但文件缺失 |
| Pack/盲盒系统 | ❌ | 需新建 |
| Marketplace 交易 | ❌ | 需新建 |
| 回购系统 | ❌ | 需新建 |
| 货币/充值系统 | ❌ | 需新建 |
| 推荐系统 | ❌ | 需新建 |
| Admin 后台 | ❌ | 需新建 |

---

## 2. 架构设计

### 2.1 总体架构

```
┌─ 前端 (Lumina React 19) ──────────────────────────────┐
│  Pack Store → Marketplace → Dashboard → Admin Panel    │
│  Phantom Wallet → SOL/USDC 支付                        │
└────────────────────┬───────────────────────────────────┘
                     │ REST API (HTTPS)
┌────────────────────▼───────────────────────────────────┐
│  GEM Backend (FastAPI) — 基于 nft-mgmt-api 扩展          │
│  ┌─────────────────────────────────────────────────┐   │
│  │ API Layer                                        │   │
│  │  /auth  /packs  /nfts  /market  /orders         │   │
│  │  /buyback  /wallet  /referral  /admin  /rank    │   │
│  ├─────────────────────────────────────────────────┤   │
│  │ Service Layer                                    │   │
│  │  PackService  MarketService  BuybackService     │   │
│  │  OrderService  WalletService  ReferralService   │   │
│  ├─────────────────────────────────────────────────┤   │
│  │ Data Layer                                       │   │
│  │  MySQL (主库) + Redis (缓存/Session)              │   │
│  ├─────────────────────────────────────────────────┤   │
│  │ External Services                                │   │
│  │  Solana RPC → SendGrid → Shippo → CoinGecko     │   │
│  │  Stripe (信用卡) → Shyft (NFT Market API)        │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────────┐
│  Solana Blockchain                                      │
│  cNFT (Compressed NFT) → SPL Token → USDC              │
└────────────────────────────────────────────────────────┘
```

### 2.2 数据库设计 (MySQL 扩展)

**保留现有表:**
- `nft_collection_meta` — 宝石 NFT 系列元数据
- `nft` — 单个 NFT 实例
- `nft_payment` — 链上支付记录
- `nft_sequence` — NFT 序列号

**新增表:**

```sql
-- 用户系统
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    twitter_handle VARCHAR(255),
    wallet_address VARCHAR(64) UNIQUE NOT NULL,
    avatar_seed VARCHAR(64),           -- 随机头像种子
    referral_code VARCHAR(16) UNIQUE,  -- 推荐码
    referred_by VARCHAR(36),           -- 谁推荐来的
    credit_balance DECIMAL(20,6) DEFAULT 0,  -- 平台内货币余额
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_wallet (wallet_address),
    INDEX idx_email (email)
);

-- 盲盒系列 (Pack Series)
CREATE TABLE pack_series (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    description TEXT,
    cover_image_url VARCHAR(512),
    status ENUM('ACTIVE','INACTIVE','SOLD_OUT') DEFAULT 'ACTIVE',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 盲盒定义 (Pack)
CREATE TABLE packs (
    id VARCHAR(36) PRIMARY KEY,
    series_id VARCHAR(36) NOT NULL,
    name VARCHAR(128) NOT NULL,
    description TEXT,
    price_usd DECIMAL(10,2) NOT NULL,    -- USD 定价
    price_sol DECIMAL(20,9),             -- SOL 定价 (可选，实时换算)
    image_gradient VARCHAR(128),
    xp_reward INT DEFAULT 0,
    max_supply INT,                       -- 总量限制 (NULL=无限)
    current_supply INT DEFAULT 0,         -- 已售出
    status ENUM('ACTIVE','INACTIVE','SOLD_OUT') DEFAULT 'ACTIVE',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (series_id) REFERENCES pack_series(id)
);

-- 盲盒概率配置 (每个 Pack 的 NFT 掉落表)
CREATE TABLE pack_drop_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pack_id VARCHAR(36) NOT NULL,
    nft_collection_meta_id INT NOT NULL,  -- 关联到哪个 NFT 集合
    rarity ENUM('COMMON','RARE','EPIC','LEGENDARY') NOT NULL,
    drop_rate DECIMAL(5,2) NOT NULL,      -- 掉落概率 (百分比)
    fmv_min DECIMAL(10,2),                -- 该稀有度最低 FMV
    fmv_max DECIMAL(10,2),                -- 该稀有度最高 FMV
    FOREIGN KEY (pack_id) REFERENCES packs(id),
    FOREIGN KEY (nft_collection_meta_id) REFERENCES nft_collection_meta(id)
);

-- 抽卡记录 (Pack Opening)
CREATE TABLE pack_openings (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    pack_id VARCHAR(36) NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    payment_id INT,                       -- 关联 nft_payment
    total_cost_usd DECIMAL(10,2),
    total_cost_sol DECIMAL(20,9),
    status ENUM('PENDING_PAYMENT','PAID','OPENED','CANCELLED') DEFAULT 'PENDING_PAYMENT',
    opened_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (pack_id) REFERENCES packs(id),
    FOREIGN KEY (payment_id) REFERENCES nft_payment(id)
);

-- 用户 NFT 库存 (Vault)
CREATE TABLE user_vault (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    nft_id VARCHAR(255) NOT NULL,
    source ENUM('PACK_OPENING','MARKETPLACE_BUY','TRANSFER') NOT NULL,
    source_id VARCHAR(36),               -- pack_opening_id 或 trade_id
    status ENUM('VAULTED','LISTED','PROCESSING','DELIVERED','SOLD','BUYBACK') DEFAULT 'VAULTED',
    fmv DECIMAL(10,2),                   -- 当前公允市场价
    acquired_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (nft_id) REFERENCES nft(id),
    INDEX idx_user_status (user_id, status)
);

-- 二级市场挂售
CREATE TABLE market_listings (
    id VARCHAR(36) PRIMARY KEY,
    seller_id VARCHAR(36) NOT NULL,
    vault_item_id INT NOT NULL,
    nft_id VARCHAR(255) NOT NULL,
    asking_price_usd DECIMAL(10,2) NOT NULL,
    status ENUM('ACTIVE','SOLD','CANCELLED','EXPIRED') DEFAULT 'ACTIVE',
    listed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    sold_at DATETIME,
    buyer_id VARCHAR(36),
    FOREIGN KEY (seller_id) REFERENCES users(id),
    FOREIGN KEY (vault_item_id) REFERENCES user_vault(id),
    FOREIGN KEY (nft_id) REFERENCES nft(id),
    INDEX idx_status_price (status, asking_price_usd)
);

-- 议价 (Make Offer)
CREATE TABLE market_offers (
    id VARCHAR(36) PRIMARY KEY,
    listing_id VARCHAR(36) NOT NULL,
    buyer_id VARCHAR(36) NOT NULL,
    offer_price_usd DECIMAL(10,2) NOT NULL,
    status ENUM('PENDING','ACCEPTED','REJECTED','CANCELLED','EXPIRED') DEFAULT 'PENDING',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    responded_at DATETIME,
    FOREIGN KEY (listing_id) REFERENCES market_listings(id),
    FOREIGN KEY (buyer_id) REFERENCES users(id)
);

-- 回购记录
CREATE TABLE buyback_requests (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    vault_item_id INT NOT NULL,
    nft_id VARCHAR(255) NOT NULL,
    fmv_at_request DECIMAL(10,2) NOT NULL,
    buyback_rate DECIMAL(3,2) DEFAULT 0.85,
    buyback_price DECIMAL(10,2) NOT NULL,  -- fmv * rate
    status ENUM('PENDING','APPROVED','PAID','REJECTED') DEFAULT 'PENDING',
    payment_tx_hash VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (vault_item_id) REFERENCES user_vault(id)
);

-- 实物兑换订单
CREATE TABLE redemption_orders (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    shipping_name VARCHAR(128),
    shipping_address_line1 VARCHAR(255),
    shipping_address_line2 VARCHAR(255),
    shipping_city VARCHAR(128),
    shipping_state VARCHAR(128),
    shipping_postal_code VARCHAR(32),
    shipping_country_code VARCHAR(4),
    shipping_phone VARCHAR(32),
    shipping_fee DECIMAL(10,2) DEFAULT 0,
    status ENUM('PROCESSING','PREPARING','SHIPPED','DELIVERED') DEFAULT 'PROCESSING',
    tracking_number VARCHAR(128),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    shipped_at DATETIME,
    delivered_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 兑换订单明细 (多个 NFT → 一个订单)
CREATE TABLE redemption_order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id VARCHAR(36) NOT NULL,
    vault_item_id INT NOT NULL,
    nft_id VARCHAR(255) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES redemption_orders(id),
    FOREIGN KEY (vault_item_id) REFERENCES user_vault(id)
);

-- 充值记录
CREATE TABLE deposits (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    amount_usd DECIMAL(10,2) NOT NULL,
    method ENUM('CREDIT_CARD','SOLANA_USDC','CROSS_CHAIN_STABLE') NOT NULL,
    external_tx_id VARCHAR(255),         -- Stripe charge ID 或链上 tx hash
    status ENUM('PENDING','CONFIRMED','FAILED') DEFAULT 'PENDING',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    confirmed_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 推荐奖励
CREATE TABLE referral_rewards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    referrer_id VARCHAR(36) NOT NULL,
    referred_id VARCHAR(36) NOT NULL,
    reward_amount DECIMAL(10,2),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (referrer_id) REFERENCES users(id),
    FOREIGN KEY (referred_id) REFERENCES users(id)
);
```

### 2.3 关键安全设计

**抽卡概率 — 必须服务端计算:**
```
前端发起购买 → 后端验证支付 → 后端 RNG 抽卡 → 返回结果 → 前端播放动画
                 ↑ 链上确认                ↑ 服务端随机
                 不可绕过                   不可操控
```

**支付流程:**
```
1. 前端请求开包 → 后端创建 pack_opening (PENDING_PAYMENT)
2. 后端返回应付金额 + 收款地址
3. 前端调 Phantom 签名发送 SOL/USDC
4. 后端监听/验证链上交易 (tx hash)
5. 确认到账 → 后端执行抽卡 → 更新状态为 OPENED
6. 返回结果给前端展示动画
```

---

## 3. 开发阶段 (5 个 Sprint)

### Sprint 1: 用户系统 + 后端骨架 (Week 1)
**后端:**
- [ ] 新建 `users` 表 + model/schema/api/service
- [ ] Solana 钱包签名登录 (复用 `web3_sol.py`)
- [ ] 邮箱 OTP 登录 (复用 `sendmail.py`)
- [ ] Twitter OAuth 绑定 (复用 `oauth.py`)
- [ ] JWT token 签发 + 中间件鉴权
- [ ] 用户基础 CRUD: profile, avatar, wallet binding

**前端改造:**
- [ ] 新增 Login/Register 页面 (邮箱 + 钱包 + Twitter)
- [ ] 替换 WalletContext → AuthContext (JWT + 钱包双认证)
- [ ] Navbar 显示用户信息 (avatar, address, balance)
- [ ] 路由保护 (未登录跳转 login)

### Sprint 2: 盲盒系统 — 后端主导 (Week 2)
**后端:**
- [ ] `pack_series`, `packs`, `pack_drop_table` 表 + CRUD
- [ ] `pack_openings` 表 + 开包逻辑
- [ ] **服务端抽卡引擎**: 安全随机数 (`secrets.SystemRandom`) + 概率引擎
- [ ] 期望值计算 API: `GET /packs/{id}/odds`
- [ ] 支付验证: 链上 tx 确认 → 触发开包
- [ ] `user_vault` 表: 开包结果入库
- [ ] cNFT mint 集成 (可选，先做数据库 NFT，后续上链)

**前端改造:**
- [ ] Pack Store 改为从 `GET /packs` 拉数据 (不再硬编码)
- [ ] 购买流程: 前端 → 后端创建订单 → 钱包支付 → 后端确认 → 返回结果
- [ ] PackOpening 动画保留，但数据从后端接收
- [ ] 概率透明展示 (从后端 API 获取)

### Sprint 3: Marketplace + 回购 (Week 3)
**后端:**
- [ ] `market_listings` 表 + 上架/下架/搜索 API
- [ ] `market_offers` 议价系统: 发起/接受/拒绝/取消
- [ ] 购买流程: 链上支付 → 确认 → NFT 转移 (vault 变更所有者)
- [ ] `buyback_requests` 回购系统: 申请 → 审核 → 打款
- [ ] 手续费计算 (2% marketplace fee)
- [ ] Shyft NFT API 集成 (PRD 推荐: https://docs.shyft.to)

**前端改造:**
- [ ] Marketplace 从后端拉真实 listing 数据
- [ ] 新增 Make Offer UI (议价弹窗 + 议价管理页)
- [ ] BuyModal 接入后端支付流程
- [ ] Dashboard 增加回购按钮 + 回购确认弹窗
- [ ] 交易历史列表

### Sprint 4: 货币系统 + 实物兑换 + 推荐 (Week 4)
**后端:**
- [ ] `deposits` 充值系统:
  - Stripe 信用卡充值
  - Solana USDC 转账监听
  - 跨链稳定币 (预留接口)
- [ ] 平台内货币余额管理 (credit_balance on users)
- [ ] `redemption_orders` + `redemption_order_items`: 多 NFT 批量兑换
- [ ] 收货地址管理 (CRUD)
- [ ] 物流状态更新 API + webhook
- [ ] 运费计算 (复用 Shippo `address_api.py`)
- [ ] `referral_rewards` 推荐系统: 生成码/使用码/奖励发放

**前端改造:**
- [ ] 新增充值页面 (信用卡 + USDC + 跨链)
- [ ] Dashboard 余额显示 (平台币 + SOL)
- [ ] 实物兑换改造: 多选 NFT → 填地址 → 计运费 → 确认
- [ ] 订单追踪页面 (Processing → Shipped → Delivered)
- [ ] 推荐码展示 + 输入推荐码 + 推荐历史

### Sprint 5: 排行榜 + Admin 后台 + 上线 (Week 5)
**后端:**
- [ ] 排行榜 API: 按 vault 总价值排名 (周/月/全时间)
- [ ] Admin API (需 admin 角色鉴权):
  - NFT 管理: CRUD + JSON 批量导入 + 上下架
  - 盲盒管理: 系列/概率/价格/NFT 池调整
  - 用户管理: 查看/禁用
  - 订单管理: 状态更新/物流录入
  - 回购管理: 审核/批量处理
- [ ] 切换 Solana mainnet + 配置 RPC (Helius/QuickNode)
- [ ] 安全审计: rate limiting, input validation, SQL injection 防护

**前端改造:**
- [ ] 排行榜页面 (周/月/全时间切换 + 搜索)
- [ ] Admin Panel (独立路由 /admin):
  - NFT 列表 + 编辑 + 批量导入
  - 盲盒配置界面 (拖拽调概率)
  - 订单管理 + 物流更新
  - 数据看板 (总收入/总 NFT/用户数)
- [ ] 切换 devnet → mainnet
- [ ] 性能优化 + 错误边界

---

## 4. 技术决策

### 4.1 为什么保留前端不重写
- Lumina UI 质量高 (暗黑风格、动画、响应式)
- PRD 的 Figma 交互原型已基于类似设计
- React 19 + Vite 性能好，组件结构清晰
- 只需: 接后端 API + 补缺失页面，不需要重做已有的

### 4.2 为什么基于 nft-mgmt-api 扩展
- FastAPI + SQLAlchemy + MySQL 架构成熟
- Solana web3 签名验证已就绪
- Redis session/cache 已就绪
- Twitter OAuth、SendGrid 邮件、Shippo 地址 已就绪
- NFT 数据模型 (collection + mint + payment) 可直接复用
- 缺失的 models (order/wallet/community) 说明团队打算扩展，方向一致

### 4.3 cNFT vs 数据库 NFT
- **Phase 1 (MVP)**: 数据库 NFT — 快速上线，所有权在 user_vault 表
- **Phase 2**: 上链 cNFT — 使用 Solana Compressed NFT (Bubblegum)，成本极低
- PRD 提到的第三方: Shyft API (https://docs.shyft.to) 可用于 NFT marketplace 构建

### 4.4 支付方式优先级
1. **Solana SOL** — 已有 (Phantom wallet)
2. **Solana USDC** — SPL Token 转账，稳定币无波动风险
3. **信用卡** — Stripe，requirements.txt 已有 stripe 依赖
4. **跨链稳定币** — Phase 2，预留接口

---

## 5. 文件结构规划 (后端扩展)

```
nft-mgmt-api/
├── app/
│   ├── api/
│   │   ├── nft.py          # (现有) NFT 基础 CRUD
│   │   ├── auth.py          # (新增) 登录/注册/钱包绑定
│   │   ├── pack.py          # (新增) 盲盒购买/开包
│   │   ├── market.py        # (新增) 二级市场/议价
│   │   ├── buyback.py       # (新增) 回购
│   │   ├── order.py         # (新增) 实物兑换订单
│   │   ├── wallet.py        # (新增) 充值/余额
│   │   ├── referral.py      # (新增) 推荐系统
│   │   ├── rank.py          # (新增) 排行榜
│   │   └── admin.py         # (新增) 后台管理
│   ├── models/
│   │   ├── nft.py           # (现有) 扩展 rarity/fmv 字段
│   │   ├── user.py          # (新增) 用户
│   │   ├── pack.py          # (新增) 盲盒
│   │   ├── market.py        # (新增) 二级市场
│   │   ├── order.py         # (新增) 订单
│   │   └── enums.py         # (现有) 扩展枚举
│   ├── services/
│   │   ├── nft.py           # (现有)
│   │   ├── auth.py          # (新增) 认证
│   │   ├── pack_engine.py   # (新增) 抽卡概率引擎 ⚡ 核心
│   │   ├── market.py        # (新增) 交易撮合
│   │   ├── buyback.py       # (新增) 回购审核
│   │   ├── payment.py       # (新增) 支付验证 (SOL/USDC/Stripe)
│   │   └── referral.py      # (新增) 推荐奖励
│   ├── db/
│   │   ├── nft.py           # (现有)
│   │   ├── user.py          # (新增)
│   │   ├── pack.py          # (新增)
│   │   ├── market.py        # (新增)
│   │   └── order.py         # (新增)
│   └── plib/                # (现有) 全部复用
│       ├── web3_sol.py
│       ├── oauth.py
│       ├── sendmail.py
│       └── address_api.py
├── migrations/              # (新增) Alembic 数据库迁移
└── admin/                   # (新增) Admin 前端 (可选: 用 React Admin)
```

---

## 6. 风险与对策

| 风险 | 影响 | 对策 |
|------|------|------|
| 客户端抽卡可被操控 | P0 安全漏洞 | Sprint 2 强制服务端抽卡 |
| SOL 价格波动导致定价混乱 | 用户体验差 | 主定价用 USD，SOL 实时换算 |
| Solana mainnet RPC 限速 | 支付失败 | 用 Helius/QuickNode 商业 RPC |
| cNFT mint 失败 | 用户拿不到 NFT | Phase 1 先数据库 NFT，后补链上 |
| models/__init__ 引用缺失文件 | 启动报错 | Sprint 1 补齐 user/order model |
| 高并发抽卡概率偏差 | 概率不公 | 用 `secrets.SystemRandom` + DB 事务锁 |
| 跨链充值复杂度高 | 延期 | Phase 2 处理，Phase 1 只做 SOL+USDC+Stripe |

---

## 7. Edge Case 全集 (按模块)

### 7.1 抽卡引擎 Edge Cases
| # | 场景 | 风险 | 处理 |
|---|------|------|------|
| E1 | 用户支付成功但服务器在抽卡前崩溃 | 付了钱没拿到卡 | pack_opening 状态机: PAID 但未 OPENED → 重启后扫描补发 |
| E2 | 同一 tx hash 重复提交 (重放攻击) | 一笔钱开多次包 | nft_payment.transaction_hash UNIQUE 约束 + 幂等校验 |
| E3 | 前端篡改 pack_id/quantity 参数 | 用 Starter 价买 Max 包 | 后端从 DB 查 pack 价格，不信任前端传的价格 |
| E4 | 概率配置错误: 总和 ≠ 100% | 抽卡异常 | 后端创建/修改盲盒时强制校验 sum(drop_rate) == 100 |
| E5 | 盲盒库存耗尽但前端未更新 | 付了钱但 SOLD_OUT | 后端 atomic decrement current_supply, 库存不够直接拒绝+退款 |
| E6 | 并发高峰大量用户同时抽卡 | 超卖 | DB 事务 SELECT FOR UPDATE on packs.current_supply |
| E7 | NFT 池为空 (某稀有度的 NFT 全被抽完) | 抽到不存在的 NFT | pack_drop_table 必须有足够 NFT，否则降级到次一级稀有度 |
| E8 | 用户快速连点 "Purchase" | 重复下单 | 前端 disable 按钮 + 后端 rate limit (1 次/5 秒/用户) |
| E9 | Solana 交易已发送但确认超时 | 用户不知道成功没 | 后端异步轮询 tx 状态 (最多 60s)，超时标记 PENDING_CONFIRMATION |
| E10 | 用户余额不足但前端未校验 | Phantom 弹窗报错 | 前端预检查 balance >= cost，后端也检查 |
| E11 | 同一用户同时在多个设备购买 | 并发订单冲突 | 用户级锁 (Redis distributed lock on user_id) |
| E12 | 概率引擎随机数可预测 | 概率操控 | 使用 `secrets.SystemRandom` 而非 `random.random()` |

### 7.2 支付系统 Edge Cases
| # | 场景 | 风险 | 处理 |
|---|------|------|------|
| E13 | SOL 价格在支付期间剧烈波动 | 用户多付/少付 | 锁定报价 5 分钟，过期重新计算 |
| E14 | 用户发送了错误金额的 SOL | 金额不匹配 | 后端验证 tx amount ± 0.5% 容差，否则退款 |
| E15 | Solana RPC 节点宕机 | 无法确认交易 | 多 RPC fallback (Helius → QuickNode → public) |
| E16 | Stripe 充值成功但 webhook 未到达 | 充值金额未入账 | 定时任务扫描 Stripe charges 对账 |
| E17 | 用户充值后立即消费但余额未更新 | 余额不足误判 | 充值确认后同步更新 credit_balance (事务内) |
| E18 | USDC 转账发到错误地址 | 资金丢失 | 前端只展示系统收款地址，不允许用户输入 |
| E19 | 链上交易成功但后端标记为失败 | 用户投诉 | 后端定期对账 (每5分钟扫描 PENDING 状态的 payment) |
| E20 | 同一 Stripe 支付 webhook 重复投递 | 重复入账 | webhook 幂等处理 (deposit.external_tx_id UNIQUE) |
| E21 | 用户使用已被 revoke 的 Phantom 钱包 | 签名失败 | 前端捕获 4001 错误码，提示重新连接 |

### 7.3 Marketplace Edge Cases
| # | 场景 | 风险 | 处理 |
|---|------|------|------|
| E22 | 卖家在买家付款瞬间下架 | 付了钱但 NFT 已不可用 | DB 事务: 检查 listing.status == ACTIVE → 扣款 → 转移，全原子 |
| E23 | 同一 NFT 同时被两个买家购买 | 双重出售 | listing 表 SELECT FOR UPDATE + 状态检查 |
| E24 | 卖家设价 $0.01 (恶意低价) | 洗钱/刷单 | 最低挂售价限制 (>= FMV * 50%) |
| E25 | 买家议价后卖家长期不回应 | offer 永远 PENDING | offer 72h 自动过期 (cron job) |
| E26 | 议价金额 > 挂售价 | 异常数据 | 后端校验 offer_price < asking_price |
| E27 | 卖家接受议价后买家余额不足 | 成交失败 | 接受后给买家 24h 支付窗口，过期自动取消 |
| E28 | 用户给自己的 listing 发 offer | 自买自卖 | 后端校验 buyer_id != seller_id |
| E29 | 已卖出的 NFT 仍显示在市场 | 数据不一致 | 购买成功后同步更新 listing.status + 缓存失效 |
| E30 | 大量 mock offer 攻击 (恶意占 listing) | DoS 正常用户 | 每个用户对同一 listing 最多 1 个 active offer |
| E31 | 卖家修改 NFT metadata 后上架 | 买家看到的信息不一致 | 上架时快照 metadata 到 listing |

### 7.4 回购系统 Edge Cases
| # | 场景 | 风险 | 处理 |
|---|------|------|------|
| E32 | 用户同时提交回购 + 上架市场 | 同一 NFT 两个操作 | 检查 vault_item.status, 非 VAULTED 拒绝操作 |
| E33 | FMV 在回购审核期间变化 | 回购价不公允 | 回购价锁定在申请时的 FMV * 85% |
| E34 | 大量用户同时回购导致平台资金不足 | 无法打款 | 设置每日回购上限 + 平台金库余额预警 |
| E35 | 回购打款失败 (链上) | 用户未收到钱 | 重试 3 次，失败后人工介入 + 通知管理员 |
| E36 | 用户提交回购后取消 | 状态管理 | PENDING 状态可取消，APPROVED 后不可取消 |
| E37 | Admin 错误审核 (批量误操作) | 大量误回购 | Admin 批量操作需二次确认 + 操作日志 |

### 7.5 实物兑换 Edge Cases
| # | 场景 | 风险 | 处理 |
|---|------|------|------|
| E38 | 用户选择了已上架市场的 NFT 兑换 | 冲突 | 只允许 VAULTED 状态的 NFT 发起兑换 |
| E39 | 偏远国家/禁运国家 | 无法配送 | 国家黑名单校验 (在地址填写时拒绝) |
| E40 | 运费计算后价格变化 (汇率/物流涨价) | 用户多付/少付 | 运费锁定 30 分钟，过期重新计算 |
| E41 | 用户填写虚假地址 | 物流退回 | Shippo 地址验证 (已有 address_api.py) |
| E42 | 实物发货后 NFT 应销毁 | NFT 仍在用户手里 | 发货时 vault_item.status → DELIVERED, 链上 burn (Phase 2) |
| E43 | 海关扣件/清关失败 | 实物卡在海关 | 需要用户提供清关码 (某些国家), 状态更新为 CUSTOMS_HOLD |
| E44 | 多件兑换部分发货 | 订单状态不一致 | order_items 级别的状态追踪，order 整体 status 取最慢的 |
| E45 | 用户兑换后修改地址 | 已发货无法改 | PROCESSING 可改，SHIPPED 后不可改 |

### 7.6 用户系统 Edge Cases
| # | 场景 | 风险 | 处理 |
|---|------|------|------|
| E46 | 同一钱包绑定到两个邮箱账号 | 数据冲突 | wallet_address UNIQUE 约束 |
| E47 | 用户在 Phantom 切换钱包 | 前端状态不一致 | 监听 accountChanged 事件 (已有) + 后端 session 失效 |
| E48 | OTP 暴力破解 | 账号被盗 | OTP 5 次错误锁定 15 分钟 + rate limit |
| E49 | Twitter OAuth token 过期 | 绑定失败 | OAuth token 只用于一次性验证，不存储 |
| E50 | 用户注销账号但有挂售/兑换中的 NFT | 孤儿数据 | 注销前强制下架所有 listing + 取消 pending 订单 |
| E51 | 推荐码被自己使用 | 刷推荐 | 后端校验 referrer_id != referred_id |
| E52 | 推荐码被重复使用 (同一用户) | 重复奖励 | 每个用户只能使用一次推荐码 (referred_by 字段非空拒绝) |
| E53 | 大量注册刷推荐奖励 (女巫攻击) | 虚假推荐 | 推荐奖励需要被推荐人完成首次消费后才发放 |

### 7.7 Admin 后台 Edge Cases
| # | 场景 | 风险 | 处理 |
|---|------|------|------|
| E54 | Admin 修改了正在售卖的盲盒概率 | 已购买用户概率不一致 | 修改概率生成新版本，已购买的用旧版本开包 |
| E55 | JSON 批量导入 NFT 格式错误 | 脏数据入库 | 严格 schema 校验 + 失败回滚 (事务) |
| E56 | Admin 下架有用户持有的 NFT | 用户 NFT 消失 | 下架只影响新抽取/购买，不影响已持有 |
| E57 | 多个 Admin 同时修改同一条记录 | 数据覆盖 | 乐观锁 (version 字段) |
| E58 | Admin 权限泄露 | 平台被操控 | Admin JWT 独立签发 + IP 白名单 + 操作审计日志 |

### 7.8 通用 Edge Cases
| # | 场景 | 风险 | 处理 |
|---|------|------|------|
| E59 | 前端和后端时区不一致 | 时间显示错误 | 全部使用 UTC，前端本地化展示 |
| E60 | 浮点精度问题 (0.1 + 0.2 ≠ 0.3) | 金额计算错误 | 后端全部用 DECIMAL(20,6)，前端 toFixed(2) |
| E61 | 数据库连接池耗尽 | 服务不可用 | pool_size + max_overflow 配置 + 连接超时 |
| E62 | Redis 宕机 | Session 丢失/缓存失效 | Redis Sentinel + graceful degradation (降级到 DB 查询) |
| E63 | API 被 DDoS | 服务不可用 | Cloudflare/Nginx rate limit + WAF |
| E64 | SQL 注入 | 数据泄露 | SQLAlchemy ORM (参数化查询) + input validation |
| E65 | XSS (用户输入 NFT 名字含脚本) | 前端被注入 | 后端 HTML escape + 前端 React 自动转义 |
| E66 | CORS 配置过于宽松 | CSRF 攻击 | 生产环境限制 origins 为前端域名 |
| E67 | JWT 过期但用户正在支付 | 操作中断 | JWT 有效期 24h + 支付操作独立 token |
| E68 | 手机端 Phantom 深链接跳转失败 | 无法支付 | 检测 mobile → 使用 Phantom 深链接协议 |

---

## 8. Dispatch 建议

按 Howard 的指挥矩阵，建议这样分工:

| Sprint | 主力执行 | 原因 |
|--------|---------|------|
| Sprint 1 (用户系统) | GLM | 标准 CRUD，清晰 spec |
| Sprint 2 (盲盒引擎) | GLM + Opus review | 概率引擎是核心，需要 Opus 审安全 |
| Sprint 3 (Marketplace) | GLM | 标准交易逻辑 |
| Sprint 4 (货币+兑换) | GLM (后端) + Codex (Stripe 集成) | Stripe 需要 API 调试 |
| Sprint 5 (Admin+上线) | GLM | CRUD 管理后台 |

**前端改造可以和后端并行 dispatch。**

---

## 8. 关键 API 概览

```
# Auth
POST   /auth/wallet-login          # Solana 钱包签名登录
POST   /auth/email-otp             # 邮箱 OTP 发送
POST   /auth/email-verify          # 邮箱 OTP 验证
POST   /auth/twitter-bind          # Twitter OAuth 绑定

# Packs
GET    /packs                      # 盲盒列表 (含系列筛选)
GET    /packs/{id}                 # 盲盒详情 + 概率 + 期望值
POST   /packs/{id}/purchase        # 购买 → 返回支付信息
POST   /packs/confirm-payment      # 支付确认 → 触发开包 → 返回结果

# NFTs / Vault
GET    /vault                      # 用户库存
GET    /vault/{id}                 # 单个 NFT 详情
POST   /vault/{id}/list            # 上架二级市场
POST   /vault/{id}/delist          # 下架
POST   /vault/{id}/buyback         # 申请回购
POST   /vault/{id}/instant-sell    # 立即卖给平台 (85% FMV)

# Marketplace
GET    /market/listings            # 市场列表 (搜索/筛选/排序)
POST   /market/{listing_id}/buy    # 购买
POST   /market/{listing_id}/offer  # 发起议价
PUT    /market/offers/{id}         # 接受/拒绝议价

# Orders (实物兑换)
POST   /orders/redeem              # 批量兑换 (多 NFT)
GET    /orders                     # 订单列表
GET    /orders/{id}                # 订单详情 + 物流状态

# Wallet
GET    /wallet/balance             # 余额 (平台币 + SOL + USDC)
POST   /wallet/deposit/stripe      # 信用卡充值
POST   /wallet/deposit/usdc        # USDC 充值确认

# Referral
GET    /referral/code              # 获取自己的推荐码
POST   /referral/use               # 使用别人的推荐码
GET    /referral/history           # 推荐历史

# Rank
GET    /rank?period=weekly|monthly|all  # 排行榜

# Admin
GET    /admin/nfts                 # NFT 管理列表
POST   /admin/nfts/batch-import    # JSON 批量导入 NFT
PUT    /admin/packs/{id}           # 修改盲盒配置
PUT    /admin/buyback/{id}/approve # 审核回购
PUT    /admin/orders/{id}/status   # 更新订单状态
```
