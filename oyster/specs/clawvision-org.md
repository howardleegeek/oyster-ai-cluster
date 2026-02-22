# ClawVision.org — Full Site Spec

## 品牌定位
ClawVision = ClawPhones 的 vision AI 子品牌，统一 30K+ 设备 camera fleet 的品牌入口。

```
ClawPhones (母品牌)
  └── ClawVision (clawvision.org)
        ├── Camera Fleet — 30K+ 设备视觉网络
        ├── Oysterworld — Living World Model (空间数据层)
        └── VisionClaw — 设备端 vision agent
```

## 三大模块

### 1. Landing Page (首页)
**路径:** `/`
**目标:** 30 秒内让访客理解 "30K 设备组成的 vision AI 网络"

**结构:**
- **Hero Section**
  - 大标题: "The World's Largest Phone-Powered Vision Network"
  - 副标题: "30,000+ ClawPhones continuously mapping and understanding the physical world"
  - CTA: "Explore the Live Map" + "Build with Our API"
  - 背景: 动态粒子/网格动画暗示全球网络

- **Stats Bar** (实时数据，从 relay API 拉)
  - Active Nodes | Total Events | Cells Covered | Freshness (avg age)
  - 数据源: `GET /v1/world/stats` (Oysterworld relay, port 8787)

- **How It Works** (3 步)
  1. ClawPhones capture 1 FPS visual + GPS → "30K phones see the world"
  2. Oysterworld indexes by H3 cells → "Spatial intelligence at 100m resolution"
  3. world.query() API → "Ask anything about any place"

- **Use Cases** (卡片)
  - Urban Planning / Smart City
  - Autonomous Navigation
  - Retail & Foot Traffic Analytics
  - Environmental Monitoring
  - Security & Safety

- **Fleet Overview** (数据可视化)
  - 缩略版 live map (嵌入 map 模块)
  - 地理分布统计

- **For Developers** (CTA → API Portal)
  - "Access world.query() API"
  - Code snippet 展示

- **For Partners** (CTA)
  - "Join the ClawVision network"
  - Contact form / email

- **Footer**
  - ClawVision by ClawPhones (Oyster Labs)
  - Links: API Docs, Live Map, GitHub, Twitter (@ClawGlasses)
  - Legal: Privacy, Terms

### 2. Live Coverage Map
**路径:** `/map`
**目标:** 实时展示 fleet 覆盖范围，证明 "world is lit up"

**基于现有:** `~/Downloads/claw-nation/node-web/map.html` (535 lines)

**改动:**
- 重新包装 UI 风格匹配 ClawVision 品牌 (深色主题)
- 顶部导航栏 (← Home | Map | API Docs)
- 左侧面板:
  - 实时 stats (nodes, events, cells)
  - 时间窗口选择 (1h/6h/24h/7d)
  - Scale toggle (log/linear)
  - Min count filter
  - Auto-refresh toggle
- 点击 hex cell → 弹出 panel:
  - Cell ID, event count, last update time
  - 最新 frame 缩略图 (从 `/v1/blobs/<evt_id>.jpg`)
  - "Query this cell via API" 链接
- 右下角: ClawVision watermark

**数据源:**
- `GET /v1/world/cells?res=9&hours=24&limit=5000`
- `GET /v1/world/events?cell=<h3>&limit=10`
- `GET /v1/blobs/<evt_id>.jpg`

### 3. API Portal
**路径:** `/api`
**目标:** 开发者能在 5 分钟内理解并开始使用 world.query() API

**结构:**
- **Overview**
  - ClawVision API 简介
  - Authentication (API key)
  - Base URL: `https://api.clawvision.org/v1/` (暂时 proxy 到 relay 8787)
  - Rate limits

- **Endpoints** (基于现有 OpenAPI spec + 扩展)
  - `GET /v1/world/stats` — System overview
  - `GET /v1/world/cells` — Coverage heatmap data
  - `GET /v1/world/events` — Query events by cell
  - `GET /v1/blobs/{id}.jpg` — Retrieve frame
  - `POST /v1/nodes/register` — Register a new node
  - `POST /v1/events/frame` — Submit a frame

