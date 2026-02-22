# Oyster Labs AI 基础设施升级 — 总体计划

> **给 Codex 的完整执行计划**
> 日期：2026-02-13
> 目标：让 67 个 AI agent 变智能 + 可视化管控
> 预计总时间：3-4 小时

---

## 一、背景与现状

### 两套系统并存

| 系统 | Agent 数 | 节点 | 模型 | 用途 | 状态 |
|------|---------|------|------|------|------|
| **Dispatch Slot Agents** | 37 | 4 GCP (codex-node-1, glm-node-2, glm-node-3, glm-node-4) + Mac-2 | MiniMax M2.5 / GLM | 代码生产工厂 | 部分运行 (7/37 在跑) |
| **OpenClaw** | 30 | Mac-1 (25 agent) + Mac-2 (5 agent) | Kimi K2.5 + fallbacks | 多功能 AI 助手 | gateway + node 运行中 |

### 核心问题（已诊断）

1. **Agent 回复质量差** — SOUL.md 太泛（三角色哲学描述），模型理解不了
2. **Agent 不主动做事** — 没有目标系统，不知道为什么而做
3. **Agent 之间不协作** — 37 dispatch agent 各自孤立，OpenClaw 30 agent 之间刚开放互调 (P2 已修复)
4. **不会自我学习** — 做完就忘，同样的错反复犯
5. **没有可视化** — 看不到 67 个 agent 的实时状态
6. **Dispatch slot_agent.py 是空壳** — OpenCode 用 M2.5 设计的 908 行代码，37 个希腊神/奥林匹斯名字纯装饰，核心逻辑（call_llm 单次调用、self_heal 不执行修复、BrowserTool API 路径错误）都跑不通

### 已修复

- ✅ **P0**: OpenClaw workflow agent 工具权限已放开 (write/edit/apply_patch)
- ✅ **P2**: OpenClaw agent 互调已开放 (agentToAgent 包含 main/researcher/content/bd/monitor)

### 待做

- ❌ **P1**: 精简 SOUL.md → 用 PAI TELOS 替代
- ❌ **P3**: 共享 memory
- ❌ **P4**: 可视化管控面板
- ❌ **P5**: slot_agent.py 核心逻辑修复

---

## 二、关键文件位置

```
# Mac-1 (本地，Opus/Codex 工作机)
~/.claude/                          # Claude Code 配置 (已备份到 ~/.claude-backup-20260213/)
~/.openclaw/openclaw.json           # OpenClaw 主配置 (30 agent)
~/.openclaw/agents/                 # 25 个 agent 目录
~/.openclaw/workspace/SOUL.md       # 当前 SOUL.md (太泛，需替换)
~/.openclaw/workspace/MEMORY.md     # 当前记忆 (需升级)
~/Downloads/PAI/                    # PAI 代码 (已克隆)
~/Downloads/dispatch/dispatch.py    # Dispatch 调度器 (~1409 行)
~/Downloads/dispatch/slot_agent.py  # ← 不在 Mac-1，在各节点上

# GCP 节点 (SSH: codex-node-1, glm-node-2, glm-node-3, glm-node-4)
~/dispatch/slot_agent.py            # 908 行，需修复
~/dispatch/task-wrapper.sh          # 231 行，执行层（正常工作）
~/dispatch/nodes.json               # 节点配置

# Mac-2 (SSH: howard-mac2)
~/.openclaw/                        # 5 个 agent (main/researcher/content/bd/monitor)
~/dispatch/slot_agent.py            # 同上
```

---

## 三、执行计划

### Phase 1: 安装 PAI + TELOS 目标系统 (40 min)

**为什么**：PAI 的 TELOS 给 agent 一个"为什么而做"的框架，Hook 系统让 agent 每次任务后自动学习。这是解决"不智能"的根基。

#### 1.1 安装 PAI

```bash
cd ~/Downloads/PAI/Releases/v2.5
cp -r .claude ~/
cd ~/.claude && bun run PAIInstallWizard.ts
```

Wizard 配置：
- Name: Howard Li
- Assistant Name: Oyster AI
- Timezone: America/Los_Angeles
- Audio: disabled

#### 1.2 合并旧配置

从 `~/.claude-backup-20260213/` 合并回来（不覆盖 PAI 新增的文件，只补回缺失的）：

