# Investor Deck RTWI Upgrade Spec
## 从 "Hardware Infrastructure for AI Agents" → "Real-Time World Index"

> 目标: 把现有 investor-materials-2026-02/ 的 16-slide deck 升级为 RTWI 叙事
> 不是推翻重写，是把 ClawVision + RTWI 定位注入

---

## 升级策略

**旧叙事**: "We build hardware for AI agents" (硬件公司 → $30-50M FDV)
**新叙事**: "We index the real world for AI agents" (数据平台 → $80-150M valuation)

硬件是基础（已验证），但估值故事要升级到 **数据 + API + 网络效应**。

---

## Slide-by-Slide 升级计划

### Slide 1: Title — 改
**旧**: "Hardware Infrastructure for the AI Agent Economy"
**新**: "The Real-Time World Index — 30K phones mapping reality for AI"
- Sub: "Oyster Labs | $4M revenue (bootstrapped) | 70K DePIN users"
- 加 clawvision.org URL

### Slide 2: Problem — 微调
**旧**: "AI agents are blind"
**新**: 保持，但加一句: "And there's no API to see the real world. Google Maps is for humans. There's nothing for agents."

### Slide 3: Solution — 重写
**旧**: "We build hardware infrastructure"
**新**: "We built the world's first Real-Time World Index"
- `world.query()` — the world as an API
- 30K phones × 1fps = 30K observations/second
- H3 spatial cells, queryable in real-time
- Hardware is the moat, data is the product

### Slide 4: What We've Shipped — 保持
不变。这是 traction proof，硬件数据很强。

### Slide 5: Product Roadmap — 重构
改为 **"The ClawVision Stack"**:
```
Layer 4: world.query() API (ClawVision.org)     ← 这是产品
Layer 3: Spatial Index (H3 cells, Oysterworld)   ← 这是引擎
Layer 2: Edge AI (OpenClaw, VisionClaw)           ← 这是处理
Layer 1: Device Fleet (UBS, Puffy, ClawGlasses)   ← 这是基础
```

### Slide 6: Oyster Stack — 改名
改为 **"Why We Win: Vertical Integration"**
保持图，但重新标注强调 data 层是核心价值

### Slide 7: Oysterworld — 升级为 RTWI
**旧**: 对标 Funes + Google Maps
**新**: 对标 World Labs + Hivemapper + Niantic Spatial

| | ClawVision | World Labs | Hivemapper | Niantic Spatial |
|---|---|---|---|---|
| 数据来源 | 30K phones (1fps) | 合成生成 | Dashcam | 历史扫描 |
| 更新频率 | 秒级 | N/A | 路测中 | 静态 |
| 覆盖范围 | 全场景 | 虚拟 | 仅道路 | 仅建筑/室内 |
| API | world.query() | World API | Map tiles | Enterprise SDK |
| 价格 | $0.01/query | $1.20/gen | $19/月 | Enterprise |
| 估值 | 目标 $80-150M | $5B | ~$200M | $250M |

### Slide 8: Business Model — 升级
加入 API 收入线:
- Hardware (current): $4M cumulative
- **Spatial Query API**: $0.01-$0.05/query (NEW)
- **HD Map Freshness 订阅**: 企业年框 (M6+)
- **AI Training Data**: 真实世界数据授权 (M6+)
- **x402 micro-payments**: agent-native pay-per-query (NOW)

### Slide 9: Unit Economics — 更新
加入 per-query economics:
- API cost per query: ~$0.001 (compute + storage)
- Revenue per query: $0.01-$0.05
- **Gross margin: 90-95%** (vs hardware 40%)
- 这就是为什么估值要从 hardware multiplier 升级到 SaaS/data multiplier

### Slide 10: Market — 扩大
**旧 TAM**: $4.5B (Edge AI)
**新 TAM**: 加入 Spatial Data 市场
- Location Intelligence: $16B → $30B (2028)
- Geospatial Analytics: $7B → $15B (2028)
- Real-Time Data API: $5B+ (emerging)
- **总 addressable**: $20B+

### Slide 11: Competition — 升级
用 Business Insight Section 9 的五分天下图
加入 Niantic ($250M), AMI Labs (€3B target), Mapbox GeoAI

### Slide 12: Moat — 加一条
加: **5. Category Definition Moat** — 我们定义了 "Real-Time World Index" 这个品类。先定义者先受益。

### Slide 13: Traction — 加新条目
加:
- clawvision.org live (Landing + Map + API + Blog + Whitepaper)
- world.query() API live with 51 nodes, 443 cells, 32 cities
- x402 hackathon participation (Feb 11-13)
- "Real-Time World Index" category defined

### Slide 14: Team — 保持

### Slide 15: The Ask — 升级
**旧**: $5-10M @ $30-50M
**新**: 两层叙事
- **Floor (叙事 A)**: $5-10M @ $50-80M (DePIN + hardware traction)
- **Ceiling (叙事 B)**: $10-15M @ $80-150M (RTWI + network effect + API platform)
- 用 Hivemapper ($32M raise) 和 World Labs ($5B) 做锚

### Slide 16: Vision — 升级
**新**: "By 2027, every AI agent's default perception layer. The Google of the physical world — but for machines, not humans."

---

## 新增 Slides

### 加 Slide: Category Design (7.5 位置)
标题: "We're Building a New Category: Real-Time World Index"
- 赛道四分图 (合成/道路/3D/RTWI)
- 一句话: "World Labs generates synthetic worlds. ClawVision indexes the real one."

### 加 Slide: Hivemapper Customers = Our Customers (10.5 位置)
- HERE, TomTom, Mapbox, Trimble, Lyft, VW ADMT
- "These companies already pay for DePIN map data. We offer what Hivemapper can't: full-scene coverage."

---

## 执行

这个 spec 给 Codex 执行:
1. 复制 02-Investor-Pitch-Full.md → 02-Investor-Pitch-RTWI.md
2. 按上述 slide-by-slide 升级
3. 保持 Markdown 格式，可直接 → PDF
4. 同步更新 01-Executive-Summary.md → 01-Executive-Summary-RTWI.md
