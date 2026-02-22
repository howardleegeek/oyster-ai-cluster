# AI 代码生产体系 v5 — 战略 Spec

> 目标：32 个 agent 生产单元跑满，代码质量好，节点即插即用
> 核心转变：Opus 不写 spec 细节，只给方向；生产单元是自治 agent
> 日期：2026-02-12

---

## 1. 核心模型

```
Howard: "做 X"  (一句话)
         ↓
指挥层 (Opus/MiniMax): 拆成原子 spec (目标+约束+验收标准)
         ↓ spec 队列
调度层 (dispatch v5): DAG 编排，自动分发
         ↓
生产层 (32 agent units): 拿 spec → 分析代码 → 写代码 → 写测试 → 自验证 → 提交
         ↓
合并层: 自动 merge + 质量兜底
```

**核心转变：**
- Opus 不烧 token 写详细 spec → 只给方向 + 关键约束，10 token
- MiniMax 免费拆分 → 原子 spec，每个 5-15min 可完成
- 生产单元不是执行器，是 **自治 agent** — 拿到目标后自己决定怎么实现
- 节点即插即用 — bootstrap.sh 一跑就加入集群

---

## 2. 三层架构

### 2.1 指挥层 — 只产 spec

| 谁 | 做什么 | 不做什么 |
|----|--------|---------|
| **Opus** | 给方向 (一句话)、关键技术决策、最终审批 | 不写代码、不写详细 spec |
| **MiniMax** | 把方向拆成原子 spec、质量门控、code review | 不写代码 |

**Opus 工作示例：**
```
输入: Howard 说 "ClawMarketing 加批量排期功能"
输出:
  方向: "POST /api/v1/posts/schedule, 支持批量排期, 限 50 条/次,
        复用 PostService, 需要鉴权, pytest 覆盖"
  约束: "不动前端, 只改 backend/routers/ 和 backend/schemas/"
```
→ 完事。10 个 token。交给 MiniMax 拆分。

**MiniMax 拆分示例：**
```
输入: Opus 的一句话方向
输出: 8 个原子 spec 文件
  S01-schedule-schema.md    (5min, 无依赖)
  S02-schedule-service.md   (10min, 无依赖)
  S03-schedule-router.md    (10min, depends: S01, S02)
  S04-schedule-auth.md      (5min, depends: S01)
  S05-test-schema.md        (3min, depends: S01)
  S06-test-service.md       (5min, depends: S02)
  S07-test-router.md        (5min, depends: S03)
  S08-test-integration.md   (5min, depends: S03, S04)
```

### 2.2 调度层 — dispatch v5

**现有 dispatch v4 能力 (直接复用)：**
- SQLite DAG 调度 + depends_on 编排
- 文件锁 + 循环依赖检测
- 5 层 context enrichment
- Git 模式: clone → 执行 → push branch → merge
- Feedback loop: 3 轮自动重试
- 节点状态追踪 + heartbeat

**v5 新增：**
- `dispatch.py feed <project>` — 从 specs/pending/ 扫描新 spec 自动入队
- `dispatch.py verify <project>` — Layer 2 MiniMax review
- `dispatch.py review-queue` — Howard 审批界面
- `dispatch.py daily-report` — 日报

### 2.3 生产层 — 32 个自治 Agent

**每个 agent 是一个完整的 Claude Code session：**

```
输入: 原子 spec (目标 + 约束 + 验收标准)
     + 5 层 context (CLAUDE.md + 项目记忆 + SHARED_CONTEXT + 兄弟任务 + 环境)

Agent 自主执行:
  1. 读 spec，理解目标
  2. 分析目标代码库 (grep/read 已有代码)
  3. 决定实现方案
  4. 写代码
  5. 写测试
  6. 跑测试 (pytest/tsc/ruff)
  7. 测试不过 → 自己读错误 → 自己修 (最多 3 轮)
  8. 通过 → commit + push branch

输出: 一个通过验收标准的 git branch
```

**Agent 能力矩阵 (32 units across 4 servers):**

| 节点 | Agent 数 | 模型配置 | 角色 |
|------|---------|---------|------|
| codex-node-1 | 8 | GLM-5 (z.ai) | 执行 agent |
| glm-node-2 | 8 | GLM-5 (z.ai) | 执行 agent |
| mac2 | 5 | GLM-5 (z.ai) | 执行 agent |
| mac1 | 2 | GLM-5 (z.ai) | 执行 agent (低优先级) |
| **新节点 (未来)** | **8+/台** | **GLM/MiniMax/Codex** | **bootstrap.sh 一键加入** |

