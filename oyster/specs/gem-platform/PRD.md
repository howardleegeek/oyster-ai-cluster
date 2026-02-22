# GEM Platform - Product Requirements Document (RWA版)

> 版本: 2.0 | 更新日期: 2026-02-14 | 状态: 正式发布

---

## 1. 产品定位与愿景

### 1.1 产品定义

**GEM Platform** 是一个 RWA（Real World Assets）开宝与交易平台，每个 NFT 代表对真实资产（收藏卡片）的可兑付权利凭证，并与 Vault 实物库存强绑定。

### 1.2 核心壁垒

不是"开宝"本身，而是以下能力的组合：

1. **确权 + 在库证明** - 实物资产存在且可验证
2. **可验证随机性** - 开宝概率公开且可审计
3. **兑付SLA** - 明确的物流、鉴定、时效承诺
4. **回购/流动性机制** - 85%-90% 回购保证

### 1.3 用户信任模型

用户愿意付溢价，是因为平台能做到：

- ✅ 开宝概率公开且可验证（Provably Fair）
- ✅ 实物资产存在且可查（Proof-of-Reserve）
- ✅ 兑付明确（费用、时效、物流、保险、争议处理）

---

## 2. 核心功能模块

### 2.1 Pack 盲盒系统

#### 2.1.1 产品概念升级：Drop / Pool / Mint Policy

| 概念 | 定义 |
|------|------|
| **Drop** | 发行批次，同一 Pack 在不同 Drop 的卡池、概率、库存可能不同 |
| **Pool** | 卡池资产范围（哪些卡、grade、认证编号区间）、库存数量、锁定规则 |
| **Mint Policy** | 开宝后立刻 mint？还是先生成 off-chain 结果再 mint？ |

#### 2.1.2 Pack 品类

- Pokemon
- Baseball (MLB)
- Basketball (NBA)
- Football (NFL)
- One Piece
- Yu-Gi-Oh!

#### 2.1.3 Pack 等级与价格

| 等级 | 价格 | Buyback比例 |
|------|------|-------------|
| STARTER | $25 | 85% |
| ROOKIE | $25 | 85% |
| PRO | $100 | 85% |
| ELITE | $50 | 85% |
| LEGEND | $250 | 90% |
| PLATINUM | $500 | 90% |
| SEALED | $100 | 85% |

#### 2.1.4 稀有度体系

- N (Normal)
- VV (Very Rare)
- SSR (Super Rare)
- SSR+
- XR
- Legendary

#### 2.1.5 开宝公平性（必须可审计）

```typescript
interface PackOpenResult {
  opening_id: string;
  pack_id: string;
  drop_id: string;
  odds_version: string;        // 概率版本锁定
  randomness_proof: string;    // VRF 证明或 commit-reveal hash
  result_hash: string;         // 结果哈希（可验证）
  revealed_items: RevealedItem[];
  created_at: string;
}
```

**关键机制：**

1. **可验证随机性**
   - 接入 Solana VRF 或 commit-reveal 机制
   - 随机性证明与开宝结果关联

2. **概率披露与版本锁定**
   - 每个 Pack 必须有 `odds_version`
   - 各稀有度概率、卡池列表 hash
   - 发售后不能改概率；如需更改必须新建 Drop

3. **开宝记录可追溯**
   - 用户"My Openings"页面
   - 每次开宝包含：时间、Pack ID、随机性证明链接、结果、对应实物资产状态

#### 2.1.6 API Endpoints

```
GET    /api/drops                 - 列出所有 Drop（展示概率、卡池 hash、剩余量）
GET    /api/drops/{id}           - Drop 详情
GET    /api/packs                 - 列出所有 Pack
GET    /api/packs/{id}           - Pack 详情
GET    /api/packs/{id}/odds      - 概率披露
POST   /api/packs/purchase       - 购买 Pack
POST   /api/packs/open           - 开宝（返回 randomness_proof、odds_version、result_hash）
GET    /api/openings             - 用户开宝记录
POST   /api/packs/buyback       - 回购申请
```

