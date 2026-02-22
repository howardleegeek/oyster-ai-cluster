# ClawVision Business Insight 矩阵

## Executive Summary
ClawVision 的机会是把 `30K+` 设备（累计 `$4M`）和 `70K` DePIN 用户，从硬件交易升级为持续数据收入。DePIN `2025.9` 市值 `>$19B`、`2026.1` 月收入 `$150M`、`2025` 私募约 `$1B`，估值回到 `10-25x revenue`。若未来 12 个月跑通 API 订阅和行业合同，ClawVision 可从“设备公司”切换为“Spatial AI 数据平台”，估值区间 `US$180M-420M`。

## 1. 市场地图 (Market Map)

### 1.1 赛道定位
- **Where we play**: `DePIN × Spatial AI × Phone Fleet`，定位是世界数据层，不是单点地图产品。
- **市场规模**: 自动驾驶 `2026: $69.5B → 2033: $103.8B`；自动驾驶软件 `2024: $1.8B → 2035: $7.0B`；AV 传感器 `2025: $5.98B → 2035: $108.41B`。
- **阶段判断**: DePIN 倍数回到 `10-25x`，核心从讲故事转为签单、续费、毛利。
- **我们的起点**: 已有 30K+ 设备和 70K 用户，具备直接商业化条件。

### 1.2 竞争格局矩阵
| 维度 | ClawVision | Hivemapper | World Labs | Planet Labs | Mapillary/Meta | Helium | Render |
|------|-----------|-----------|-----------|------------|---------------|--------|--------|
| 赛道定位 | Phone vision + Spatial API | Dashcam map DePIN | LWM + World API | 卫星遥感 | 众包街景 | 去中心化无线 | 去中心化 GPU |
| 网络规模 | 30K+ 设备，70K 用户 | 100K+ 贡献者 | 未披露 | 卫星星座 | 大规模 UGC | 115K hotspots, 1.9M DAU | 全球节点网络 |
| 已披露收入 | 累计 `$4M`（硬件） | FY25 `$18M` | 未披露 | 上市持续收入 | 未单列 | `2026.1` 月 `$24M` | `2026.1` 月 `$38M` |
| 融资/估值 | 待下一轮 | `2025.10` 融资 `$32M` | `2026.1` 估值 `$5B` 融资中，累计 `$230M` | 二级市场定价 | Meta 支持 | Token 估值体系 | Token+业务双驱动 |
| 数据采集方式 | 手机/眼镜终端 | 专用 dashcam | 模型+多源数据 | 卫星采集 | UGC 上传 | 热点部署 | GPU 供给 |
| 数据新鲜度 | 秒到分钟（1fps） | 路测中高频 | 依场景 | 天/周级 | 非连续 | 实时网络状态 | 实时算力状态 |
| 覆盖与精度 | H3 + 多模态上下文 | 道路场景强 | 3D 语义强 | 广域强，地面弱 | 街景强 | 非视觉空间 | 非视觉空间 |
| 商业模式 | 硬件+API+订阅 | `$19/月`+合同 | API/平台合作 | 数据订阅 | 平台导流 | 使用费+Token | 算力计费+Token |
| Token 经济 | `$WORLD` | `$HONEY` | 非主叙事 | 无 | 无 | HNT | RNDR |
| API/团队能力 | 全栈可控 | 地图运营成熟 | 顶级研究团队，`World API` 已发 | 政企销售强 | 平台化运营 | 基建运营强 | HPC 平台化 |

**结论**: Hivemapper 是直接替代，World Labs 是估值锚，Helium/Render 是 DePIN 变现上限参照。ClawVision 的主战场是“低成本采集 + 快速 API 产品化”。

### 1.3 产业链位置
ClawVision 四段都可覆盖：采集靠终端网络，处理靠 H3/relay，分发靠 OpenClaw，应用切入 AV/城市/物流。短期应优先做强“处理+分发”。

## 2. 竞争优势分析 (Moat Analysis)