---

## 3. Spec 格式 — Agent 能自治的关键

**原子 Spec 模板 (给 agent 的)：**

```yaml
---
task_id: S01-schedule-schema
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - "backend/schemas/post.py"
executor: glm
---

## 目标
在 backend/schemas/post.py 中新增 BatchScheduleRequest 和 BatchScheduleResponse schema。

## 约束
- 使用 Pydantic v2 (项目已有)
- 最多 50 条 posts
- 每条 post 必须有 scheduled_at (datetime, 未来时间)
- 复用已有的 PostBase schema

## 验收标准
- [ ] BatchScheduleRequest 包含 posts: list[ScheduleItem] 和 max 50 校验
- [ ] ScheduleItem 包含 post_id, scheduled_at, platform
- [ ] scheduled_at 必须是未来时间 (validator)
- [ ] pytest tests/schemas/test_schedule.py 全绿

## 不要做
- 不改 router (S03 负责)
- 不改 service (S02 负责)
- 不改前端
```

**关键原则：**
1. **目标清晰** — agent 知道做什么
2. **约束明确** — agent 知道边界在哪
3. **验收可测** — agent 能自己验证是否完成
4. **不要做** — 防止 agent 越界踩其他任务的文件

---

## 4. Spec 流水线 SOP

### 4.1 全流程

```
Step 1: Howard 给方向
  → inputs/directions/2026-02-12.md

Step 2: MiniMax 原子拆分
  → mcp__llm__chat(model="minimax", "把这个方向拆成原子 spec...")
  → 输出 5-10 个 spec 文件到 specs/<project>/

Step 3: Spec 校验 (自动)
  → 检查 YAML front-matter 完整性
  → 检查 depends_on 无环
  → 检查 modifies 路径存在
  → 合格 → 标记 verified

Step 4: dispatch 分发 (自动)
  → python3 dispatch.py start <project>
  → 32 个 agent 自动抢任务

Step 5: Agent 执行 + 自验证
  → 每个 agent 独立闭环
  → 通过 → push branch
  → 失败 → feedback loop 3 轮

Step 6: 合并
  → python3 dispatch.py collect <project>
  → 自动 merge 无冲突的 branch

Step 7: 质量兜底 (可选)
  → MiniMax review 关键 PR
  → Howard 抽查 P0 任务
```

### 4.2 每日节奏

```
09:00  Howard: 给 3-5 个方向 (5 分钟)
09:05  MiniMax: 拆成 20-40 个原子 spec (自动, 2 分钟)
09:10  dispatch: 分发到 32 个 agent (自动)
09:15  Agents: 开始并行执行
       ...
       (agents 陆续完成，dispatch 自动喂新任务)
       ...
17:00  Howard: 看 daily-report, 抽查 2-3 个 PR (10 分钟)
17:10  dispatch: collect 合并通过的 branch (自动)

Howard 总投入: 15-20 分钟/天
Agent 产出: 20-40 tasks/天 (利用 80%+ 并发)
```

### 4.3 具体命令

```bash
# Step 1: Howard 写方向 (或口述后 Opus 整理)
echo "ClawMarketing 加批量排期, 复用 PostService, 限50条, 需鉴权, 只改 backend" \
  >> ~/Downloads/factory/inputs/directions/2026-02-12.md

# Step 2: MiniMax 拆分 (在 Opus session 中调用)
# mcp__llm__chat(model="minimax", prompt="拆分以下方向为原子 spec...")
# 输出存到 ~/Downloads/specs/<project>/S*.md

# Step 3+4: 校验 + 分发
python3 ~/Downloads/dispatch/dispatch.py start clawmarketing

# Step 5: 自动执行 (dispatch 自动 SSH 到各节点)

# Step 6: 合并
python3 ~/Downloads/dispatch/dispatch.py collect clawmarketing

# Step 7: 查看报告
python3 ~/Downloads/dispatch/dispatch.py report clawmarketing
```

---

## 5. 节点即插即用

### 5.1 bootstrap.sh