---

### 2.2 Marketplace 交易市场

#### 2.2.1 订单形态

| 类型 | 描述 |
|------|------|
| **Listing** | 挂单出售 |
| **Offer** | 求购报价 |
| **Auction** | 拍卖（英式） |
| **Bulk List** | 批量上架 |
| **Bulk Buy** | 批量购买 |

#### 2.2.2 手续费

- 买家手续费: 2%
- 卖家版税: 1%

#### 2.2.3 信息透明度

- 最近成交价
- 7D/30D 成交量
- 地板价

#### 2.2.4 资产详情页（必须同时展示）

- NFT 信息（链上）
- 实物信息（vault）
- 是否可兑付、兑付费用预估、预计发货时效

#### 2.2.5 API Endpoints

```
POST   /api/market/orders           - 挂单
GET    /api/market/orders           - 订单簿
DELETE /api/market/orders/{id}      - 撤单
POST   /api/market/buy              - 购买
POST   /api/market/offer            - 求购报价
POST   /api/market/auction         - 创建拍卖
GET    /api/market/history          - 交易历史
GET    /api/market/assets/{id}     - 资产详情（NFT + 实物 + 兑付）
```

---

### 2.3 Vault 物理存储

#### 2.3.1 实物资产证据链（每个资产必须有以下字段）

```typescript
interface RwaAsset {
  id: string;
  
  // 资产指纹
  cert_provider: string;      // PSA/BGS/CGC 等
  cert_number: string;        // 证书编号
  grade: string;             // 评级分数
  set: string;               // 系列
  card_no: string;           // 卡片编号
  
  // 多角度高清图
  images: string[];          // 正反、编号特写
  
  // 入库证据
  checkin_at: string;
  checkin_operator: string;
  checkin_photos: string[];
  weight_scan_record?: string;
  
  // 保险与责任
  insured: boolean;
  insurance_policy_no?: string;
  insurance_amount?: number;
  
  // 状态
  status: 'stored' | 'reserved' | 'shipping' | 'shipped' | 'redeemed';
  
  // 位置
  shelf: string;
  box: string;
  position: string;
}
```

#### 2.3.2 Proof-of-Reserve（在库证明）

**实现方案：**

1. 每日/每周生成一次**库存 Merkle Root**（包含所有在库可兑付资产的哈希集合）
2. Root 上链或公开存档
3. 用户可验证：自己的 NFT claim 是否包含在某期 PoR 里

**API:**

```
GET    /api/por/latest              - 最新 PoR root
GET    /api/por/{timestamp}        - 历史 PoR
GET    /api/por/verify/{nft_id}   - 验证 NFT 是否在 PoR 中
```

#### 2.3.3 状态管理

- stored: 已入库
- reserved: 预留中
- shipping: 发货中
- shipped: 已发出
- redeemed: 已兑付

#### 2.3.4 API Endpoints

```
POST   /api/vault/checkin           - 卡片入库
GET    /api/vault/items             - 库存列表
GET    /api/vault/items/{id}        - 详情
PUT    /api/vault/items/{id}/status - 更新状态
GET    /api/assets/{id}             - RWA 资产详情
```

---

### 2.4 Redemption 兑付

#### 2.4.1 流程状态

```
PENDING → VERIFIED → SHIPPING → DELIVERED
PENDING → REJECTED
PENDING → CANCELLED
```

#### 2.4.2 成本拆分（必须明确）

| 费用类型 | 说明 |
|----------|------|
| 鉴定费 | 可选，默认 $5 |
| 包装费 | 固定 $2 |
| 运费 | 按国家/地区/重量阶梯 |
| 保险费 | 可选 |
| 关税/清关 | 国际单责任归属 |

#### 2.4.3 异常路径（必须支持）

