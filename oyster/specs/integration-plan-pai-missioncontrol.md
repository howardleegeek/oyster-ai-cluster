# 集成计划：PAI + Mission Control + 现有系统

> 目标：让 67 个 agent (30 OpenClaw + 37 Dispatch) 变智能 + 可视化管控
> 执行者：Codex
> 预计时间：2-3 小时

---

## 现有系统清单

| 系统 | 位置 | Agent 数 | 状态 |
|------|------|---------|------|
| OpenClaw (Mac-1) | ~/.openclaw/ | 25 | gateway + node 运行中 |
| OpenClaw (Mac-2) | ~/.openclaw/ | 5 | node + 5 slots 运行中 |
| Dispatch Slot Agents | 4 GCP + Mac-2 | 37 | slot_agent.py 部分运行 |
| PAI | ~/Downloads/PAI/ | 新装 | 待安装 |
| Mission Control | 待装 (Docker) | - | 待部署 |

---

## Phase 1: 安装 PAI (30 min)

### 1.1 安装 PAI 到 ~/.claude/

```bash
cd ~/Downloads/PAI/Releases/v2.5
# 已备份 ~/.claude → ~/.claude-backup-20260213
cp -r .claude ~/
cd ~/.claude && bun run PAIInstallWizard.ts
```

配置参数：
- Name: Howard Li
- Assistant Name: Oyster AI
- Timezone: Asia/Shanghai (或 America/Los_Angeles)
- Audio: 关闭 (GCP 节点没音频)

### 1.2 合并旧配置回来

从 `~/.claude-backup-20260213/` 复制回：
- `plugins/` → 合并到新 `~/.claude/plugins/`
- `skills/` → 合并到新 `~/.claude/skills/`
- `CLAUDE.md` → 合并关键内容到 PAI 的 CLAUDE.md（保留 Opus 铁律、指挥矩阵、dispatch 命令）
- `projects/` → 直接复制回
- `settings.json` → 对比合并

### 1.3 创建 TELOS 文件

PAI 的核心 — 在 `~/.claude/TELOS/` 创建：

**identity.md**:
```markdown
# Howard Li
- CEO, Oyster Labs
- 构建 Web3 + AI 硬件生态
- 工作到凌晨 3-4 点，偏好直接沟通
- 中英文混合
```

**goals.md**:
```markdown
# 2026 Q1 Goals
1. ClawPhones 上线 App Store
2. GEM Platform 验收到 95+
3. Oysterworld MVP 上线
4. 代码工厂日产 100+ PR
5. 融资 Pre-A 轮
```

**projects.md**:
```markdown
# Active Projects
- ClawPhones: iOS/Android AI 手机应用
- GEM Platform: Web3 平台
- Oysterworld: Living World Model
- ClawMarketing: 营销自动化
- Twitter/Discord: 社交运营
```

**beliefs.md**:
```markdown
# 技术信念
- AI 应该放大每个人，不只是 top 1%
- 好 spec > 好模型
- 失败 2 次换方案
- 基础设施冻结，不折腾
- M2.5 执行强但不做规划
```

**mental-models.md**:
```markdown
# 决策模型
- 将军/特种兵/步兵：Codex 规划、M2.5 执行、GLM 补量
- 一次只做一个 feature
- 先验证再进下一步
- Opus 铁律：不写代码、不微管理、不碰基础设施
```

---

## Phase 2: 安装 Mission Control (30 min)

### 2.1 克隆并部署

```bash
cd ~/Downloads
git clone https://github.com/abhi1693/openclaw-mission-control.git
cd openclaw-mission-control
# 按 README 运行安装脚本或 docker compose up
docker compose up -d
```

### 2.2 配置 Mission Control 连接 OpenClaw

Mission Control 需要连接 OpenClaw gateway：
- Mac-1 gateway: localhost:18789
- Mac-2 gateway: (如有)

