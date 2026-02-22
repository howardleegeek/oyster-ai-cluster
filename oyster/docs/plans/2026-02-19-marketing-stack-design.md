# Marketing Stack Design v2 — MECE + Fallback

**Date:** 2026-02-19
**Approach:** A+B+C (Content Factory + Growth Loop + Platform Blitz)
**Principles:** MECE (互斥穷尽) + Fallback (每层降级) + 最大复用 + 轻量化
**Method:** Open-source assembly + Pomelli + bluesky-poster 公共层抽取 + dispatch 集群

---

## 设计原则

### MECE (Mutually Exclusive, Collectively Exhaustive)
每个模块只做一件事，模块间职责不重叠，合起来覆盖所有需求。
- 内容生成 ≠ 内容分发 ≠ 内容度量 — 三层分离
- 每个平台一个 adapter，共享公共层
- 数据只在一个地方存，其他模块通过 API 读

### Fallback (降级设计)
每个关键路径都有 Plan B，不依赖单点。
- LLM: Claude → Grok → 模板
- 发布: Queue+Worker → 直接 client.post()
- 分析: PostHog → Plausible → 手动 CSV
- 工作流: n8n → cron + CLI
- 素材: Pomelli → ALwrity → 模板

### 最大复用
bluesky-poster 已有 5,505 行生产代码，核心模块直接抽为跨平台公共层。

### 轻量化
先跑通再优化。每个工具最小部署，后续精简合并。

---

## 架构 (MECE 分层)

```
Layer 1: GENERATION (内容生成 — 互斥: 素材 vs 文字 vs 视频)
┌──────────┬───────────┬─────────────┐
│ Pomelli  │ ALwrity   │ LLM Client  │
│ 品牌素材  │ 长文/博客  │ 社交短文     │
│ + 视频   │ + SEO     │ (已有复用)   │
│ Fallback │ Fallback  │ Fallback    │
│ →ALwrity │ →LLM+模板  │ →模板库     │
└────┬─────┴─────┬─────┴──────┬──────┘
     │           │            │
Layer 2: ORCHESTRATION (编排 — 单一入口)
┌────▼───────────▼────────────▼──────┐
│              n8n                    │
│  工作流引擎 / 所有工具的连接器        │
│  Fallback: cron + CLI 直接调用      │
└────┬───────┬───────┬───────┬───────┘
     │       │       │       │
Layer 3: DISTRIBUTION (分发 — 每平台一个 adapter, MECE)
┌────▼──┐┌───▼──┐┌───▼───┐┌──▼─────┐
│Common ││      ││       ││        │
│Layer  ││ More ││       ││        │
│(复用) ││ ...  ││       ││        │
├───────┤├──────┤├───────┤├────────┤
│Twitter││Blusky││Listmnk││ Postiz │
│Poster ││Poster││ Email ││LinkedIn│
│(已有) ││(已有)││(新部署)││Discord │
│       ││      ││       ││Reddit  │
│F:手动 ││F:手动││F:SMTP ││F:手动  │
└───┬───┘└──┬───┘└───┬───┘└───┬────┘
    │       │        │        │
Layer 4: MEASUREMENT (度量 — MECE: 产品/Web/SEO/社交)
┌───▼───┬───▼────┬───▼────┬───▼─────┐
│PostHog│Plausbl │SerpBer │ Obsei   │
│产品    │Web     │SEO     │社交聆听  │
│分析    │分析    │追踪    │情感分析  │
│F:手动 │F:GA4   │F:手动  │F:手动   │
└───┬───┴───┬────┴───┬────┴───┬─────┘
    │       │        │        │
Layer 5: RELATIONSHIP (客户关系 — 单一数据源)
┌───▼───────▼────────▼────────▼─────┐
│            Twenty CRM              │
│   Lead → MQL → SQL → Customer     │
│   Fallback: SQLite + CSV export    │
└───────────────┬────────────────────┘
                │
Layer 6: CONTROL (总控)
┌───────────────▼────────────────────┐
│         ClawMarketing (已有)        │
│   596K 行代码 / 25 路由 / React UI  │
│   统一看板 + Campaign + 审批        │
└────────────────────────────────────┘
```