```bash
# 新 GCP VM 上只跑这一条命令:
bash bootstrap.sh --name node-3 --slots 8 --mode hybrid

# 自动完成:
# ✅ 装 Node.js + Python + git
# ✅ 装 Claude Code
# ✅ 配 GLM (z.ai) API key
# ✅ 配 MiniMax API key
# ✅ 创建 worker 目录结构
# ✅ 输出 node-info.json

# 然后在 Mac-1 controller 上更新 nodes.json 加上新节点
```

### 5.2 扩展新节点流程 (5 分钟)

```bash
# 1. 创建 VM (1 min)
gcloud compute instances create node-3 \
  --zone=us-west1-b \
  --machine-type=e2-standard-2 \
  --boot-disk-size=50GB \
  --image-family=ubuntu-2404-lts-amd64 \
  --image-project=ubuntu-os-cloud

# 2. Bootstrap (3 min)
gcloud compute ssh node-3 --zone=us-west1-b --command='
  curl -sL https://raw.githubusercontent.com/xxx/bootstrap.sh | bash -s -- --name node-3 --slots 4 --mode hybrid
'

# 3. 注册到 controller (1 min)
# 更新 ~/Downloads/dispatch/nodes.json 加上新节点

# 完事。以后再也不碰这台机器。
```

### 5.3 连接层 — 解决 SSH 不稳定问题

**现有问题：**
- gcloud SSH 每次冷启动慢、经常超时
- 长任务跑一半 SSH 断了，状态丢失
- 不同节点连接方式不统一 (gcloud vs ssh -i vs localhost)

**解决方案：三层防护**

**Layer 1: 持久 SSH tunnel (消除冷启动)**
```bash
# 每个节点开一个持久 tunnel，保持连接
# Mac-1 上运行 (launchd 保活):
ssh -f -N -M -S /tmp/ssh-codex-node-1 \
    -o ServerAliveInterval=30 \
    -o ServerAliveCountMax=3 \
    -o ExitOnForwardFailure=yes \
    codex-node-1

# 之后所有命令走已有 tunnel，秒连:
ssh -S /tmp/ssh-codex-node-1 codex-node-1 'command'
```

**Layer 2: tmux 脱离 SSH (断线不怕)**
```bash
# 所有 agent 任务在 tmux 里跑，SSH 断了任务继续
ssh node1 'tmux new -d -s task-S01 "bash task-wrapper.sh project S01 spec.md"'

# 检查状态不需要 SSH 连着
ssh node1 'cat ~/dispatch/project/tasks/S01/status.json'
```

**Layer 3: dispatch.py 统一连接抽象**
```python
def run_on_node(node_name, command, timeout=30):
    """统一连接层 — 不管什么节点，一个接口"""
    node = get_node(node_name)

    if node.is_local:
        # localhost 直接跑
        return subprocess.run(command, ...)

    # 1. 尝试持久 tunnel
    socket = f"/tmp/ssh-{node_name}"
    if Path(socket).exists():
        result = ssh_via_socket(socket, command, timeout)
        if result.ok:
            return result

    # 2. tunnel 不在 → 重建
    rebuild_tunnel(node)

    # 3. 还是不行 → 直接 SSH (fallback)
    return ssh_direct(node, command, timeout)

def dispatch_task(node_name, project, task_id, spec_file):
    """分发任务 — tmux 包装，断线安全"""
    tmux_cmd = f'tmux new -d -s {task_id} "bash ~/agent-worker/task-wrapper.sh {project} {task_id} {spec_file}"'
    return run_on_node(node_name, tmux_cmd)
```

**nodes.json 统一格式 (v5):**
```json
{
  "name": "codex-node-1",
  "ssh_target": "codex-node-1",           // 统一用 SSH config 别名
  "socket": "/tmp/ssh-codex-node-1",       // 持久 tunnel socket
  "slots": 8,
  "mode": "hybrid"
}
```

**SSH config (~/.ssh/config) 统一所有节点：**
```
Host codex-node-1
    HostName 35.203.150.12
    User howard
    IdentityFile ~/.ssh/gcp-key
    ServerAliveInterval 30

Host glm-node-2
    HostName 34.145.79.154
    User howard
    IdentityFile ~/.ssh/gcp-key
    ServerAliveInterval 30

Host mac2
    HostName 192.168.4.63
    User howardlee
    IdentityFile ~/.ssh/howard-mac2
    ServerAliveInterval 30
```

→ 所有节点统一用 `ssh <alias> 'command'`，不再区分 gcloud / ssh -i