在 Mission Control 的配置中添加：
- Organization: Oyster Labs
- Gateway 1: Mac-1 (localhost:18789, token: 46b129eeb24d2cf5e577f3ea4593281fb2f791f42dfb886c)
- Gateway 2: Mac-2 (通过 Tailscale)

### 2.3 注册所有 Agent

在 Mission Control 中注册：
- 5 个核心 agent (main, researcher, content, bd, monitor)
- 20 个 workflow agent (bug-fix, feature-dev, security-audit 三条流水线)
- 37 个 dispatch slot agent (按节点分组)

---

## Phase 3: 集成 (1-2 小时)

### 3.1 PAI TELOS → OpenClaw Agent SOUL.md

**目标**：用 PAI 的 TELOS 替代 OpenClaw 现有的泛泛 SOUL.md

对每个 OpenClaw agent：
1. 读取 `~/.claude/TELOS/` 中的目标和信念
2. 生成专属 SOUL.md，只包含该 agent 需要的上下文
3. 写入 `~/.openclaw/agents/<agent-id>/workspace/SOUL.md`

**规则**：
- main agent: 完整 TELOS
- researcher: goals + projects + mental-models
- content: goals + identity (品牌调性)
- bd: goals + identity + beliefs
- monitor: 只需 projects 列表
- workflow agents: 只需 projects + 相关 spec

### 3.2 PAI Hook System → OpenClaw Heartbeat 增强

**目标**：让 agent 每次任务后自动学习

在 OpenClaw 的 heartbeat 机制中加入 PAI hook：
- `on_task_complete`: 提取经验 → 写入 memory
- `on_task_fail`: 分析原因 → 更新 beliefs
- `on_session_start`: 加载最近 warm memory
- `on_session_end`: 压缩 hot → warm

### 3.3 PAI Memory → Dispatch Slot Agent

**目标**：让 37 个 slot agent 共享记忆

修改 `slot_agent.py` 的 `understand_intent` 方法：
1. 执行前先查 PAI memory（warm 层）获取相关上下文
2. 执行后将学到的经验写入 memory
3. memory 存储位置：Mac-1 的 `~/.claude/MEMORY/` (通过 SSH 同步)

### 3.4 Mission Control → Dispatch 状态同步

**目标**：在 Mission Control 面板上看到所有 67 个 agent 的实时状态

方案：
1. dispatch.py 的 `status` 命令输出 JSON
2. 写一个 bridge 脚本，定时把 dispatch 状态推送到 Mission Control API
3. 频率：每 30 秒

```python
# bridge_dispatch_to_mc.py
import subprocess, requests, json, time

while True:
    # 获取 dispatch 状态
    result = subprocess.run(
        ["python3", "dispatch.py", "status", "--json"],
        capture_output=True, text=True
    )
    status = json.loads(result.stdout)

    # 推送到 Mission Control
    requests.post("http://localhost:PORT/api/agents/status", json=status)

    time.sleep(30)
```

---

## Phase 4: 验证

### 检查清单

- [ ] PAI 安装完成，TELOS 文件齐全
- [ ] ~/.claude/ 旧配置已合并回来（skills, plugins, projects）
- [ ] Mission Control Docker 容器运行中
- [ ] Mission Control 能看到 OpenClaw gateway
- [ ] Mission Control 能看到所有 agent
- [ ] OpenClaw agent 的 SOUL.md 已更新（基于 TELOS）
- [ ] PAI hook 在任务完成后触发学习
- [ ] Dispatch slot agent 能读 PAI memory
- [ ] 从 Mission Control 面板能看到 dispatch 任务状态

---

## 不做的事

- ❌ 不重构 dispatch.py 或 slot_agent.py 架构
- ❌ 不改 SSH/节点配置
- ❌ 不换模型（M2.5 继续做执行）
- ❌ 不改 OpenClaw gateway 配置
- ❌ 不新增 npm 依赖到 OpenClaw