### 2.1 已有护城河
- `30K+` 设备 + `70K` 用户，网络冷启动已完成。
- 硬件累计 `$4M`，交付和转化能力已验证。
- 多产品线（UBS/Puffy/ClawGlasses）带来更广采集场景。
- VisionClaw + Oysterworld + OpenClaw 形成 edge 到 API 的闭环。

### 2.2 可建护城河
- **Freshness Moat**: 分钟级更新 SLA 合同化。
- **Quality Moat**: cell 级评分 + 分层定价。
- **Distribution Moat**: free tier + SDK 做开发者飞轮。
- **Compliance Moat**: 匿名化与区域合规前置。

### 2.3 风险/短板
- 1fps 对部分高精场景不够，需要后处理与多源融合。
- ToB 销售与客户成功体系仍需补齐。
- World Labs 抬高客户预期。
- 收入结构仍偏硬件，订阅化速度决定估值上限。

## 3. 商业模式矩阵 (Revenue Model)

### 3.1 当前收入
- 已实现硬件收入 `$4M`（`30K+` 设备），单设备历史收入约 `$133`。
- 70K DePIN 用户是待货币化资产，目标是迁移到可重复收入。

### 3.2 潜在收入线

| 收入线 | 描述 | TAM | 时间线 | 难度 |
|------|------|-----|-------|------|
| Spatial Query API | `world.query()` 按调用计费 | `$54M-$560M` | 0-3月 | 中 |
| HD Map Freshness 订阅 | 重点区域分钟级更新 + SLA | `$1B-$3B` | 3-6月 | 高 |
| 行业数据合同 | 物流/城市/导航企业年度合同 | `$300M-$1B` | 3-9月 | 中高 |
| AI 训练数据授权 | 给 VLM/LWM/机器人训练与评测 | `$500M+` | 3-12月 | 中高 |
| 企业看板订阅 | 零售/保险/城市洞察看板 | `$100M-$300M` | 2-6月 | 中 |
| `$WORLD` 结算手续费 | 数据交易与返佣抽成 | 对应 DePIN 年化 `$1.8B` 流量池 | 6-12月 | 中高 |

### 3.3 定价策略建议
- 三层套餐：`Developer / Growth / Enterprise`。
- 双轨计费：按调用 + 按区域包月。
- 价值定价：按 freshness、coverage、quality 收费。

## 4. 客户矩阵 (Customer Segments)

| 客户群 | 需求 | 付费意愿 | 竞品对比 | 我们的优势 |
|------|------|---------|---------|-----------|
| Robotaxi/ADAS | 道路变化与 HD map 更新 | 高 | Hivemapper 先发 | 多终端入口 + 低边际采集成本 |
| 地图与导航平台 | 高频增量更新 | 中高 | Hivemapper 直接竞争 | 非道路场景覆盖更广 |
| 城市治理部门 | 设施异常与路网状态 | 中 | Planet 广域强但地面细节弱 | 地面视角 + 高频更新 |
| 物流与本地服务 | 可达性与路径效率 | 中高 | 传统地图更新慢 | 分钟级 feed 可直接优化运营 |
| AI/机器人公司 | 真实世界训练与评测数据 | 中高 | World Labs 品牌与研究强 | 真实终端数据持续供给能力 |

## 5. 估值参考框架

### 5.1 可比公司法
- Hivemapper：FY25 `$18M` + `2025.10` 融资 `$32M`，验证地图合同路径。
- World Labs：`2026.1` 估值 `$5B` 融资中，体现空间智能溢价。
- Helium/Render：`$24M/$38M` 月收入，证明 DePIN 可做高现金流。

### 5.2 收入倍数法
- 当前可用倍数：`10-25x revenue`（行业回归基本面后区间）。
- 12个月情景：
- 保守：可重复收入 `$8M-$12M`，估值 `US$80M-$144M`
- 基准：可重复收入 `$15M-$22M`，估值 `US$180M-$396M`
- 进取：可重复收入 `$25M-$30M`，估值 `US$375M-$600M`

