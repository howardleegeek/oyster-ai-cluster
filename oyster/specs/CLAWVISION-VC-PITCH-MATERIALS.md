# ClawVision VC 融资材料

> 用途：VC Pitch / Investor Outreach / Website Content
> 版本：2026-02-16

---

# 一、VC 会买单的首页文案（完整版）

---

## HERO SECTION（第一屏）

# ClawVision

## The Real-Time World Index

World Labs generates synthetic worlds.
ClawVision indexes the real one.

We are building the first global, real-time index of the physical world — powered by distributed cameras, AI glasses, and edge devices.

---

## SECTION 2 — 为什么现在（Why Now）

The world is becoming machine-readable.

- AI agents are making decisions autonomously
- Robotics and logistics require live environmental data
- Generative world models need real-world grounding
- Existing mapping systems are static, slow, or limited to roads

But there is no continuous, queryable, real-time index of the physical world.

Until now.

---

## SECTION 3 — 我们做什么（What We Built）

ClawVision turns cameras into a real-time indexing network.

**Data Pipeline:**

```
Devices
  → 1fps visual + audio capture
  → Edge compression
  → Spatial indexing (H3 cells)
  → Event classification
  → world.query() API
```

Developers, enterprises, and AI agents can query the real world like a database.

**Example Query:**

```json
world.query({
  city: "Los Angeles",
  category: "traffic_density",
  freshness: "< 5 minutes"
})
```

**Result:** structured, timestamped, geospatially indexed data.

---

## SECTION 4 — 硬件战略（Hardware + Network）

We are deploying:

- AI Glasses
- Smart Cameras
- Edge Devices
- Phone-based nodes

Each device becomes a real-time world sensor.

**This is not a SaaS product.**
**This is a distributed physical infrastructure network.**

---

## SECTION 5 — 护城河（Moat）

1. **Continuous capture (1fps model)** — cost-efficient at scale
2. **Spatial-temporal indexing** — structured, queryable data
3. **Network effect** — more nodes = more coverage = more value
4. **API-first architecture** — high-margin data layer

We do not compete as a computer vision tool.
We operate as a **real-world data infrastructure**.

---

## SECTION 6 — 市场机会

AI agents will require real-world data:

- Robotics
- Logistics
- Insurance
- Smart Cities
- Retail
- Autonomous systems

**Global market potential: $100B+ in real-world data services.**

---

## SECTION 7 — 商业模型

- Pay-per-query API
- Enterprise contracts
- Hardware revenue
- Data subscriptions
- Agent-based micro-payments

**High-margin recurring data layer on top of hardware deployment.**

---

## SECTION 8 — 愿景

We are building the real-time layer of the physical world.

**ClawVision**
**Index the real world.**

---

# 二、融资 One Pager（直接给 VC）

---

## ClawVision

### The Real-Time World Index

---

### Problem

AI systems and autonomous agents require continuous real-world data.
Existing mapping solutions are static, limited, or road-focused.
There is no global, queryable, real-time index of the physical world.

---

### Solution

ClawVision transforms distributed cameras, AI glasses, and edge devices into a real-time spatial indexing network.

**Data is:**

- Continuously captured (1fps model)
- Geospatially indexed
- Event-structured
- Accessible via world.query() API

---

### Why Now

- Explosion of AI agents
- Robotics and logistics automation
- Generative world models
- Edge AI cost reduction
- Hardware commoditization

**Timing aligns for real-world indexing infrastructure.**

---

### Market

AI data infrastructure + robotics + logistics + mapping

**Total addressable opportunity: $100B+**

**Comparable category signals:**

- World Labs — $5B valuation
- Hivemapper — $32M raised
- Niantic Spatial — $250M raised

---

### Business Model

- $0.01–$0.05 per query
- Enterprise subscriptions
- Hardware distribution
- Data licensing

**Long-term: high-margin API layer with recurring revenue.**

---

### Traction

*(Fill with your real metrics)*

- X active nodes
- X cities covered
- X events indexed
- Hardware pipeline underway

---

### Vision

ClawVision becomes the default real-time data layer for AI systems interacting with the physical world.

---

### The Ask

**Raising: $X million**

**Use of funds:**

- Hardware deployment
- Node expansion
- API scaling
- Enterprise BD
- Global coverage growth

---

# 三、融资导向的网站结构（兼顾硬件落地）

---

## 网站架构总览

```
clawvision.org/
├── index.html          # Hero + Vision + Network Stats + CTA
├── network.html       # Device types + Coverage Map
├── hardware.html       # Network deployment narrative
├── api.html           # world.query() docs + Use Cases
├── investors.html     # One Pager + Deck + Contact
└── blog/              # Category definition content
```

---

## 1. 首页（Vision + Network）

**必须包含：**

- Real-Time World Index 定位
- 网络规模（实时数字）
- world.query() API 演示
- 对标 World Labs / Hivemapper
- **融资 CTA**