- 地址校验失败
- 用户未支付运费/补差
- 海关退回
- 物流丢失/破损 → 理赔流程
- 用户拒收 → 退库与再次上架规则
- 鉴定不通过 → 退款/换货/回库规则

#### 2.4.4 API Endpoints

```
POST   /api/redemption/requests              - 创建兑换请求
GET    /api/redemption/requests              - 列表
GET    /api/redemption/requests/{id}         - 详情
GET    /api/redemption/requests/{id}/tracking - 物流追踪
POST   /api/redemption/requests/{id}/cancel  - 取消
POST   /api/redemption/requests/{id}/verify  - 鉴定确认（管理端）
POST   /api/redemption/requests/{id}/ship    - 发货（管理端）
```

---

### 2.5 回购系统（Buyback）

#### 2.5.1 回购规则（必须明确）

```typescript
interface BuybackPolicy {
  id: string;
  
  // 回购基准
  price_type: 'pack_price' | 'nft_floor' | 'platform_index';
  
  // 回购窗口
  window_days: number;           // 购买后多少天内可回购
  cooldown_hours: number;        // 购买后冷却时间
  
  // 限额
  daily_limit_per_user: number;
  total_daily_limit: number;
  
  // 回购比例
  buyback_rate: number;          // 0.85 或 0.90
  
  // 适用范围
  applicable_packs: string[];    // 适用 Pack 列表
  requires_unredeemed: boolean;  // 是否要求未兑付
}
```

#### 2.5.2 回购资金池（Buyback Reserve）

- 每次售包抽取 X% 进入准备金
- Dashboard 展示准备金覆盖率指标
- 动态报价系统（RFQ），但承诺最低底线

#### 2.5.3 API Endpoints

```
POST   /api/buyback/quote              - 报价（先报价再确认）
POST   /api/buyback/request             - 申请回购
GET    /api/buyback/requests            - 回购请求列表
GET    /api/buyback/policy              - 当前回购政策
GET    /api/buyback/reserve             - 准备金状态
```

---

### 2.6 Referral 推荐系统

#### 功能

- 推荐码生成
- 推荐奖励（折扣/积分）
- 推荐统计

#### API Endpoints

```
POST   /api/referral/code              - 生成推荐码
GET    /api/referral/stats             - 推荐统计
GET    /api/referral/rewards           - 奖励列表
```

---

### 2.7 Leaderboard 排行榜

#### 排行维度

- 收藏总值
- 开盒数量
- 交易次数
- 推荐人数

#### 时间周期

- 每周
- 每月
- 全部时间

---

### 2.8 Admin Dashboard

#### 功能

| 模块 | 功能 |
|------|------|
| Pack 管理 | CRUD、上架/下架、概率配置、Drop 管理 |
| 用户管理 | 冻结、VIP、查看详情、KYC 状态 |
| 订单管理 | 查看、处理、手动操作 |
| Vault 库存 | 批量导入、统计、位置调整 |
| 财务管理 | 收入、支出、准备金、报表导出 |
| 营销活动 | 促销活动、Buyback BOOST、奖励配置 |
| 系统配置 | 手续费、版税、Stripe/API 配置 |
| 操作日志 | 审计日志、权限分级 |

#### 权限分级

- 超级管理员
- 运营管理员
- 财务管理员
- 只读用户

---

## 3. 账户与支付

### 3.1 账户等级

| 等级 | 描述 |
|------|------|
| 游客 | 邮箱登录 + 托管钱包（MPC） |
| 钱包用户 | Phantom / Solflare 登录 |
| 完整用户 | KYC + 法币支付 + 提现 |

### 3.2 支付方式

| 方式 | 状态 |
|------|------|
| Phantom (SOL) | ✅ 已实现 |
| USDC | ✅ 已实现 |
| Stripe (信用卡) | ⏳ 待实现 |
| 邮箱登录 + 托管钱包 | ⏳ 待实现 |

### 3.3 KYC/AML 触发条件

- 购买达到阈值
- 回购达到阈值
- 提现达到阈值
- 兑付达到阈值

