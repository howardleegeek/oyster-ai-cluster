# Oyster Labs AI 代码工厂 v6 — 统一流程

> v5 教训: 散打模式（70+ repos, 1390 tasks 盲跑）效率低，方向不聚焦。
> v6 核心: **一条管线，六个阶段，每步有明确输入输出。**

---

## 全流程一览

```
┌─────────────────────────────────────────────────────────────┐
│  Howard: "做 X"                                              │
│     ↓                                                        │
│  P0  方向定义     Opus 10 秒给方向 + 约束                       │
│     ↓                                                        │
│  P1  开源扫描     Codex MCP 搜 GitHub (不走 dispatch)          │
│     ↓                                                        │
│  P2  选型决策     Opus 看扫描结果: Fork / 集成 / 自研            │
│     ↓                                                        │
│  P3  Spec 生成    MiniMax 拆 spec (基于 fork 的代码)            │
│     ↓                                                        │
│  P4  Dispatch     dispatch.py start → 集群执行                 │
│     ↓                                                        │
│  P5  交付合并     collect → report → Howard 审批               │
│     ↓                                                        │
│  DONE                                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 每阶段详细定义

### P0 — 方向定义 (Howard + Opus, 1 分钟)

**输入**: Howard 一句话 ("做一个 AI 合同审查工具")
**输出**: 方向文档 (存 `specs/<project>/DIRECTION.md`)

```markdown
# DIRECTION: ai-contract-review
- 目标: AI 自动审查法律合同，标注风险条款
- 用户: 律所、企业法务
- 技术约束: Python, REST API, 支持 PDF 输入
- 不做: 不做 UI, 不做移动端
```

**规则**:
- Opus 只写 5 行以内
- 不写详细 spec
- 不写代码

---

### P1 — 开源扫描 (Codex MCP, 5 分钟)

**输入**: DIRECTION.md 中的关键词
**输出**: 扫描报告 (存 `memory/open-source-atlas/projects/<project>.md`)

**执行方式**: Opus 直接调用 Codex MCP 或 GitHub MCP，不走 dispatch。

```
Opus 调 Codex:
  "搜索 GitHub: ai contract review legal document analysis
   找 TOP 5 开源项目，按 stars/活跃度/license 排序
   输出: repo, stars, license, 最后更新, 匹配度"
```

**为什么不走 dispatch**:
- Research 任务无代码产出 → Gate 2 必然失败
- Codex 有 GitHub 原生工具 → 搜索更准
- 5 分钟完成 vs dispatch 等 30 分钟

**规则**:
- 必须完成 P1 才能进 P2
- 没有扫描报告 = 不许自研

---

### P2 — 选型决策 (Opus + Howard, 2 分钟)

**输入**: P1 扫描报告
**输出**: 决策 (存到扫描报告末尾)

只有三种决策：

| 决策 | 条件 | 下一步 |
|------|------|--------|
| **直接 Fork** | Stars > 5K, 活跃, MIT/Apache | `gh repo fork` → 进 P3 |
| **Fork + 改造** | Stars > 1K, 部分匹配 | `gh repo fork` → spec 基于 fork 代码 |
| **核心自研** | 无匹配 / Oyster 独有逻辑 | 从零写 spec，但只自研核心差异部分 |

**规则**:
- "直接 Fork" 和 "Fork + 改造" 合计应 > 70% 的能力模块
- 全栈自研需要 Howard 签字

---

### P3 — Spec 生成 (MiniMax, 3 分钟)

**输入**: DIRECTION.md + P2 决策 + fork 后的代码库
**输出**: 原子 spec 文件 (存 `specs/<project>/S*.md`)

```
Opus 调 MiniMax:
  "基于这个 fork 的代码库 (OpenContracts), 拆成原子任务:
   1. 加中文合同支持
   2. 接入 GPT-4o 做条款风险打分
   3. 加 REST API endpoint /analyze
   约束: 不改原有功能, 只加新功能"
```

**与 v5 的区别**:
- v5: 从零生成 spec → agent 要写全部代码
- v6: 基于 fork 生成 spec → agent 只改/加代码，工作量减 60%

---

### P4 — Dispatch 执行 (dispatch.py, 自动)

**输入**: P3 生成的 spec 文件
**输出**: 代码改动 (git branch per task)

```bash
python3 dispatch.py start <project>
```

**规则**:
- 沿用现有 dispatch 系统，不改
- Spec 必须指向 fork 后的 repo (有代码基础)
- Gate 2 通过率预期 > 80% (因为是改代码不是从零写)

---

### P5 — 交付合并 (dispatch + Howard, 10 分钟)

**输入**: dispatch report
**输出**: merged code / PR

```bash
python3 dispatch.py collect <project>
python3 dispatch.py report <project>
# Howard 看报告: PASS/FAIL
```

---

## 三个执行通道 (明确分工)

| 通道 | 用途 | 适合 |
|------|------|------|
| **Codex MCP** (本地) | 搜索、调研、读代码分析 | P1 开源扫描, 代码审计 |
| **Dispatch** (集群) | 写代码、改代码、跑测试 | P4 执行, 批量生产 |
| **Opus** (本地) | 给方向、审批、架构决策 | P0, P2, 关键技术决策 |

**铁律**: 搜索用 Codex，写代码用 Dispatch，决策用 Opus。不混用。

---

## 项目分类与处理策略

### A. 核心产品 (5 个，持续迭代)
ClawMarketing, GEM Platform, ClawPhones, WorldGlasses, ClawVision

→ 正常走 P0-P5，dispatch 已有 spec 继续跑

### B. 新项目 (开源优先)
ai-contract-review, voice-ai, ai-trading 等

→ **必须先走 P1 开源扫描**，找到 fork 基础再写 spec

### C. 概念项目 (70+ repos，大部分无代码)
new-venture-*, ai-driven-*, ai-powered-*

→ **归档到 archive/**，不再投入 dispatch 资源
→ 需要时从 archive 拿出来走 P0-P5

### D. 社交工具 (6 个，维护模式)
twitter-poster, bluesky-poster, discord-admin 等

→ 维护现有功能，新功能走 P0-P5

---

## 每日节奏 (v6)

```
09:00  Howard: 给 1-3 个方向 (P0)
09:05  Opus/Codex: 开源扫描 (P1, 5 min each)
09:15  Opus: 选型决策 (P2, 快速)
09:20  Opus/MiniMax: 基于 fork 拆 spec (P3)
09:30  dispatch: 自动执行 (P4)
       ... agent 并行执行 ...
17:00  Howard: 看 report, PASS/FAIL (P5)
17:10  collect + merge
```

**vs v5 差异**: 多了 P1 (开源扫描)，spec 基于 fork 而不是从零写。

---

## Token 优化 (v6)

| 规则 | 省多少 |
|------|--------|
| P1 用 Codex MCP 不用 Opus | 省 90% (Codex 免费) |
| Spec 基于 fork → agent 改代码不是写全部 | 省 40% task token |
| Research 不走 dispatch | 省 100% (不会 Gate 2 失败重试) |
| 概念项目归档 → 不占 slot | 省 slot 给真正项目 |

---

## 从 v5 迁移清单

- [ ] 把 70+ 概念项目归档到 archive/
- [ ] 正在跑的 dispatch 任务跑完不续
- [ ] 新项目统一走 P0-P5 流程
- [ ] Research 任务从 dispatch 队列移除
- [ ] Open Source Atlas 作为 P1 的数据库
