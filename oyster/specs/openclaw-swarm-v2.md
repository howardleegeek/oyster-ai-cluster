# OpenClaw Agent Swarm V2 — 智能集群升级

## 背景
当前 5 agent swarm 本质上是 5 个独立 cron job，互不通信、频繁失败、无汇报机制。
需要升级为真正的"智能集群"：共享上下文、互相协作、自动汇报。

## 当前问题诊断

| 问题 | 根因 | 影响 |
|------|------|------|
| Researcher 零产出 | Kimi API cooldown + isolated session | 完全无用 |
| Content 草稿没人用 | 无接入 twitter-poster | 白生成 |
| Monitor 无输出 | Cerebras 400 error + prompt 太模糊 | 看不到系统状态 |
| BD 连续5次error | Kimi API cooldown | 最好的 agent 也跑不了 |
| Agent 互不知道 | 无共享上下文/event bus | 各做各的 |
| Howard 不知道状态 | delivery mode = none | 跑没跑、成没成功都不知道 |

## 升级方案 (5 个改动)

### 改动 1: 修 API 可靠性 — 多 provider 自动切换

**问题**: Kimi API 限速导致 auth profile cooldown，3/5 agent 失败。

**方案**:
- 给每个非 monitor agent 设置多个 primary model 轮换
- 优先级: Kimi K2.5 → Cerebras Llama 3.3 70B (free) → DeepSeek R1 (free) → Qwen3 Coder (free)
- 确认 fallback chain 已在 defaults 里配了（已有），但需要确认 agent 级别的 model config 是否覆盖了 defaults
- Monitor agent: 换用 Cerebras Llama 3.3 70B (比 3.1 8B 更可靠)

**具体修改 `~/.openclaw/openclaw.json`**:
```json
// researcher agent - 删除 model override，使用 defaults 的 fallback chain
{
  "id": "researcher",
  "workspace": "/Users/howardli/.openclaw/agents/researcher/workspace"
  // 不再设 model.primary，用 defaults 的 kimi + fallback chain
}

// content agent - 同上
{
  "id": "content",
  "workspace": "/Users/howardli/.openclaw/agents/content/workspace"
}

// bd agent - 同上
{
  "id": "bd",
  "workspace": "/Users/howardli/.openclaw/agents/bd/workspace"
}

// monitor agent - 升级到 70B
{
  "id": "monitor",
  "workspace": "/Users/howardli/.openclaw/agents/monitor/workspace",
  "model": {
    "primary": "cerebras/llama-3.3-70b"
  }
}
```

**验证**: `openclaw cron list` 所有 job 应该不再出现 "auth profile cooldown" error。

---

### 改动 2: 共享状态 — 建立 shared/ 事件总线

**问题**: Agent 之间无法通信。researcher 发现的热点 content 不知道，bd 需要的数据 researcher 不给。

**方案**: 创建 `~/.openclaw/workspace/shared/` 作为 agent 间的"公告栏"。

**目录结构**:
```
~/.openclaw/workspace/shared/
├── events.jsonl          # 事件总线 (append-only)
├── context.md            # 当前公司状态摘要 (每日更新)
├── hot-topics.md         # researcher 发现的热点 → content 消费
├── leads.md              # researcher/bd 共享的潜在合作/投资线索
└── health-report.md      # monitor 写的最新系统状态
```

**events.jsonl 格式** (每行一个事件):
```json
{"ts": "2026-02-11T10:00:00Z", "from": "researcher", "type": "HOT_TOPIC", "data": {"topic": "Solana DePIN TVL突破$2B", "urgency": "high"}}
{"ts": "2026-02-11T10:05:00Z", "from": "monitor", "type": "ALERT", "data": {"service": "relay", "status": "down", "node": "mac-2"}}
{"ts": "2026-02-11T12:00:00Z", "from": "content", "type": "DRAFT_READY", "data": {"account": "@ClawGlasses", "file": "drafts/2026-02-11-clawglasses.md"}}
{"ts": "2026-02-11T14:00:00Z", "from": "bd", "type": "LEAD", "data": {"name": "Framework Ventures", "source": "x402 hackathon", "priority": "A"}}
```