- **Code Examples** (Python, JavaScript, cURL)
  ```python
  import requests
  r = requests.get("https://api.clawvision.org/v1/world/cells?res=9&hours=24")
  cells = r.json()["cells"]
  print(f"{len(cells)} active cells in the last 24h")
  ```

- **Interactive Playground**
  - Try-it-now: 选 endpoint → 填参数 → 发请求 → 看结果
  - 不需要注册就能试基础查询

- **SDKs & Tools** (coming soon placeholder)
  - Python SDK
  - JavaScript SDK
  - CLI tool

## 技术架构

```
clawvision.org (Cloudflare / Vercel / 静态 + proxy)
  │
  ├── / (Landing) — 静态 HTML + CSS + JS
  ├── /map — Leaflet + H3 可视化
  ├── /api — API 文档 (可能用 Swagger UI 或自建)
  │
  └── API proxy: api.clawvision.org → relay:8787
```

**技术选型:**
- **方案 A (推荐): 纯静态 SPA**
  - Single HTML 或极简 framework (Alpine.js / vanilla)
  - Cloudflare Pages 部署 (免费)
  - API proxy 通过 Cloudflare Workers
  - 优点: 零运维，秒加载，便宜

- **方案 B: Next.js**
  - Vercel 部署
  - API route 做 proxy
  - 优点: SEO 更好，但对这种场景可能过重

**推荐方案 A** — 和现有 Oysterworld 前端 (纯 HTML) 保持一致，Codex 实现速度最快。