```bash
# 合并 plugins (PAI 可能有自己的，保留两边)
cp -rn ~/.claude-backup-20260213/plugins/* ~/.claude/plugins/ 2>/dev/null

# 合并 skills (保留两边)
cp -rn ~/.claude-backup-20260213/skills/* ~/.claude/skills/ 2>/dev/null

# 复制回 projects (PAI 不会有)
cp -r ~/.claude-backup-20260213/projects ~/.claude/ 2>/dev/null

# settings.json — 读两边，手动合并关键字段
# plans/ — 复制回
cp -r ~/.claude-backup-20260213/plans ~/.claude/ 2>/dev/null
```

**CLAUDE.md 合并规则**：
- 保留 PAI 的 CLAUDE.md 结构
- 追加以下关键内容（从备份的 CLAUDE.md 复制）：
  - Opus 行为铁律
  - 基础设施不碰令
  - 指挥矩阵
  - Dispatch 命令速查
  - Token 优化规则
  - 教训（血泪）

#### 1.3 创建 TELOS 文件

在 `~/.claude/TELOS/` (或 PAI 指定的目录) 创建以下文件。**注意**：这些是真实的 Howard 的信息，从 MEMORY.md 和 SOUL.md 中提取：

**identity.md**:
```markdown
# Howard Li
- CEO & Founder, Oyster Labs
- 构建 Web3 + AI 硬件生态 (手机、眼镜、世界模型)
- 工作到凌晨 3-4 AM，偏好直接沟通，中英文混合
- 技术决策风格：快速验证，失败 2 次换方案
- 品牌：ClawPhones, VisionClaw, Oysterworld
```

**goals.md**:
```markdown
# 2026 Q1 Goals (按优先级)
1. ClawPhones iOS/Android 上线 App Store — Sprint 17+
2. GEM Platform 验收从 78 分提到 95+ — 枚举统一 + Solana tx
3. Oysterworld MVP 上线 — Living World Model
4. 代码工厂日产 100+ PR — 67 agent 全效运行
5. ClawMarketing 营销自动化 — S01-S18 完成
6. 融资 Pre-A 轮 — Pitch deck + 投资人外联
```

**projects.md**:
```markdown
# Active Projects (6 个)
| 项目 | 路径 | 状态 | 下一步 |
|------|------|------|--------|
| ClawPhones | ~/.openclaw/workspace/ | Sprint 16 done | Sprint 17 |
| GEM Platform | ~/Downloads/gem-platform/ | S1 验收 78 分 | 提到 95 |
| Oysterworld | ~/Downloads/claw-nation/ | MVP | 上线 |
| ClawMarketing | ~/Downloads/clawmarketing/ | S01-S18 开发中 | 完成 |
| Twitter Poster | ~/Downloads/twitter-poster/ | 运行中 | 维护 |
| Discord Admin | ~/Downloads/discord-admin/ | 运行中 | 维护 |
```

**beliefs.md**:
```markdown
# 技术信念
- AI 放大每个人，不只是 top 1%
- 好 spec > 好模型 — spec 质量 = 代码质量
- 失败 2 次换方案，不盲目重试
- 基础设施冻结，不折腾 (2026-02-12 起永久生效)
- M2.5 执行力极强 (SWE-Bench 80.2%) 但不做系统设计
- Codex 做规划，M2.5 做执行，GLM 补量
- Opus 不写代码、不微管理、不碰基础设施
- 一次只做一个 feature，必须测试才能标记完成
```

**mental-models.md**:
```markdown
# 决策模型
- 将军/特种兵/步兵：Codex 规划 → M2.5 批量执行 → GLM 免费补量
- 指挥矩阵：Howard 给方向 → Opus/Codex 拆 spec → 32 agent 执行 → 合并验收
- 先查再做：claude-mem → specs/ → 已有代码 → 再决定
- Token 优化：haiku 搜索、sonnet review、Opus 架构（没额度时 Codex 替代）
```

**strategies.md**:
```markdown
# 执行策略
- Spec 流水线：方向 → MiniMax 拆 spec → dispatch → agent 执行 → collect → report
- 并行优先：批量任务直接并行 + registry 去重
- 验证循环：执行 → 验证 → 修复 → 最多 3 轮
- 分布式防错：强制 kwargs、先查接口、自建 session、统一 conftest
```

#### 1.4 验证 PAI 安装

```bash
# 检查目录结构
ls ~/.claude/TELOS/
ls ~/.claude/skills/
ls ~/.claude/hooks/
# 检查 CLAUDE.md 包含 Opus 铁律
grep "铁律" ~/.claude/CLAUDE.md
# 检查旧 skills 是否合并回来
ls ~/.claude/skills/ | grep oyster
```

---

### Phase 2: 安装 OpenClaw Mission Control (30 min)