---

## 复用分析: bluesky-poster → 跨平台公共层

### 抽取到 `oyster/social/common/`

| 模块 | 来源 | 行数 | 跨平台用途 | 改动量 |
|---|---|---|---|---|
| `queue.py` | bluesky-poster | 404 | 通用任务队列 | 0 行 — 直接 symlink |
| `rate_limiter.py` | bluesky-poster | 94 | 通用限速 | ~10 行 — 参数化 timezone/caps |
| `quality_gate.py` | bluesky-poster | 231 | 通用内容质检 | 0 行 — 直接复用 |
| `llm_client.py` | bluesky-poster | 280 | 通用 LLM 调用 | 0 行 — 直接复用 |
| `content_db.py` | bluesky-poster | 457 | 通用内容追踪 | ~5 行 — 加 platform 字段 |
| `personas.py` | bluesky-poster | 569 | 通用人设系统 | 0 行 — 扩展新 persona |
| `content_templates.py` | bluesky-poster | 587 | 通用模板库 | 0 行 — 扩展新模板 |
| **小计** | | **2,622** | | **~15 行改动** |

### 各平台只写 Adapter (MECE)

| Adapter | 职责 | 预估行数 | 已有代码 |
|---|---|---|---|
| `twitter/adapter.py` | Twitter API 封装 | ~200 | twitter_poster.py 3,804 行可提取 |
| `bluesky/adapter.py` | AT Protocol 封装 | ~50 | client.py 270 行 ← 直接用 |
| `linkedin/adapter.py` | LinkedIn API 封装 | ~200 | linkedin-optimize 空项目 |
| `discord/adapter.py` | Discord Bot 封装 | ~150 | discord-admin 19 个 mjs 脚本 |
| `email/adapter.py` | Listmonk API 封装 | ~100 | 新建 |
| `reddit/adapter.py` | Reddit API 封装 | ~150 | 新建 |

**每个 adapter 接口统一:**
```python
class PlatformAdapter(Protocol):
    async def post(text, images=None) -> PostResult
    async def reply(text, parent_id) -> PostResult
    async def get_metrics(post_id) -> Metrics
    async def search(query, limit) -> list[Post]
```

### 复用节省量

| 项目 | 原计划 | 复用后 | 节省 |
|---|---|---|---|
| 社交分发层代码 | ~5,000 行新写 | ~700 行 adapter | **86%** |
| 内容引擎 | ~2,000 行新写 | 0 行 (直接用) | **100%** |
| 质量系统 | ~500 行新写 | 0 行 (直接用) | **100%** |
| LLM 集成 | ~500 行新写 | 0 行 (直接用) | **100%** |

---

## 现有代码资产盘点

| 系统 | 行数 | 状态 | 复用方式 |
|---|---|---|---|
| ClawMarketing | 596,649 | 25 路由在线 | 对接层 — 加 API connector |
| twitter-poster | 458,741 | 生产运行 | adapter 提取 |
| bluesky-poster | 5,505 | 生产运行 | 公共层抽取 + 直接用 |
| bluesky-automation | ~8,863 | 实验原型 | personas/engagement 已搬到 poster |
| discord-admin | ~4,067 (mjs) | 运行中 | JS adapter 封装 |
| article-pipeline | ~54,000 | 生产运行 | n8n workflow 接入 |
| engagement-farmer | ~5,600 | 生产运行 | 保持独立，n8n 触发 |

**总已有代码: ~1.13M 行** — 大部分只需要接入，不需要重写。

---

## 更新后的任务清单 (MECE)

### Wave 1: 基础设施 (并行, 无依赖)

**W1-A: 公共层抽取 — 8 tasks**
- A01: 创建 `oyster/social/common/` 目录结构
- A02: 抽取 queue.py → common/ (加 platform 参数)
- A03: 抽取 rate_limiter.py → common/ (参数化 timezone/caps)
- A04: 抽取 quality_gate.py → common/
- A05: 抽取 llm_client.py → common/
- A06: 抽取 content_db.py → common/ (加 platform 字段)
- A07: 抽取 personas.py → common/ (保留所有现有 persona)
- A08: 抽取 content_templates.py → common/ (保留所有现有模板)

