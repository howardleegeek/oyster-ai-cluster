## 任务: Oyster Labs 12 项市场研究分析 (McKinsey-Level AI Prompts)

### 背景
来源: @socialwithaayan 的病毒推文 (876K views, 6.4K likes)，12 个 Claude Opus 4.6 市场研究 prompt。
需要针对 Oyster Labs 的实际业务 (DePIN phones, ClawGlasses, Oysterworld, $WORLD token) 全面执行这 12 项分析。
产出用于: 投资人 deck、产品策略、GTM 规划。

### Oyster Labs 核心数据 (填入 prompts)
- **Products**: Universal Phone (UBS) $180, Puffy $TBD, ClawGlasses $TBD, ClawPhones (software)
- **Revenue**: $4M (40K+ phones sold)
- **Users**: 70K DePIN users
- **Token**: $WORLD
- **Industry**: DePIN + AI + Spatial Computing
- **Target Customer**: Web3 早期采用者, DePIN 矿工, AI 开发者, 新兴市场用户
- **Geography**: Global (focus: SEA, LATAM, NA)
- **Competitors**: Solana Phone ($450), JamboPhone, IoTeX Pebble, Helium

---

## 第一批 P0 — 投资人必备 (立即执行)

### 分析 1: Market Sizing & TAM Analysis
**角色**: McKinsey-level market analyst
**Prompt 要点**:
- Top-down: Global DePIN market → AI Phone segment → Oyster's slice
- Bottom-up: Unit economics × potential customers
- TAM, SAM, SOM breakdown with dollar figures
- CAGR 5 years
- Key assumptions
- Comparison to 3 analyst reports (Messari, IoTeX research, DePIN Ninja)
- Format: investor-ready market sizing slide

**输出文件**: `~/Downloads/specs/output/01-tam-analysis.md`

### 分析 5: SWOT + Porter's Five Forces
**角色**: Harvard Business School strategy professor
**Prompt 要点**:
- SWOT: 7 strengths, 7 weaknesses, 7 opportunities, 7 threats (with evidence)
- Porter's Five Forces for DePIN phone industry:
  - Supplier power (chip manufacturers, blockchain infra)
  - Buyer power (Web3 users, DePIN miners)
  - Threat of new entrants
  - Threat of substitutes (regular phones + DePIN apps)
  - Competitive rivalry
- Strategic implications matrix

**输出文件**: `~/Downloads/specs/output/05-swot-porters.md`

### 分析 9: Financial Modeling & Unit Economics
**角色**: VP of Finance at a high-growth startup
**Prompt 要点**:
- Unit economics: CAC by channel, LTV, LTV:CAC ratio
- Revenue model: hardware sales + token economics + data marketplace
- Contribution margin per phone
- Break-even analysis
- 3-year P&L projection (base/bull/bear)
- Key assumptions table
- Use actual data: $4M revenue, 40K units, $100 avg price point

**输出文件**: `~/Downloads/specs/output/09-unit-economics.md`

### 分析 12: Executive Strategy Synthesis (Master Prompt)
**角色**: Senior partner at McKinsey presenting to CEO
**Prompt 要点**:
- Executive summary: 3-paragraph strategic overview
- Synthesize all analyses (1-11) into one strategic recommendation
- Key strategic pillars (3-5)
- Critical decisions needed in next 90 days
- Resource allocation recommendation
- Risk-adjusted roadmap
- One-page strategy canvas

**输出文件**: `~/Downloads/specs/output/12-master-synthesis.md`
**注意**: 这个需要在 1, 5, 9 完成后执行，需要读取前面的分析结果

---

## 第二批 P1 — 产品策略

### 分析 2: Competitive Landscape Deep Dive
**角色**: Senior strategy consultant at Bain & Company
**Prompt 要点**:
- Direct competitors: Solana Phone, JamboPhone, IoTeX Pebble, Nothing Phone (crypto edition)
- Indirect: Regular phones + DePIN apps (Helium, Hivemapper)
- Top 10 players ranked by market share, revenue, funding
- Competitive advantages map (2x2 matrix)
- Gap analysis: underserved segments
- Strategic positioning recommendation

**输出文件**: `~/Downloads/specs/output/02-competitive-landscape.md`

### 分析 3: Customer Persona & Segmentation
**角色**: World-class consumer research expert
**Prompt 要点**:
Build 4 personas for Oyster Labs products:
1. **DePIN Miner Mike** — crypto-native, passive income seeker
2. **AI Developer Dana** — building on-device AI agents
3. **Emerging Market Ella** — affordable smart device, new to Web3
4. **Spatial Explorer Sam** — ClawGlasses early adopter, spatial computing enthusiast
- Each: demographics, psychographics, pain points, buying triggers, channels, objections

**输出文件**: `~/Downloads/specs/output/03-customer-personas.md`

### 分析 6: Pricing Strategy Analysis
**角色**: Pricing strategy consultant (Fortune 500 experience)
**Prompt 要点**:
- Competitor pricing audit: Solana Phone $450, JamboPhone $99, regular phones $150-300
- Value-based pricing analysis for each product line
- Price sensitivity testing framework
- Tier structure recommendation (Basic/Pro/Enterprise?)
- Token economics impact on effective price
- Regional pricing strategy (SEA vs NA vs LATAM)

**输出文件**: `~/Downloads/specs/output/06-pricing-strategy.md`

### 分析 7: Go-To-Market Strategy
**角色**: Chief Strategy Officer (20+ B2B/B2C launches)
**Prompt 要点**:
- Launch phasing: Pre-launch (60d), Launch (week 1), Post-launch (90d)
- Channel strategy: crypto communities, DePIN ecosystems, developer platforms
- Partnership strategy: blockchain L1s, DePIN protocols, carrier partnerships
- Content & community plan
- Metrics & KPIs per phase
- Budget allocation per channel
- Geographic rollout sequence

**输出文件**: `~/Downloads/specs/output/07-gtm-strategy.md`

---

## 第三批 P2 — 背景研究 (可交给 OC agents)

### 分析 4: Industry Trend Analysis
**角色**: Senior analyst at Goldman Sachs Research
**输出文件**: `~/Downloads/specs/output/04-industry-trends.md`

### 分析 8: Customer Journey Mapping
**角色**: Customer experience strategist
**输出文件**: `~/Downloads/specs/output/08-customer-journey.md`

### 分析 10: Risk Assessment & Scenario Planning
**角色**: Risk management partner at Deloitte
**输出文件**: `~/Downloads/specs/output/10-risk-assessment.md`

### 分析 11: Market Entry & Expansion Strategy
**角色**: Global expansion strategist (30+ market entries)
**输出文件**: `~/Downloads/specs/output/11-market-entry.md`

---

### 执行顺序
1. 并行执行 P0: #1, #5, #9
2. #12 依赖 P0 完成后执行
3. 并行执行 P1: #2, #3, #6, #7
4. P2 交给 OC agents 或空闲时执行

### 验收标准
- [ ] 每份分析至少 1500 字，结构清晰有 markdown 表格
- [ ] 包含具体数据和引用来源 (不编造数据)
- [ ] 投资人可直接使用的格式
- [ ] 所有输出存到 ~/Downloads/specs/output/ 目录
- [ ] #12 Master Synthesis 综合引用前 11 份分析

### 注意
- 使用 web search 获取最新数据 (DePIN market size 2025-2026)
- 不要编造具体数字，标注来源或标明 "estimated"
- Oyster Labs 真实数据: $4M revenue, 40K phones, 70K users, $WORLD token
- 竞品数据用公开信息，不确定的标注 "unverified"