### 5.3 网络价值法 (DePIN 特有)
- 简式：`Network Value = Active Devices × Data Yield × Monetization × Retention`
- 以 `30K` 设备、每设备年收益 `$200-$500` 估，网络收益潜力约 `$6M-$15M/年`。
- **合理估值区间**：当前建议 **`US$180M-$420M`**；若 6-12 月内拿下 2-3 个标杆合同，可上探 **`US$420M-$600M`**。

## 6. 战略路径 (Go-to-Market)

### 6.1 短期 (0-3月)
- 发布商业可用 `world.query()` v1（覆盖/新鲜度/变化检测）。
- 落地 3 个 design partners（AV、物流、城市）。

### 6.2 中期 (3-6月)
- 把 design partner 转为付费 pilot，形成 2 个标准合同模板。
- 上线区域包月 + SLA 定价，提升毛利与可预测收入。

### 6.3 长期 (6-12月)
- 从 API 升级为行业方案（AV/城市/零售 feed）。
- 打通 `$WORLD` 在数据交易与返佣中的结算闭环。

## 7. 关键洞察 (Key Insights)

1. **估值逻辑已变**：续费收入比叙事更重要。
2. **最大护城河是已部署分发网络**：30K+ 设备可快速验证。
3. **与 Hivemapper 的差异在成本和场景宽度**。
4. **对抗 World Labs 需用 KPI，不是概念**。
5. **12 个月窗口期必须先合同化，再生态化**。

## 8. 行动建议 (Action Items)

1. **P0 / 30天**：周更三项 North Star（可计费覆盖、SLA、可重复收入占比）。
2. **P0 / 60天**：签下 3 个 design partners，全部绑定转付费 KPI。
3. **P0 / 90天**：上线三档商业套餐和标准 SLA 合同。
4. **P1 / 90天**：完成 cell 级质量评分并绑定价格。
5. **P1 / 持续**：每月更新 Hivemapper/World Labs 战情并调价。
6. **P2 / 6-12月**：把 `$WORLD` 接入数据交易结算，目标可重复收入超过硬件收入。

---

## 9. 赛道卡位战略 (Category Design)

### 9.0 赛道全景 — 2026年"世界模型"五分天下

```
┌──────────────────────────────────────────────────────────────────┐
│                    "World Model" 赛道全景                         │
├──────────────┬───────────────┬──────────────┬───────────────────┤
│  合成世界     │  道路地图      │  3D 数字孪生  │ ??? 真实世界索引  │
│  World Labs  │  Hivemapper   │  Niantic     │  ClawVision       │
│  AMI Labs    │  Bee Maps     │  Spatial     │                   │
│              │               │              │                   │
│  文字→3D     │  dashcam→HD   │  扫描→数字孪生│  phone fleet→     │
│  $5B est.    │  $32M raised  │  $250M       │  world.query()    │
│  $1.20/生成  │  $19/月订阅   │  企业定制     │  $0.01/查询       │
│              │               │              │                   │
│  输出:虚拟世界│  输出:道路图层 │ 输出:cm级3D   │  输出:实时事件流  │
│  用户:游戏/   │  用户:AV/     │ 用户:制造/    │  用户:全行业      │
│  影视/机器人  │  导航/物流    │ 物流/建筑     │  AI/城市/零售/AV  │
└──────────────┴───────────────┴──────────────┴───────────────────┘

投资者: Cisco/Nvidia/AMD   Multicoin/a16z    Scopely $50M     → 你们 ←
估值锚: $5B (pre-rev)      ~$200M (有收入)   $250M (spin-off) 目标: $80-150M
```

### 9.0.1 新玩家速查