**W1-B: 开源工具部署 — 12 tasks (每个工具 2 tasks: deploy + config)**
- B01: n8n Docker deploy on GCP
- B02: n8n SSL + admin + API credentials
- B03: PostHog Docker deploy on GCP
- B04: PostHog project setup (9 products)
- B05: Plausible Docker deploy on GCP
- B06: Plausible site setup (9 products)
- B07: Listmonk Docker deploy
- B08: Listmonk SMTP + list setup
- B09: Twenty CRM Docker deploy
- B10: Twenty CRM pipeline + fields setup
- B11: SerpBear Docker deploy
- B12: SerpBear domain + keyword setup (6 products)

**W1-C: Pomelli Brand DNA — 6 tasks**
- C01: Pomelli setup for ClawPhones
- C02: Pomelli setup for WorldGlasses
- C03: Pomelli setup for GEM Platform
- C04: Pomelli setup for ClawGlasses
- C05: Pomelli setup for OysterRepublic
- C06: Pomelli setup for getPuffy

**Wave 1 subtotal: 26 tasks, 全部可并行**

### Wave 2: 平台 Adapter + 工具对接 (依赖 Wave 1)

**W2-A: Platform Adapters — 6 tasks**
- D01: twitter/adapter.py (从 twitter_poster.py 提取)
- D02: bluesky/adapter.py (从 client.py 封装)
- D03: linkedin/adapter.py (新建, LinkedIn API)
- D04: discord/adapter.py (封装现有 mjs 脚本)
- D05: email/adapter.py (Listmonk API 封装)
- D06: reddit/adapter.py (新建, Reddit API)

**W2-B: n8n Workflow 连接 — 15 tasks**
- E01: n8n → Twitter Poster webhook
- E02: n8n → Bluesky Poster webhook
- E03: n8n → Listmonk email trigger
- E04: n8n → Postiz social schedule
- E05: n8n ← PostHog event webhook
- E06: n8n ← Plausible goal webhook
- E07: n8n ← SerpBear rank alert
- E08: n8n → Twenty CRM lead create
- E09: n8n: Pomelli asset → Directus → Postiz pipeline
- E10: n8n: Daily analytics digest → email
- E11: n8n: New subscriber → welcome sequence
- E12: n8n: Negative sentiment (Obsei) → alert
- E13: n8n: Content publish → social amplification
- E14: n8n: A/B test winner → auto-scale
- E15: n8n: Error/failure alerting

**W2-C: ClawMarketing 对接 — 12 tasks**
- F01: CM analytics router → PostHog API pull
- F02: CM analytics router → Plausible API pull
- F03: CM campaign router → n8n webhook trigger
- F04: CM content router → Pomelli asset import
- F05: CM scheduler → n8n workflow trigger
- F06: CM scout → Obsei data pull
- F07: CM accounts → Twenty CRM sync
- F08: CM frontend: unified analytics dashboard widget
- F09: CM frontend: social calendar widget
- F10: CM frontend: CRM pipeline widget
- F11: CM frontend: SEO rank widget
- F12: CM API auth layer for all external tools

**Wave 2 subtotal: 33 tasks, adapter 间可并行**

### Wave 3: 扩展能力 (依赖 Wave 2)

**W3-A: 高级工具部署 — 8 tasks**
- G01: Mautic Docker deploy + config
- G02: Mautic campaigns (welcome, launch, re-engage, newsletter)
- G03: Directus Docker deploy + schema
- G04: Directus editorial workflow + asset library
- G05: GrapesJS 集成到 ClawMarketing frontend
- G06: GrapesJS template library (product, waitlist, launch)
- G07: Obsei deploy + source config (Twitter, Reddit)
- G08: ALwrity deploy + API config

**W3-B: 新模块开发 — 4 tasks**
- H01: competitor_tracker.py (竞品追踪, 基于 Obsei + SerpBear)
- H02: ab_testing.py (A/B 测试引擎, 基于 PostHog)
- H03: trending.py 增强 (跨平台趋势聚合)
- H04: __main__.py 加新 CLI 命令 (campaign, analytics, competitor)