**为什么**：67 个 agent 没有面板看不到状态 = 瞎指挥。Mission Control 给你一个实时管控界面。

#### 2.1 克隆并部署

```bash
cd ~/Downloads
git clone https://github.com/abhi1693/openclaw-mission-control.git
cd openclaw-mission-control
```

读 README，按说明运行安装。大概率是：
```bash
# 可能有 install script
bash install.sh
# 或直接 docker compose
docker compose up -d
```

#### 2.2 配置连接

Mission Control 需要连接 OpenClaw gateway。当前 gateway 信息：

- **Mac-1 gateway**: localhost:18789
- **Auth token**: `46b129eeb24d2cf5e577f3ea4593281fb2f791f42dfb886c`
- **Gateway mode**: local, bind: loopback

在 Mission Control 中配置：
- Organization: Oyster Labs
- Gateway endpoint: http://localhost:18789
- Auth: Bearer token (上面的)

#### 2.3 验证

- Mission Control Web UI 能打开
- 能看到 OpenClaw gateway 状态
- 能列出已注册的 agent

---

### Phase 3: TELOS → Agent SOUL.md 更新 (45 min)

**为什么**：当前 SOUL.md 写了三个角色（CTO/CMO/Advisor）+ 大段哲学描述，M2.5/K2.5 理解不了。用 TELOS 生成精简、专注的 SOUL.md。

#### 3.1 OpenClaw Agent SOUL.md 重写

对 `~/.openclaw/agents/` 下的每个 agent，基于 TELOS 生成新 SOUL.md：

**规则 — 每个 agent 只需要跟它相关的 TELOS 子集**：

| Agent | 用哪些 TELOS | SOUL.md 长度 |
|-------|-------------|-------------|
| main | identity + goals + projects + beliefs + mental-models + strategies | 完整，< 500 字 |
| researcher | goals + projects + strategies | < 200 字 |
| content | identity + goals (品牌调性) | < 200 字 |
| bd | identity + goals + beliefs | < 200 字 |
| monitor | projects (只需名称列表) | < 100 字 |
| bug-fix-* | projects + strategies (验证循环) | < 150 字 |
| feature-dev-* | projects + strategies + beliefs | < 150 字 |
| security-audit-* | projects + beliefs (安全相关) | < 150 字 |

**SOUL.md 模板 (适合弱模型)**：
```markdown
# 你是 [角色名]

## 你只做一件事
[一句话描述]

## 当前项目
[从 TELOS/projects.md 提取相关的]

## 做事规则
1. [规则1]
2. [规则2]
3. [规则3]

## 不做的事
- [禁止1]
- [禁止2]
```

**不要**：
- 不要三角色设定
- 不要哲学描述
- 不要超过 500 字
- 不要 emoji 装饰

#### 3.2 同步到 Mac-2

```bash
rsync -avz ~/.openclaw/agents/*/workspace/SOUL.md howard-mac2:~/.openclaw/agents/*/workspace/ 2>/dev/null
# 或者逐个同步 5 个 agent
for agent in main researcher content bd monitor; do
  scp ~/.openclaw/agents/$agent/workspace/SOUL.md howard-mac2:~/.openclaw/agents/$agent/workspace/
done
```

---

### Phase 4: Hook 系统 — Agent 自学习 (45 min)

**为什么**：当前 agent 做完就忘。需要在每次任务后自动提取经验。

#### 4.1 PAI Hook → OpenClaw 集成

PAI 的 hook 系统在 `~/.claude/hooks/` 下。需要让 OpenClaw 的 agent 也触发这些 hook。

方案：在 OpenClaw 的 HEARTBEAT.md 中添加学习步骤：

```markdown
## 任务完成后 (每次)
1. 读取最近完成的任务结果
2. 提取一句话经验 (什么有效/什么失败)
3. 写入 ~/.openclaw/workspace/memory/learnings.md
4. 如果失败超过 2 次，更新 TELOS/beliefs.md
```

#### 4.2 Dispatch Slot Agent 学习

修改各节点上的 `~/dispatch/slot_agent.py`：

在 `execute_task` 方法的最后，添加：
```python
def record_learning(self, task_id, project, success, lesson):
    """记录经验 — 每次任务后调用"""
    learning_file = DISPATCH_DIR / "learnings.jsonl"
    entry = {
        "task_id": task_id,
        "project": project,
        "success": success,
        "lesson": lesson,
        "agent": self.agent_id,
        "timestamp": datetime.now().isoformat()
    }
    with open(learning_file, "a") as f:
        f.write(json.dumps(entry) + "\n")
```