**Niantic Spatial** (2025.5 从 Niantic 分拆)
- 资金: $250M ($200M Niantic 资产 + $50M Scopely)
- 创始人: John Hanke (Google Earth/Maps 联创)
- 数据: **300 亿张带位姿图像** (Pokemon Go 用户积累)
- 产品: Capture → Reconstruct → Localize → Understand
- 精度: **厘米级** 定位 (VPS)
- 客户: 仓库/娱乐/制造 (企业)
- 弱点: 数据是历史扫描的，不是实时的；没有 DePIN token 激励

**AMI Labs** (LeCun 的新公司, 2026.1)
- 融资: 寻求 €500M @ €3B 估值
- 方向: "World Models for AGI" — 学术路径
- 状态: Pre-launch，纯研发
- 与我们: 不同层 — 他们做底层模型，我们做数据供给

**Mapbox GeoAI** (2026 趋势)
- 已有: 地图 API 龙头，开发者生态成熟
- 新动向: 2026 押注 "agents + MCP + live data"
- 与我们: 潜在合作方 (数据供给) 也是竞争 (如果他们自建采集)

### 9.0.2 我们要卡的赛道: "Real-Time World Index"

**赛道定义**: 从真实世界持续采集的多模态事件流，按空间-时间索引，通过 API 供任何应用查询。

**为什么这条赛道还没人卡住:**

| 玩家 | 为什么不是他们 |
|------|--------------|
| World Labs | 合成世界，不碰真实数据采集 |
| Hivemapper | 只有道路，只有视觉，无音频，无全场景 |
| Niantic Spatial | 历史扫描数据，不是实时流；没有 token 激励 |
| Planet Labs | 卫星，天/周级更新，无地面细节 |
| Mapillary/Meta | UGC 众包，不连续，无 SLA |
| Google/Apple | 中心化，更新慢，不开放 API |

**ClawVision 能卡住的原因:**
1. **30K 设备已在手** — 不是计划，是事实
2. **1fps 连续流** — 不是快照，是事件流
3. **多模态** — 视觉 + 音频 + GPS + heading (Hivemapper 只有视觉)
4. **全场景** — 行人/室内/非道路 (Hivemapper 只有道路)
5. **DePIN 激励** — $WORLD token 驱动采集成本趋零
6. **API-first** — world.query() 对标 World Labs World API

### 9.0.3 赛道命名与叙事

**赛道名**: **Real-Time World Index** (RTWI)
- 对标 "Real-Time Bidding (RTB)" 在广告行业的定义力
- 简洁、技术感、可搜索

**一句话**: "World Labs generates synthetic worlds. ClawVision indexes the real one."

**投资人 pitch 版**: "我们不造世界，我们索引真实世界。30K 手机每秒一帧，H3 空间索引，world.query() API。Hivemapper 做道路，我们做全场景。Niantic 做 3D 扫描，我们做实时事件流。"

**开发者 pitch 版**: "一个 API 查询真实世界。哪个街区最拥挤？这个路口 10 分钟前什么样？某个区域有多少行人？world.query() 帮你回答。"

### 9.0.4 卡位动作清单 (先做好往后赞)

**占名 (本周)**:
- [x] clawvision.org 上线 — 域名+网站+品牌占位
- [ ] Twitter/X: @ClawVision 占号 + 发 thread "Introducing Real-Time World Index"
- [x] GitHub: `howardleegeek/world-index-sdk` 占仓库名 (后续 transfer 到 oysterlabs org)
- [ ] Product Hunt: 提前占坑 "ClawVision — Real-Time World Index API"

**定义权 (30 天)**:
- [x] 发一篇 blog/文章: "Why the world needs a Real-Time World Index" → blog.html
- [x] 写一份 whitepaper 摘要页放 clawvision.org/whitepaper → whitepaper.html
- [ ] OC-content 在 4 个 Twitter 账号同步 RTWI 叙事

**技术占位 (60 天)**:
- [ ] world.query() API v1 上线 — 哪怕只有 read-only + demo 数据
- [ ] Python SDK `pip install clawvision` 占包名
- [ ] npm `@clawvision/sdk` 占包名
- [ ] OpenAPI spec 公开 → 被 API 目录收录 (RapidAPI, APIs.guru)