**tunnel 保活 (launchd):**
```bash
# ~/Library/LaunchAgents/ai.oyster.ssh-tunnels.plist
# 每 60 秒检查 tunnel 是否活着，断了自动重连
```

### 5.4 何时加节点

| 信号 | 含义 | 行动 |
|------|------|------|
| pending > running × 2 | 任务积压 | 加执行节点 |
| Spec 产出 > 消化能力 | 并发不够 | 加执行节点 |
| L1 失败率 > 30% | 质量问题 | 不加节点，改 spec 质量 |
| merge 冲突频繁 | 架构拆分问题 | 不加节点，改任务拆分方式 |

---

## 6. 质量保证 (验证闭环)

### 6.1 质量内建于 Agent

**每个 agent 自己负责质量 (spec 中强制声明)：**
- 验收标准里必须有 pytest 命令
- Agent 必须跑通测试才能 commit
- Feedback loop: 测试不过 → agent 自己修 → 最多 3 轮

### 6.2 质量兜底 (可选)

| 层 | 谁 | 什么时候 | 覆盖 |
|----|-----|---------|------|
| Agent 自测 | GLM agent | 每个 task | 100% |
| MiniMax review | MiniMax | collect 之后 | P0: 100%, P1: 50% |
| Howard 抽查 | 人工 | 每天 5min | P0: 100%, 其他: 随机 |

### 6.3 Spec 质量 = 代码质量

**最重要的洞察: 代码质量取决于 spec 质量。**

好 spec → agent 理解准确 → 代码对
烂 spec → agent 猜 → 代码错

所以质量投资应该在 **spec 端**，不在执行端。MiniMax 拆 spec 时要：
- 验收标准必须可测试 (有 pytest 命令)
- modifies 声明清楚 (防踩文件)
- 不要做 列表清楚 (防越界)
- 约束写死技术栈 (防 agent 乱选)

---

## 7. 验证闭环 — 核心最佳实践 (2026-02-13 战略更新)

> **核心认知**: 从「调度优先」升级到「验证闭环」——每个环节都必须有明确的输入、输出、验证标准，不给 agent 任何糊弄空间。
>
> Dispatch 系统已有强大的**调度能力**（DAG 编排、并行分发、节点管理），但缺验证闭环，这是 ClawMarketing 58% 测试通过率的根因。

### 7.1 七大最佳实践

#### 1. 先出计划，再写代码

```
输出顺序：执行计划 → 文件树 → 逐文件代码 → README → 验收清单 → 自评
```

**教训**: S01-S18 直接 dispatch 写代码，没有统一的执行计划。导致三节点产出合并后 79 个 test fail、接口对不上。

**借鉴**:
- 每个项目开始前，先输出一份包含以下内容的执行计划
- 里程碑拆分（至少 6 步，有先后依赖）
- 模块边界（谁写什么，不碰什么）
- 数据模型设计（统一的 schema）
- API 列表（含请求/响应示例）——SHARED_CONTEXT
- **风险清单 + 缓解策略**

---

#### 2. 共享契约是铁律

```
模块边界：前端 / 后端 / 共享契约 / 测试
```

**教训**: SHARED_CONTEXT.md 写了但不够硬。PersonaEngine 构造函数参数错位、Pydantic 大小写不一致、方法不存在——全是契约没对齐。

**借鉴**:
- 共享契约必须包含：**每个接口的请求/响应 JSON 示例**，不只是类型签名
- Spec 里必须引用契约，agent 执行前先读契约
- 契约变更 = 全停，重新对齐

---

#### 3. 一键启动 + 一键测试

```
./run.sh dev   启动前后端
./run.sh test  运行所有测试
```

**教训**: ClawMarketing 到现在都没有统一的启动/测试命令。每次验证都临时拼命令。

**借鉴**:
- 项目根目录必须有 `run.sh` 或 `Makefile`
- `make dev` = 启动全栈
- `make test` = 跑全部测试
- 这是 agent 自验证的基础——spec 的验收标准直接写 `./run.sh test`

---

#### 4. Revision + 冲突检测

```
PATCH 必须带 baseRevision；不匹配返回 409
```

**教训**: 32 个 agent 并行改同一个项目，没有任何冲突检测。rsync basename 冲突、同文件互踩。

**借鉴**:
- 每个 spec 的 `modifies` 字段是我们的"锁"
- dispatch 应该检查：两个 running 任务的 modifies 有交集 → 串行不并行
- collect 回来时做 diff 检查，有冲突报 409 而不是静默覆盖