## 设计风格
- **主色:** 深色背景 (#0a0a0f) + 青色/蓝绿高亮 (#00e5ff / #00ff88)
- **副色:** 白色文字 + 灰色 (#666) 次要信息
- **风格:** 暗黑科技感，类似 Mapbox / Planet Labs 的数据可视化风格
- **字体:** Inter (UI) + JetBrains Mono (代码)
- **动画:** 微动效，不要花哨。Stats 数字滚动，hex cells 渐显

## 文件结构
```
~/Downloads/clawvision-org/
├── index.html          # Landing page
├── map.html            # Live coverage map
├── api.html            # API documentation portal
├── css/
│   └── style.css       # 全局样式
├── js/
│   ├── main.js         # Landing page 逻辑 (stats fetch, animations)
│   ├── map.js          # Map 逻辑 (Leaflet + H3)
│   └── api.js          # API playground 逻辑
├── assets/
│   ├── logo.svg        # ClawVision logo
│   └── og-image.png    # Social sharing image
└── README.md           # 部署说明
```

## 数据对接
- Relay API 当前跑在 `localhost:8787`
- 开发时直接连 localhost
- 部署时通过 Cloudflare Workers proxy 到 EC2 或直接暴露 relay

## 验收标准
- [ ] Landing page 加载 < 2s，首屏无闪烁
- [ ] Stats bar 从 relay API 实时拉数据 (有 fallback 显示 "30,000+" 静态值)
- [ ] Live map 正确渲染 H3 hexagons，点击可查看 cell 详情
- [ ] API docs 页面包含所有 6 个 endpoint 的文档
- [ ] API playground 可以发真实请求并显示结果
- [ ] 全站响应式 (mobile + desktop)
- [ ] 深色主题，视觉风格统一
- [ ] 导航栏在所有页面一致
- [ ] 代码示例可复制
- [ ] 无外部 tracking / analytics (隐私优先)

## 部署
- Domain: clawvision.org (已购)
- DNS: 先指向 Cloudflare Pages (或 Vercel)
- SSL: 自动 (Cloudflare / Let's Encrypt)
- API proxy: api.clawvision.org → relay server

## 竞品分析: Sean Liu (seanliu.io) — 要学的东西

### 竞品概况
Xiaoan (Sean) Liu — CU Boulder PhD, 前 Google Blended Intelligence Lab + NYU Future Reality Lab
核心项目: Reality Proxy (UIST 2025) — Apple Vision Pro + DINO-X + GPT-4o
定位: "human-centered multimodal AI thinking tools" (学术方向)
网站: Framer 建的学术 portfolio，深色极简，项目卡片式展示

### 他做得好的 (学过来)

**1. 学术 credibility 包装 → 我们用数据 credibility**
- 他: UIST/SIGGRAPH 论文 badge, Google/NYU logo 背书
- 学: 在 Landing page 加 "Backed by Data" section
  - "30,000+ active devices" (硬数据)
  - "$4M hardware revenue" (商业验证)
  - "70,000 DePIN users" (社区规模)
  - 合作伙伴 logo 墙 (如有)

**2. 项目展示用 video/动图 → 我们用 live demo**
- 他: 每个项目一个 hero video + 动图演示
- 学: Hero section 放一个 live mini-map (不是视频，是真实数据实时渲染)
  - 比视频更有说服力: "这不是 demo，这是真的在跑"
  - Hex cells 实时闪烁 = 数据在流入的视觉证明

**3. 交互叙事结构 → 我们用 scroll storytelling**
- 他: 问题 → 洞察 → 方案 → Demo 的叙事链
- 学: Landing page 用 scroll-driven 叙事:
  - Section 1: "The problem" — "99% of the physical world is unmapped and un-queryable"
  - Section 2: "Our approach" — "30K phones × 1 FPS = Living World Model"
  - Section 3: "See it live" — 嵌入 live map
  - Section 4: "Build with it" — API code snippet + playground CTA

**4. 技术深度展示 → 我们用架构图**
- 他: 论文级的系统架构图 (pipeline diagram)
- 学: 在 "How it Works" section 加一张精美的架构图:
  ```
  Phone Fleet → 1 FPS Capture → H3 Indexing → world.query() API
  (30K devices)   (GPS + Visual)   (100m cells)   (Any app)
  ```
  用 SVG 动画，数据从左到右流动

**5. 开放生态叙事**
- 他: "open-source AR/WebXR toolkits"
- 学: 强调开放 API + 开发者友好
  - "Free tier: 1000 queries/day"
  - GitHub link (开源 SDK)
  - "Join 70K+ node operators"

### 他的弱点 (我们的优势)

| 弱点 | 我们怎么打 |
|------|----------|
| 1 台 AVP | "30,000+ devices, real-world scale" |
| 实验室数据 | Live map 用真实数据打脸 |
| 纯学术 | "$4M revenue, shipping product" |
| 个人项目 | "Oyster Labs team + 70K community" |
| 无 API | world.query() 开放给任何开发者 |

### 融入 spec 的具体改动

**Hero Section 升级:**
- 背景不再是粒子动画 → **改为 live mini-map** (缩小版 H3 heatmap，真实数据)
- 加一行 social proof: "Powering 30K+ devices across XX countries"

**新增 Section: "Why ClawVision"**
位于 How It Works 之后:
- 对比卡片: "Traditional Mapping" vs "ClawVision"
  - Static snapshots vs Continuous 1 FPS updates
  - Expensive survey equipment vs Existing phone fleet
  - Months-old data vs Minutes-fresh data
  - Single perspective vs Multi-angle coverage

**新增 Section: "Backed by Real Scale"**
- 大数字展示 (counter animation):
  - 30,000+ Active Devices
  - $4M+ Hardware Revenue
  - 70,000+ Network Participants
  - 100m Spatial Resolution

**API Portal 升级:**
- 加 "Try it now — no signup required" 醒目 badge
- 首页 code snippet 从 Python 改为更短的 cURL one-liner
- 加 response 预览 (实际返回的 JSON)

## 不在本期范围
- 用户注册/登录系统
- API key 管理 dashboard
- 付费 plan
- world.query() 自然语言接口 (planned, not MVP)
- 3D 重建展示
- 多语言