**Agent 读写规则**:
- 每个 agent 跑时先 `read shared/events.jsonl | tail -50` 看最近事件
- 每个 agent 跑时先 `read shared/context.md` 了解公司当前状态
- 产出有价值信息时 append 到 events.jsonl
- researcher 更新 hot-topics.md，bd 更新 leads.md，monitor 更新 health-report.md

**context.md 模板** (main agent 每天 9am 更新):
```markdown
# Oyster Labs 当前状态
更新时间: 2026-02-11 09:00 PST

## 公司
- 40K+ phones sold, 70K DePIN users
- Products: ClawPhones, ClawGlasses, Puffy
- $WORLD token 生态

## 本周重点
- x402 Hackathon (Feb 11-14) — 正在进行
- Solana AI Hackathon (Feb 12) — 明天开始
- ClawPhones Sprint 10 完成，准备上线

## Twitter 账号定位
- @ClawGlasses: 产品技术 (AR眼镜 + AI Agent)
- @Oysterecosystem: 生态 (DePIN + token economy)
- @UBSphone: 用户故事 (Universal Phone 体验)
- @Puffy_ai: 社区 (meme + 互动 + 活动)

## 竞品关注
- Frame (AI眼镜), Brilliant Labs, Meta Orion
- DIMO, Hivemapper (DePIN 同行)

## 融资状态
- 目标投资人: Multicoin, Polychain, Framework
- Pitch 材料已准备
```

---

### 改动 3: 重写 Cron Job Prompts — 精准指令 + 共享上下文

**问题**: 当前 prompt 太泛 ("查看 AGENTS.md 了解你的职责")，agent 不知道具体要做什么。

**方案**: 每个 cron job 的 message 重写为精准的、带共享上下文读取的指令。

**Monitor (每30min)**:
```
你是 Oyster Labs 系统监控 agent。

执行以下检查:
1. 运行 `ps aux | grep -E "openclaw|relay|dashboard|caffeinate" | grep -v grep` 检查服务进程
2. 运行 `df -h / | tail -1` 检查磁盘
3. 运行 `vm_stat | head -5` 检查内存
4. 运行 `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:18789/health` 检查 gateway
5. 读取 ~/.openclaw/cron/jobs.json 检查各 cron job 最新状态

输出格式 — 写入 /Users/howardli/.openclaw/workspace/shared/health-report.md:
```markdown
# 系统状态 [时间戳]
## 服务
- Gateway (18789): ✅/❌
- Relay (8787): ✅/❌
- Dashboard (3456): ✅/❌
## 资源
- 磁盘: XX% used
- 内存: XX% used
## Cron Jobs
- monitor: ✅ last ok Xm ago
- content: ✅/❌ last status
- researcher: ✅/❌ last status
- bd: ✅/❌ last status
- daily-briefing: next run at XX
## 告警
- [如有异常列出]
```

如果发现异常，同时 append 一行到 /Users/howardli/.openclaw/workspace/shared/events.jsonl:
{"ts":"[ISO时间]","from":"monitor","type":"ALERT","data":{"issue":"[问题描述]"}}
```

**Researcher (每4h)**:
```
你是 Oyster Labs 行业研究 agent。

先读取共享上下文:
1. read /Users/howardli/.openclaw/workspace/shared/context.md — 了解公司当前状态
2. read /Users/howardli/.openclaw/workspace/shared/events.jsonl 最后20行 — 看其他 agent 的最新动态

然后执行研究任务:
1. 搜索 DePIN/Web3/AI Agent 行业最新动态 (过去4小时)
2. 关注竞品: Frame, Brilliant Labs, Meta Orion, DIMO, Hivemapper
3. 关注生态: Solana DePIN, AI Agent frameworks, token economy 趋势
4. 找到 2-3 条最有价值的情报

输出:
1. 更新 /Users/howardli/.openclaw/workspace/shared/hot-topics.md — 覆盖写入最新 top 5 热点
2. 如果发现投资/合作线索 → append 到 /Users/howardli/.openclaw/workspace/shared/leads.md
3. 每条热点 append 到 events.jsonl: {"ts":"...","from":"researcher","type":"HOT_TOPIC","data":{"topic":"...","source":"...","relevance":"high/medium"}}
4. 写详细报告到自己 workspace: /Users/howardli/.openclaw/agents/researcher/workspace/reports/[日期].md
```