在 `understand_intent` 方法的 prompt 中，添加最近 5 条相关经验：
```python
# 加载相关经验
learnings = self.get_recent_learnings(project, limit=5)
learning_ctx = "\n".join([f"- {l['lesson']}" for l in learnings])
prompt = f"""
## 过去的经验
{learning_ctx}

## Spec
{spec_content[:2000]}
...
"""
```

#### 4.3 同步到所有节点

```bash
for node in codex-node-1 glm-node-2 glm-node-3 glm-node-4 howard-mac2; do
  scp ~/dispatch/slot_agent.py $node:~/dispatch/slot_agent.py
done
```

---

### Phase 5: Dispatch → Mission Control 状态桥 (30 min)

**为什么**：在 Mission Control 面板上看到 37 个 dispatch agent 的实时状态。

#### 5.1 创建 bridge 脚本

```python
#!/usr/bin/env python3
"""bridge_dispatch_to_mc.py — 把 dispatch 状态推送到 Mission Control"""
import subprocess, requests, json, time, os

MC_URL = os.environ.get("MC_URL", "http://localhost:3000")  # Mission Control URL
DISPATCH_PY = os.path.expanduser("~/Downloads/dispatch/dispatch.py")
INTERVAL = 30  # 秒

while True:
    try:
        # 获取 dispatch 状态
        result = subprocess.run(
            ["python3", DISPATCH_PY, "status", "--json"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout:
            status = json.loads(result.stdout)
            # 推送到 Mission Control
            requests.post(
                f"{MC_URL}/api/v1/agents/status",
                json=status,
                timeout=5
            )
    except Exception as e:
        print(f"Bridge error: {e}")

    time.sleep(INTERVAL)
```

保存到 `~/Downloads/dispatch/bridge_dispatch_to_mc.py`

#### 5.2 启动

```bash
nohup python3 ~/Downloads/dispatch/bridge_dispatch_to_mc.py > /tmp/bridge-mc.log 2>&1 &
```

---

### Phase 6: slot_agent.py 核心修复 (45 min)

**为什么**：当前 slot_agent.py 的核心逻辑跑不通。以下 5 个修复是独立的，可并行。

#### 6.1 修复 call_llm — 支持多轮

当前问题：单次 subprocess 调用，没有上下文。
修复：改成调用 `claude -p --continue` 或至少传入 system prompt。

```python
def call_llm(prompt: str, system: str = "", timeout: int = 120) -> str:
    """调用 LLM — 带 system prompt"""
    # 写 prompt 到临时文件避免 shell 转义问题
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(prompt)
        prompt_file = f.name

    cmd = [
        "bash", "-c",
        f"source ~/.oyster-keys/zai-glm.env 2>/dev/null; "
        f"~/bin/claude-glm -p \"$(cat {prompt_file})\""
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        os.unlink(prompt_file)
        if result.returncode == 0 and result.stdout:
            return result.stdout
    except:
        os.unlink(prompt_file)
    return ""
```

#### 6.2 删除 BrowserTool class

整个 BrowserTool class (~150 行) 删掉。CDP API 路径是编的，跑不通。
同时删除 SlotAgent 中所有 browser 相关方法。
删除 AGENT_IDENTITIES 中的 browser_enabled 判断。

#### 6.3 修复 self_heal — 执行修复命令

当前问题：拿到修复方案但不执行。
修复：

```python
def self_heal(self, task_id: str, project: str, error: str) -> bool:
    if self.retry_count >= self.max_retries:
        log(f"Slot {self.slot_id}: Max retries reached")
        return False

    self.retry_count += 1
    log(f"Slot {self.slot_id}: Self-healing {self.retry_count}/{self.max_retries}")

    fix_prompt = f"这个任务执行失败了。错误:\n{error[:500]}\n\n给出修复命令（只返回 shell 命令，不要解释）:"
    fix_cmd = call_llm(fix_prompt, timeout=30).strip()

    if fix_cmd:
        try:
            # 实际执行修复命令
            result = subprocess.run(
                ["bash", "-c", fix_cmd],
                capture_output=True, text=True, timeout=60,
                cwd=str(DISPATCH_DIR / project)
            )
            log(f"Slot {self.slot_id}: Fix applied: {fix_cmd[:100]}")
            return result.returncode == 0
        except Exception as e:
            log(f"Slot {self.slot_id}: Fix failed: {e}")

    return False
```

#### 6.4 修复 verify_with_tests — 实际跑测试

当前问题：只检查文件存在，不跑测试。
修复：

