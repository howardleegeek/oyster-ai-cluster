---
task_id: S01-clawvision-website
project: clawvision
priority: 1
depends_on: []
modifies:
  - ~/Downloads/clawvision-org/index.html
---

# ClawVision 官网重写 — "最伟大的公司"版

## 目标

把 ClawVision 首页重写为**史诗级公司官网**，定位 "Real-Time World Index"，体现"最伟大的公司"气场。

## 约束

- 不动 CSS（保持现有深色科技风格）
- 不动其他页面（map.html, api.html, blog.html, whitepaper.html）
- 保持响应式
- 保持现有 JS 交互（stats bar 等）

## 现有内容参考

当前 index.html (382 行) 结构：
1. Hero — 30K phones, world.query()
2. Stats bar — 实时节点/事件/Cells/新鲜度
3. Problem — 99% 物理世界未映射
4. Solution — 30K phones × 1 FPS = Living World Model
5. Live Map embed
6. API code snippet
7. 对比表：传统地图 vs ClawVision
8. Big Numbers: 30K devices, $4M revenue, 70K users
9. Pipeline 架构图
10. Node Architecture 详图
11. Use Cases (6 个)
12. For Developers / For Partners

## 新版首页方向

### 核心定位

> **"World Labs generates synthetic worlds. ClawVision indexes the real one."**

### 叙事结构

1. **Hero** — 一句话史诗定位
2. **Why Now** — 为什么现在是时刻
3. **What We Built** — 产品架构
4. **Hardware = Network** — 硬件是网络扩张工具
5. **Moat** — 护城河（数据持续性、网络效应）
6. **Market** — $100B+ 市场
7. **Business Model** — API 收费 + 企业合同
8. **Vision** — 终极愿景

### 风格要求

- 史诗感、公司感
- 不是"产品功能清单"
- 是"我们在改变世界"的叙事
- 参考 Stripe、World Labs、Helium 风格

## 验收标准

- [ ] 新 index.html 写完，叙事连贯
- [ ] 本地 `python3 -m http.server 8000` 能跑
- [ ] 用 curl 检查主要 section 存在