**Content (每2h)**:
```
你是 Oyster Labs Twitter 内容创作 agent。

先读取共享上下文:
1. read /Users/howardli/.openclaw/workspace/shared/context.md — 公司状态
2. read /Users/howardli/.openclaw/workspace/shared/hot-topics.md — researcher 发现的热点
3. read /Users/howardli/.openclaw/workspace/shared/events.jsonl 最后20行 — 最新事件

然后为 4 个账号各生成 1 条推文草稿:
- @ClawGlasses: 产品技术向 (AR + AI Agent, 专业但不晦涩)
- @Oysterecosystem: 生态叙事 (DePIN + token, 数据驱动)
- @UBSphone: 用户故事 (真实场景, 情感共鸣)
- @Puffy_ai: 社区互动 (meme 风格, 轻松有趣, 可带投票/提问)

规则:
- 必须基于 hot-topics.md 里的真实热点，不编造数据
- 每条推文 < 280 字符
- 包含 1-2 个相关 hashtag
- 不用 emoji 过度

输出到 /Users/howardli/.openclaw/agents/content/workspace/drafts/[日期]-[时间].md
格式:
```markdown
# Twitter Drafts [时间]
## @ClawGlasses
[推文内容]

## @Oysterecosystem
[推文内容]

## @UBSphone
[推文内容]

## @Puffy_ai
[推文内容]

---
Sources: [引用的 hot-topics]
```

然后 append 到 events.jsonl: {"ts":"...","from":"content","type":"DRAFT_READY","data":{"file":"drafts/[文件名]","accounts":4}}
```

**BD (每6h)**:
```
你是 Oyster Labs BD (商务拓展) agent。

先读取共享上下文:
1. read /Users/howardli/.openclaw/workspace/shared/context.md — 公司状态
2. read /Users/howardli/.openclaw/workspace/shared/leads.md — researcher 发现的线索
3. read /Users/howardli/.openclaw/workspace/shared/events.jsonl 最后20行

然后执行 BD 任务:
1. 基于 leads.md 的新线索，评估优先级 (A/B/C)
2. 为 A 级线索准备 outreach 邮件草稿
3. 更新投资人/合作伙伴跟踪表
4. 关注即将到来的活动 (hackathon, conference) 的 networking 机会

输出:
1. 更新 /Users/howardli/.openclaw/workspace/shared/leads.md — 添加评估和状态
2. 写邮件草稿到 /Users/howardli/.openclaw/agents/bd/workspace/outreach/[日期].md
3. append events.jsonl: {"ts":"...","from":"bd","type":"OUTREACH_READY","data":{"leads_processed":N,"emails_drafted":N}}
```

**Daily Briefing (每天9am)**:
```
你是 Oyster Labs 日报 agent (OC-main)。

读取所有共享数据:
1. read /Users/howardli/.openclaw/workspace/shared/events.jsonl — 过去24小时所有事件
2. read /Users/howardli/.openclaw/workspace/shared/health-report.md — 最新系统状态
3. read /Users/howardli/.openclaw/workspace/shared/hot-topics.md — 行业热点
4. read /Users/howardli/.openclaw/workspace/shared/leads.md — BD 线索

生成日报并写入 /Users/howardli/.openclaw/workspace/shared/context.md (覆盖，保持最新):
按 context.md 的模板格式更新公司状态。

同时生成给 Howard 的简报写入 /Users/howardli/.openclaw/agents/main/workspace/briefings/[日期].md:
```markdown
# 🌅 Oyster Labs 每日简报 — [日期]