---

## 4. 合规与风控

### 4.1 地区限制

- 预留 geo-block 能力
- 年龄确认门槛

### 4.2 赔率披露

- 明确概率展示
- 期望值区间计算
- 限购/冷却/风控策略

### 4.3 安全

- 智能合约第三方审计
- Treasury 多签
- 管理后台操作审计日志

---

## 5. 技术架构

### 5.1 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React + TypeScript + Vite + Tailwind CSS |
| 后端 | FastAPI + SQLAlchemy + MySQL + Redis |
| 区块链 | Solana + Phantom Wallet |
| 支付 | Stripe（待实现） |

### 5.2 API 规范

- 鉴权：JWT / 钱包签名（Sign-In with Wallet）
- 分页、排序、过滤统一格式
- 幂等键：购买/开宝/回购/兑付请求必须幂等
- 统一错误码与可观测性（trace_id）

---

## 6. 数据模型

### 6.1 核心实体

| 实体 | 描述 |
|------|------|
| Drop | 发行批次 |
| Pool | 卡池与库存集合 |
| OddsVersion | 概率版本 |
| RwaAsset | 实物资产主表（证据链字段） |
| Claim | NFT 与实物资产/兑付权的绑定关系 |
| ProofOfReserveSnapshot | 在库证明快照 |
| BuybackQuote | 回购报价 |
| BuybackReserve | 回购准备金 |

---

## 7. 验收标准

### Phase 1 - 核心功能 (P0)

- [ ] Pack 购买和开盒
- [ ] 开宝可展示概率版本与随机性证明
- [ ] 任何一次开宝可复验结果
- [ ] NFT 可映射到明确的 Claim（兑付权）
- [ ] 钱包连接（Phantom）

### Phase 2 - Marketplace (P0)

- [ ] 挂单/撤单/购买
- [ ] 手续费计算正确
- [ ] 资产详情页展示 NFT + 实物 + 兑付信息
- [ ] Offer / Auction 支持

### Phase 3 - 物理服务 (P0)

- [ ] Vault 资产证据链字段完整
- [ ] 卡片可入库
- [ ] Redemption 兑换流程完整
- [ ] 物流追踪可用
- [ ] 异常路径处理（丢件/退回/拒收/理赔）

### Phase 4 - 回购 (P0)

- [ ] 回购规则可配置（条件/限额/窗口/资金池）
- [ ] 回购报价机制
- [ ] 准备金指标展示

### Phase 5 - 用户激励 (P1)

- [ ] Referral 推荐系统
- [ ] Leaderboard 排行
- [ ] Stripe 支付

### Phase 6 - 运营 (P1)

- [ ] Admin Dashboard 完整功能
- [ ] 操作审计日志
- [ ] 权限分级
- [ ] PoR（在库证明）第一版

### Phase 7 - 合规 (P2)

- [ ] KYC/AML 触发机制
- [ ] 地区限制
- [ ] 智能合约审计

---

## 8. 路线图

### v1.0 (MVP) - 已完成 ✅

- Pack 购买/开盒
- 基础 Marketplace
- 钱包连接

### v1.1 - 本次升级 ⏳

- Drop/Pool/OddsVersion 体系
- Provably Fair（VRF/Commit-Reveal）+ 开宝记录页
- 回购规则落地（窗口/限额/资金池/报价机制）
- Vault 资产证据链字段
- Marketplace 资产详情透明化

### v1.2 - Phase B

- 邮箱登录 + 托管钱包
- Stripe/法币支付 + 基础 KYC/AML
- Offer / 批量操作
- PoR（在库证明）第一版

### v1.3 - Phase C

- 运营系统：任务、等级、空投、活动引擎
- 资产定价指数/估值模型
- 国际物流与清关流程
- 第三方审计/保险合作

---

## 9. 参考

- Phygitals: https://www.phygitals.com
- Phygitals Docs: https://phygitals.gitbook.io/docs