**Wave 3 subtotal: 12 tasks**

### Wave 4: 产品 Rollout (依赖 Wave 2-3)

**W4: Per-Product Setup — 9x5 = 45 tasks**
对每个产品 (ClawMarketing, ClawPhones, WorldGlasses, GEM, ClawVision, ClawGlasses, getPuffy, OysterRepublic, AgentForge):
- I-xx-1: Analytics tracking live (PostHog + Plausible)
- I-xx-2: SEO keyword baseline (SerpBear)
- I-xx-3: Initial content campaign (5 posts across platforms)
- I-xx-4: Email signup form on landing page
- I-xx-5: Social calendar (2 weeks planned)

**Wave 4 subtotal: 45 tasks, 产品间可并行**

### Wave 5: 验证 (依赖 Wave 4)

**W5: E2E Testing — 10 tasks**
- J01: Full pipeline: Pomelli → n8n → Postiz → analytics
- J02: Email pipeline: content → Listmonk → tracking
- J03: CRM pipeline: web visit → lead → email sequence
- J04: SEO pipeline: rank track → content trigger
- J05: Social listening: mention → alert → response
- J06: Cross-tool data consistency check
- J07: Error recovery + fallback validation
- J08: Security audit (API keys, access control)
- J09: Performance benchmarks
- J10: Runbook for each tool

**Wave 5 subtotal: 10 tasks**

---

## 任务总览

| Wave | 内容 | Tasks | 并行度 | 依赖 |
|---|---|---|---|---|
| W1 | 基础设施 + 公共层 + Pomelli | 26 | 全部并行 | 无 |
| W2 | Adapter + n8n + CM 对接 | 33 | adapter 间并行 | W1 |
| W3 | 高级工具 + 新模块 | 12 | 工具间并行 | W2 |
| W4 | 产品 Rollout | 45 | 产品间并行 | W2-3 |
| W5 | E2E 验证 | 10 | 管线间并行 | W4 |
| **TOTAL** | | **126** | | |

**从 296 → 126 tasks, 减少 57%。**
核心原因: 公共层复用消除大量重复开发。

---

## 执行计划

```
09:00  Wave 1 启动 (26 tasks, 32 agents) ——— ~2h
11:00  Wave 2 启动 (33 tasks) ——— ~2h
13:00  Wave 3 启动 (12 tasks) ——— ~1h
14:00  Wave 4 启动 (45 tasks, 全并行) ——— ~2h
16:00  Wave 5 启动 (10 tasks) ——— ~1h
17:00  完成。总耗时 ~8h。
```

32 agent 集群, 一天完成。

---

## Fallback 汇总

| 层 | 主路径 | Fallback 1 | Fallback 2 |
|---|---|---|---|
| 素材生成 | Pomelli | ALwrity | 模板 + Canva 手动 |
| 文字内容 | LLM (Claude) | Grok | content_templates |
| 工作流 | n8n | cron + CLI | 手动触发 |
| 社交发布 | Queue→Worker | 直接 adapter.post() | 手动发布 |
| 产品分析 | PostHog | Plausible | GA4 免费版 |
| Web 分析 | Plausible | PostHog web | GA4 |
| SEO | SerpBear | Google Search Console 手动 | — |
| 邮件 | Listmonk | Mautic email | 手动 SMTP |
| CRM | Twenty | SQLite + CSV | 手动表格 |
| 社交聆听 | Obsei | n8n + Twitter search | 手动搜索 |
| 营销自动化 | Mautic | n8n workflows | 手动触发 |
| CMS | Directus | 文件系统 + git | — |
| 着陆页 | GrapesJS | 手写 HTML | Pomelli 生成 |

---

## 成功标准

- [ ] 公共层 7 模块抽取完成，bluesky-poster + twitter-poster 共用
- [ ] 6 个平台 adapter 实现统一接口
- [ ] 12 个开源工具部署并可访问
- [ ] n8n 15 个核心 workflow 运行
- [ ] ClawMarketing 统一看板展示所有数据源
- [ ] 9 个产品全部有 analytics tracking
- [ ] 首个自动化 campaign 跨 3+ 平台发布
- [ ] 每个关键路径 fallback 验证通过