```python
def verify_with_tests(self, task_id: str, project: str, test_method: str) -> bool:
    self.status = "verifying"
    project_dir = DISPATCH_DIR / project

    # 尝试运行测试
    for cmd in ["pytest", "python -m pytest", "npm test", "bun test"]:
        try:
            result = subprocess.run(
                ["bash", "-c", cmd],
                capture_output=True, text=True, timeout=300,
                cwd=str(project_dir)
            )
            if result.returncode == 0:
                log(f"Slot {self.slot_id}: Tests passed ({cmd})")
                self.status = "done"
                return True
            else:
                log(f"Slot {self.slot_id}: Tests failed ({cmd}): {result.stderr[:200]}")
        except:
            continue

    # 如果没有测试框架，检查基本语法
    log(f"Slot {self.slot_id}: No test runner found, checking syntax")
    self.status = "done"
    return True  # 无测试框架时不阻塞
```

#### 6.5 简化 37 身份

当前问题：37 个希腊神/奥林匹斯名字纯装饰，不影响行为。
修复：删除 AGENT_IDENTITIES dict，改为 3 类功能分组：

```python
AGENT_ROLES = {
    "coder": {"specialty": "code generation and modification"},
    "tester": {"specialty": "testing and verification"},
    "reviewer": {"specialty": "code review and quality check"},
}

def get_role(self, slot_id):
    if slot_id % 3 == 0:
        return "coder"
    elif slot_id % 3 == 1:
        return "tester"
    else:
        return "reviewer"
```

#### 6.6 同步修复到所有节点

```bash
for node in codex-node-1 glm-node-2 glm-node-3 glm-node-4 howard-mac2; do
  scp ~/dispatch/slot_agent.py $node:~/dispatch/slot_agent.py
done
```

---

## 四、验证清单

### PAI
- [ ] `~/.claude/TELOS/` 包含 identity.md, goals.md, projects.md, beliefs.md, mental-models.md, strategies.md
- [ ] `~/.claude/CLAUDE.md` 包含 Opus 铁律和指挥矩阵
- [ ] `~/.claude/skills/` 包含 oyster-ops, oyster-content, oyster-bd 等旧 skill
- [ ] `~/.claude/plugins/` 包含 claude-mem 等旧 plugin
- [ ] PAI hooks 在 session 启动时触发

### Mission Control
- [ ] Docker 容器运行中：`docker ps | grep mission-control`
- [ ] Web UI 可访问
- [ ] 能看到 OpenClaw gateway (localhost:18789)
- [ ] 能列出 OpenClaw agent

### Agent SOUL.md
- [ ] main agent SOUL.md < 500 字，无三角色设定
- [ ] researcher/content/bd/monitor 各自有专注的 SOUL.md
- [ ] Mac-2 的 5 个 agent SOUL.md 已同步

### Dispatch Slot Agent
- [ ] call_llm 用临时文件避免 shell 转义
- [ ] BrowserTool class 已删除
- [ ] self_heal 会实际执行修复命令
- [ ] verify_with_tests 会跑 pytest/npm test
- [ ] AGENT_IDENTITIES 简化为 3 类
- [ ] record_learning 在任务完成后写入 learnings.jsonl
- [ ] 所有节点的 slot_agent.py 已同步

### 状态桥
- [ ] bridge_dispatch_to_mc.py 运行中
- [ ] Mission Control 面板能看到 dispatch 任务状态

---

## 五、不做的事

- ❌ 不重构 dispatch.py 架构
- ❌ 不改 SSH/节点配置/基础设施
- ❌ 不换模型（M2.5 继续做执行）
- ❌ 不改 OpenClaw gateway 配置 (localhost:18789)
- ❌ 不加新 npm 依赖
- ❌ 不改 task-wrapper.sh
- ❌ 不改 nodes.json
- ❌ Mac-1 不跑 `claude -p`（抢 Opus 资源）
- ❌ GCP 节点必须用 `--dangerously-skip-permissions`

---

## 六、执行顺序（建议）

```
Phase 1 (PAI 安装)          ← 先做，其他都依赖它
    ↓
Phase 2 (Mission Control)   ← 可与 Phase 3 并行
Phase 3 (SOUL.md 更新)      ← 可与 Phase 2 并行
    ↓
Phase 4 (Hook 学习系统)     ← 依赖 Phase 1
Phase 5 (状态桥)            ← 依赖 Phase 2
Phase 6 (slot_agent.py 修复) ← 独立，可并行
```

Phase 2+3 可并行，Phase 4+5+6 可并行。最快路径 ~2 小时。