**生态占位 (90 天)**:
- [ ] Hackathon 赞助/参加 — 用 RTWI 做赛题
- [ ] 1-2 个 demo app 展示: "用 world.query() 能做什么"
- [ ] 找 3 个 design partner 用 RTWI 叙事签约

## 10. 定价与融资深挖

### 10.1 定价锚定：World Labs 给了我们天然参照

World Labs `World API` 定价已公开 (`2026-01-21`):
- 信用体系: `$1 = 1,250 credits`
- Standard 生成: `1,500-1,600 credits/次` ≈ **$1.20-$1.28/次**
- Draft 生成: `150-250 credits/次` ≈ **$0.12-$0.20/次**
- 无月费、无限制、credits 不过期

**对我们的意义**: World Labs 做的是 **"从文字/图片→生成3D世界"**（合成），我们做的是 **"从真实世界→结构化查询"**（采集+索引）。两个方向互补，但定价可以锚定：
- `world.query()` 查询定价建议: **$0.01-$0.05/次**（比 World Labs 便宜 25-100x）
- 理由: 我们是"读"操作（查覆盖、查事件），World Labs 是"写"操作（生成世界），边际成本完全不同
- **叙事角度**: "World Labs 合成世界，ClawVision 索引真实世界" — 这不是竞争，是互补层

### 10.2 Hivemapper 客户即我们的客户

Bee Maps 已签约客户（公开信息）:
- **HERE Technologies** — 全球 Top 3 地图商
- **TomTom** — 欧洲最大地图商
- **Mapbox** — 开发者地图 API 领导者
- **Trimble** — 建筑/农业/物流
- **Lyft** — 出行平台
- **大众 ADMT** — 2026 无人出租车

**战术意义**:
1. 这些客户**已经验证**了 DePIN 地图数据的付费意愿
2. 他们买 Hivemapper 的原因是 **freshness**（5-6x faster than Google/Apple）
3. 我们的差异化: Hivemapper 只有道路视角 (dashcam)，ClawVision 有**全场景**（行人、室内、非道路区域）
4. **行动**: 直接联系 HERE/TomTom/Mapbox 的数据采购团队，pitch "complementary to dashcam coverage"

### 10.3 收入路径的诚实审视

之前 Business Model Canvas (2025年2月) 的预测:
```
2025: $800K → 2026: $3.8M → 2027: $11M → 2028: $50M
单设备: $10/月收入, $5/月成本, 50% 毛利
目标: Q4 2025 $300K MRR ($3.6M ARR)
```

**现实 check (2026年2月)**:
- 设备卖了 30K+，但可重复收入 ≈ $0（还没有 API 收入）
- Q4 2025 $300K MRR 目标**未达成**
- $10/月/设备的假设需要 API 产品 live 才能验证

**修正后的 12 个月目标**:
| 阶段 | 时间 | MRR 目标 | 来源 |
|------|------|---------|------|
| API 上线 | M1-M3 | $0-$10K | Free tier + 少量付费试用 |
| Design Partner | M3-M6 | $10K-$50K | 2-3 个 pilot 合同 |
| 首个标杆合同 | M6-M9 | $50K-$150K | 1 个年框 + 多个 Growth 订阅 |
| 规模化 | M9-M12 | $150K-$300K | 3-5 个合同 + 开发者长尾 |

**年底目标 ARR: $1.8M-$3.6M**（比之前的 $11M 保守，但更可信）

### 10.4 融资时机与估值叙事

**当前状态**: 第一轮机构融资，`investor-materials-2026-02/` 已在准备中

**两种融资叙事，选一个**:

**叙事 A: "DePIN Spatial AI 基础设施"**
- 对标 Hivemapper ($32M raise, ~$150-200M implied valuation)
- 我们的优势: 30K 设备 vs 100K dashcam，但场景更广
- 合理 ask: **$5-10M raise @ $50-80M valuation** (pre-revenue DePIN + hardware traction)
- 适合: Multicoin, Framework, HashKey, Solana Ventures