**VC 视角：** 第一屏就要看到"这不是普通 SaaS，这是基础设施网络"

---

## 2. Network 页面

**内容结构：**

### Device Types

| 设备类型 | 角色 | 数据产出 |
|---------|------|----------|
| AI Glasses | 移动视觉采集 | 1fps + GPS + heading |
| Smart Cameras | 固定点监测 | 连续流 + 事件检测 |
| Edge Devices | 边缘计算 | 本地处理 + 压缩 |
| Phone Nodes | 众包采集 | 间歇式 + 场景丰富 |

**核心叙事：** 每台设备 = 网络节点 = 数据源

---

## 3. Hardware 页面

**这是关键 — 硬件是网络扩张工具，不是消费电子品牌**

### Why Hardware Matters

| 维度 | 消费电子视角 | 基础设施视角 |
|------|------------|------------|
| 目标 | 卖产品给用户 | 部署节点扩网络 |
| 成功标准 | 销量 | 覆盖密度 |
| 边际成本 | 高（每台都要赚） | 低（越铺越便宜） |
| 估值模型 | 硬件 P/E | 网络 NTM |

### Hardware Deployment Economics

```
每增加 1,000 节点
  → 覆盖范围 +X km²
  → 数据新鲜度 +X%
  → API 潜在调用 +X

节点密度 → 数据质量 → 客户付费意愿
```

**VC 要看到：** 硬件 = 跑马圈地的工具

---

## 4. API 页面

### world.query() — 核心产品

**用例展示：**

| 用例 | 查询 | 客户 |
|------|------|------|
| 物流优化 | "此仓库周边 1km 内实时交通密度" | 物流公司 |
| 保险风险 | "该区域过去 24h 天气事件" | 保险公司 |
| 零售洞察 | "这家店门口每小时人流峰值" | 零售商 |

### 定价

| Tier | 价格 | 限制 |
|------|------|------|
| Developer | 1,000 calls/day | Free |
| Growth | $99/mo | 100K calls |
| Enterprise | Custom | SLA + 专属区域 |

---

## 5. Investors 页面

**仅供投资人访问**

- One Pager 下载 (PDF)
- Pitch Deck 下载 (PDF, request access)
- Contact: founders@clawvision.io

**加密访问** — 可设置简单密码或需要邮件申请

---

## 页面间叙事逻辑

```
首页 (What)      → 我们是 Real-Time World Index
     ↓
网络页 (How)    → 靠分布式设备网络实现
     ↓
硬件页 (Why)    → 硬件是扩张工具，不是终点
     ↓
API页 (Value)   → 客户怎么使用、数据怎么变现
     ↓
融资页 (Ask)    → 投资人专用入口
```

---

# 四、核心叙事校准

---

## 两种公司，估值差 10 倍

| 维度 | 视觉 AI 公司 | 数据基础设施公司 |
|------|-------------|-----------------|
| 定位 | AI 工具 | 网络平台 |
| 护城河 | 算法 | 节点 × 数据 |
| 增长 | 获客 | 网络效应 |
| 收入 | 项目合同 | API 调用 |
| 估值 | 3-5x ARR | 10-25x NTM |

---

## 硬件的正确叙事

**❌ 不要说：**
> "我们做了一款 AI 眼镜"

**✅ 要说：**
> "我们部署网络节点，每台设备扩展实时世界索引的覆盖范围"

**差别：**
- 前者 = 消费电子创业
- 后者 = 基础设施扩张

---

## 一句话定位

> **"World Labs generates synthetic worlds. ClawVision indexes the real one."**

**VC 听到的：** 这不是另一个计算机视觉创业公司，这是一个新赛道的基础设施。

---

# 五、下一步

---

## 立即可执行

| 任务 | 优先级 | 负责人 |
|------|--------|--------|
| 更新 clawvision.org 首页为融资版 | P0 | Codex |
| 创建 Network 页面 | P0 | Codex |
| 创建 Hardware 页面 | P1 | Codex |
| 创建 Investors 页面 | P1 | Codex |
| 填充真实节点/覆盖数据 | P0 | Relay |
| 拍摄硬件产品图 | P2 | External |

## 待定

| 任务 | 说明 |
|------|------|
| 12 页 Pitch Deck | 需要先确认财务模型 |
| 25 个 VC 刁钻问题 | 需要准备 Q&A |
| 硬件商业模型测算 | 需要财务数据 |

---

# 六、你的选择

---

**下一步方向：**

A) **冲融资** — 先把网站改成融资版，12 页 deck 写出来

B) **冲收入** — 先做 world.query() 商业化，接真实客户

C) **两条腿跑** — 网站融资版 + API 商业化同步推进

**告诉我你的选择，我给你最狠的执行方案。**

---

*文档结束 — 准备给 VC 的完整融资材料*