---

#### 5. 测试不是可选的

```
后端单测 >= 12, 前端单测 >= 8, E2E >= 5
否则判定失败
```

**教训**: S01-S18 写了 19 个测试文件，但 58% 通过率，27 个 ERROR。测试是"写了但没人跑"的装饰品。

**借鉴**:
- Spec 模板强制加：`verify: ./run.sh test`
- Agent 执行完必须跑测试，测试不过 = 任务失败，不算 completed
- task-wrapper.sh 结尾加测试步骤，测试红 → status = failed

---

#### 6. 导入/导出验证闭环

```
导入后再导出应保持等价（可通过测试证明）
```

**借鉴**: 应用到 dispatch 回收链——
- 代码从 Mac-1 → 节点（export）
- Agent 改完 → 回收到 Mac-1（import）
- **import 后的代码 build/test 必须通过 = 闭环验证**
- 不通过就不 merge

---

#### 7. 严格输出格式

```
不要跳过任何硬约束
不要只给伪代码
不要用 TODO 糊弄
```

**教训**: GLM agent 经常输出"已完成"但实际只写了注释 `# TODO: implement`，或者报告"Already Complete"但没验证。

**借鉴**:
- Spec 加约束：`禁止 TODO/FIXME/placeholder`
- task-wrapper 加验证：grep 产出代码里有没有 TODO，有就 fail
- Agent 的"已完成"声明不可信，必须跑验证命令

---

### 7.2 立即可落地的改进清单

| 改进项 | 当前状态 | 目标状态 | 优先级 |
|--------|----------|----------|--------|
| 执行计划 | 无 | 每个项目先出计划 spec | 高 |
| 一键测试 | 无 | ClawMarketing 根目录加 Makefile | 高 |
| 测试强制 | agent 报完成即完成 | task-wrapper 强制跑测试，不过 = fail | 高 |
| TODO 检查 | 无 | task-wrapper 增加 grep TODO | 中 |
| 冲突检测 | modifies 字段不检查 | dispatch.py 检查 modifies 交集 | 中 |
| 契约强化 | SHARED_CONTEXT 只有类型 | 必须带 JSON 示例 | 中 |
| 导入验证 | collect 不验证 | collect 后自动 build+test | 低 |

### 7.3 落地顺序建议

1. **task-wrapper.sh 增加测试强制** — 最简单、效果最直接
2. **ClawMarketing 根目录加 Makefile** — 让验证有统一入口
3. **dispatch.py 增加冲突检测** — 避免并行任务互踩
4. **Spec 模板增加执行计划段** — 从源头规范
5. **collect 后自动 build+test** — 闭环验证

---

## 8. 实施计划

### Phase 1: 今天跑通一个闭环 (Day 1)

```
1. Howard 给一个方向
2. MiniMax 拆成 3-5 个原子 spec
3. 手动放到 specs/<project>/
4. dispatch.py start <project>
5. 看 agent 跑完
6. collect + 检查结果
```
→ 验证整个链路能通

### Phase 2: Spec 流水线 SOP 固化 (Day 2-3)

```
1. 固化 MiniMax 拆分 prompt (存到 factory/prompts/)
2. 写 factory.py: collect → split → verify → enqueue
3. 固化原子 spec 模板
4. 日常开始用
```

### Phase 3: 自动化 + 扩展 (Day 4-7)

```
1. Cron 自动扫描 backlog → 生成 spec → dispatch
2. dispatch v5 新增 verify / review-queue / daily-report
3. 有需要时 bootstrap.sh 加新节点
```

### Phase 4: 跑满 (Week 2+)

```
1. 每天 30+ tasks 稳定产出
2. 并发利用率 80%+
3. Howard 日投入 < 30min
4. 按需加节点
```

---

## 8. 成功标准

| 指标 | 当前 | Phase 1 | Phase 4 |
|------|------|---------|---------|
| 日产出 (tasks) | ~0 | 5-10 | 30+ |
| 并发利用率 | ~0% | 30% | 80%+ |
| Opus token 消耗 | 大 | 少 (只给方向) | 极少 |
| Howard 日投入 | 数小时 | 1h | 20min |
| 新节点上线时间 | 数小时配置 | 5min (bootstrap) | 5min |
| Spec → 代码周期 | 手动 | 2h | 30min |