**叙事 B: "Phone Fleet × World Model"**
- 对标 World Labs ($5B valuation, but pre-revenue)
- 我们的优势: 已有分发网络和硬件收入
- 合理 ask: **$10-15M raise @ $80-150M valuation** (网络效应溢价)
- 适合: a16z crypto, Paradigm, tier-1 通才 VC

**建议选 A 做底，B 做叙事天花板**。先拿 DePIN VC 的钱（他们懂 token + hardware），用合同进展抬估值到 B 区间。

### 10.5 $WORLD Token 战略定位

之前 Tokenomics 设计:
```
总供给: 1B WORLD
分配: 40% 社区挖矿, 20% 团队, 20% 投资者, 15% 国库, 5% 流动性
目标 FDV: $30-50M
```

**与 ClawVision 商业模式的融合**:
- **采集激励**: 设备上报 1fps frame → earn WORLD（替代现金补贴）
- **数据消费**: API 调用可用 WORLD 支付（折扣 vs USD）
- **质量奖励**: cell 质量评分高 → 额外 WORLD 奖励
- **治理**: WORLD 持有者投票决定区域优先级

**关键决策**: Token launch 放在融资之前还是之后？
- **建议: 融资之后**。先拿 equity round 定价，再做 token，避免 SEC 风险和估值混乱
- Hivemapper 也是先融 $32M equity，$HONEY 作为独立网络激励层

### 10.6 竞品动态预警矩阵

| 事件 | 影响 | 我们的应对 |
|------|------|----------|
| Hivemapper 拿下更多 Tier-1 地图商 | 证明市场但抬高竞争 | 加速 API 上线，打"全场景"差异 |
| World Labs 发布免费 tier | 抬高客户对 3D 的预期 | 定位互补 "合成 vs 真实"，做集成 demo |
| Helium/Render 月收入持续破纪录 | DePIN 估值预期上升 | 融资叙事加入 DePIN 收入参照 |
| Google/Apple 加速街景更新 | 中心化替代压力 | 强调去中心化 + 隐私 + 成本优势 |
| Meta 开放更多 Ray-Ban API | VisionClaw 能力扩展 | 快速迭代 VisionClaw → ClawGlasses |
| Solana DePIN 生态基金发新 RFP | 潜在资金来源 | OC-bd 监控 + 快速响应 |

## 11. 90 天作战计划 (War Plan)

### 月度里程碑

**M1 (2月): "让世界看到"**
- [x] clawvision.org 上线 (Landing + Map + API Portal + Blog + Whitepaper)
- [x] Seed 数据灌入 — 51 nodes, 543 events, 443 cells, 32 cities
- [x] Business Insight 矩阵完成 (11 sections)
- [ ] Investor deck RTWI 升级版 (Codex 执行中)
- [ ] 确定融资 round size 和估值区间
- [x] x402 hackathon spec 完成 (specs/x402-hackathon-clawvision.md) — x402 middleware dispatched to Codex
- [ ] Solana AI hackathon (Feb 12) — 借势曝光

**M2 (3月): "让开发者用起来"**
- [ ] world.query() API v1 公开 (read-only endpoints)
- [ ] Developer free tier 上线 (1000 calls/day)
- [ ] Python SDK + JS SDK 发布
- [ ] Product Hunt launch → 目标 500+ upvotes
- [ ] 开始联系 HERE/TomTom/Mapbox 数据采购团队

**M3 (4月): "让钱进来"**
- [ ] 2-3 个 design partner 签约 (LoI 级别)
- [ ] Growth 套餐上线 ($99-499/月)
- [ ] 融资 first close
- [ ] $WORLD token 设计最终版 (不发，先定)
- [ ] MRR 目标: $5K-$10K（哪怕很小，证明可收费）