## 📊 过去 24 小时
- **Researcher**: [发现了什么/没跑成功]
- **Content**: [生成了几条草稿/待发布]
- **BD**: [处理了几个线索/邮件草稿]
- **Monitor**: [系统状态摘要]

## 🔥 热点 (来自 researcher)
1. [热点1]
2. [热点2]

## 📋 今日行动项
1. [最重要的事]
2. [第二重要]
3. [第三重要]

## ⚠️ 需要 Howard 决策
- [如果有需要人工决策的事项]

## 🎯 本周目标进展
- [进展]
```
```

---

### 改动 4: 开启汇报 — Telegram 通知

**问题**: delivery mode 全是 `"none"`，Howard 不知道 agent 跑没跑。

**方案**:
- Daily Briefing: 开启 Telegram 推送 (已有 bot token)
- Monitor: 仅在发现异常时推送
- 其余 agent: 不推送 (避免噪音)，结果通过 events.jsonl → daily briefing 汇总

**修改 cron/jobs.json**:
- daily-briefing: `"delivery": {"mode": "channel", "channel": "telegram"}`
- 其余保持 `"none"`

**同时**: 在 openclaw.json 里启用 telegram channel:
```json
"channels": {
  "telegram": {
    "enabled": true,  // 已经是 true
    ...
  }
}
```

---

### 改动 5: Session 模式 — 从 isolated 改为 continue

**问题**: `"sessionTarget": "isolated"` 导致每次跑完上下文丢失。agent 不记得上次做了什么。

**方案**:
- researcher/content/bd: 改为 `"sessionTarget": "continue"` — 保持上下文连续性
- monitor: 保持 `"isolated"` — 每次独立检查，不需要上下文
- daily-briefing: 保持 `"isolated"` — 每天全新汇总

**注意**: continue 模式下上下文会膨胀，需要设置 `maxTurns` 或定期 reset。
建议 researcher/content/bd 设 `"maxSessionTurns": 20`，超过后自动新建 session。

---

## 执行步骤

### Step 1: 创建共享目录和初始文件
```bash
mkdir -p /Users/howardli/.openclaw/workspace/shared
mkdir -p /Users/howardli/.openclaw/agents/researcher/workspace/reports
mkdir -p /Users/howardli/.openclaw/agents/content/workspace/drafts
mkdir -p /Users/howardli/.openclaw/agents/bd/workspace/outreach
mkdir -p /Users/howardli/.openclaw/agents/main/workspace/briefings
```

创建 context.md 初始内容 (见上面模板)。
创建空的 events.jsonl, hot-topics.md, leads.md, health-report.md。

### Step 2: 修改 openclaw.json
- 删除 researcher/content/bd 的 model override (用 defaults fallback chain)
- 升级 monitor model 到 cerebras/llama-3.3-70b

### Step 3: 重写 cron/jobs.json
- 用上面的精准 prompt 替换当前模糊 prompt
- daily-briefing 开启 telegram delivery
- researcher/content/bd 改 sessionTarget 为 continue

### Step 4: 重启 gateway
```bash
launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway
```

### Step 5: 验证
- `openclaw cron list` — 确认所有 job enabled + 无 error
- 等 30min 后检查 monitor 有没有写 health-report.md
- 等 2h 后检查 content 有没有读 hot-topics 生成草稿
- 等 4h 后检查 researcher 有没有产出

## 验收标准
- [ ] `shared/` 目录存在且有初始文件
- [ ] openclaw.json 中 researcher/content/bd 无 model override
- [ ] monitor model 升级到 llama-3.3-70b
- [ ] 所有 5 个 cron job prompt 已重写
- [ ] daily-briefing delivery 改为 telegram
- [ ] researcher/content/bd sessionTarget 改为 continue
- [ ] gateway 重启成功，`openclaw cron list` 无 error
- [ ] 30min 后 health-report.md 有内容
