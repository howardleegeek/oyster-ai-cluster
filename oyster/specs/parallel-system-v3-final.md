# 并行执行体系 V3 — 最终设计

> 整合了 2 个 Codex chaos engineering 分析 + Sonnet 故障模式调研 + 基础设施实测。

---

## 推翻 V2 的关键发现

| V2 假设 | 实际情况 | 影响 |
|---------|---------|------|
| 用 flock 做锁 | **macOS 没有 flock** | Mac-1 Mac-2 上锁完全失效 |
| GCP rsync 回推 Mac-1 | **Mac-1 没开 sshd, GCP 无法 SSH 回来** | 双向同步不可行 |
| JSON 文件做 registry | **多进程并发写 JSON = 文件损坏** | SPOF + 数据丢失 |
| 23 并发全开 | **Mac-2 16GB 跑 5 个 claude ≈ 吃满内存** | OOM/swap thrash |
| 任务经常失败需要重试 | **实际 18/18 成功，问题是集成** | 重试不是核心问题 |

---

## 核心架构决策

### 决策 1: SQLite 替代 JSON registry

**原因**: JSON 文件无法原子读写，多进程并发 = 文件损坏。SQLite WAL 模式天然支持并发读 + 排他写，自带事务，跨平台。

```sql
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,        -- S01, S02, ...
    project TEXT NOT NULL,
    spec_file TEXT NOT NULL,
    spec_hash TEXT,             -- SHA256, 确保 immutable
    status TEXT DEFAULT 'pending',  -- pending/claimed/running/completed/failed
    node TEXT,
    pid INTEGER,
    attempt INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 2,
    started_at TEXT,
    completed_at TEXT,
    heartbeat_at TEXT,
    error TEXT,
    log_file TEXT,
    duration_seconds REAL
);

-- 原子 claim: 单条 SQL, 无需外部锁
-- UPDATE tasks SET status='claimed', node=?, attempt=attempt+1, started_at=?
-- WHERE id = (SELECT id FROM tasks WHERE status IN ('pending','failed')
--   AND attempt < max_retries ORDER BY id LIMIT 1)
-- RETURNING id, spec_file;
```

### 决策 2: Mac-1 是唯一 orchestrator + 唯一 DB 写者

**原因**: GCP 不能 push 回 Mac-1。与其搞复杂的双向同步，不如彻底简化：
- Mac-1 是 **唯一写 DB 的进程**
- 远程节点通过 SSH 汇报状态（Mac-1 主动 pull）
- 消除所有分布式锁的需求

### 决策 3: Pull 模式状态同步

**原因**: 既然 Mac-1 → GCP 单向通，那让 Mac-1 主动问每个节点"你现在怎样"。

```
Mac-1 (controller) 每 30 秒:
  1. SSH 到每个节点: cat ~/dispatch/<project>/status/*.json
  2. 解析远端状态
  3. 更新本地 SQLite
  4. 如果有 pending 任务 + 节点有空闲 slot → SSH 启动新任务
```

### 决策 4: 每任务独立 workspace

**原因**: 多任务写同一个目录 = 文件冲突。ClawMarketing 最后需要手动 merge 18 个 session 的产物。

```
~/dispatch/<project>/
  tasks/
    S01/                    # 独立 workspace
      spec.md               # immutable 快照
      output/               # claude 产出
      status.json           # 本地状态 (worker 写)
      heartbeat             # 时间戳文件 (wrapper 每 10s 更新)
      task.log              # 完整日志
    S02/
    ...
```

### 决策 5: Wrapper 脚本替代裸 claude -p

**原因**: PID 追踪不可靠，stdout 缓冲导致"假卡死"，崩溃后无法区分状态。

```bash
#!/bin/bash
# task-wrapper.sh <task_id> <spec_file>
# 由 controller 通过 SSH 启动，运行在远程节点
TASK_DIR=~/dispatch/$PROJECT/tasks/$TASK_ID
mkdir -p "$TASK_DIR/output"

# 写 PID + 启动信息
echo "$$" > "$TASK_DIR/pid"
echo '{"status":"running","pid":'$$',"started_at":"'$(date -Iseconds)'"}' > "$TASK_DIR/status.json"

# 启动 heartbeat (后台, 每 10 秒)
while true; do date -Iseconds > "$TASK_DIR/heartbeat"; sleep 10; done &
HB_PID=$!
trap "kill $HB_PID 2>/dev/null; exit" EXIT INT TERM

# 执行任务 (exec 确保 PID 准确)
cd "$TASK_DIR/output"
if [ "$API_MODE" = "zai" ]; then
    ANTHROPIC_AUTH_TOKEN="$ZAI_API_KEY" \
    ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic" \
    API_TIMEOUT_MS=3000000 \
    claude -p "$(cat $TASK_DIR/spec.md)" --dangerously-skip-permissions > "$TASK_DIR/task.log" 2>&1
else
    claude -p "$(cat $TASK_DIR/spec.md)" --dangerously-skip-permissions > "$TASK_DIR/task.log" 2>&1
fi

EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo '{"status":"completed","completed_at":"'$(date -Iseconds)'","exit_code":0}' > "$TASK_DIR/status.json"
else
    echo '{"status":"failed","completed_at":"'$(date -Iseconds)'","exit_code":'$EXIT_CODE',"error":"exit code '$EXIT_CODE'"}' > "$TASK_DIR/status.json"
fi
```

---

## 架构图 (V3)

```
┌──────────────────────────────────────────────────────┐
│                   Opus (总司令)                       │
│  1. 写 specs/  2. dispatch.py start  3. 读 report    │
└─────────────────────┬────────────────────────────────┘
                      │
         ┌────────────▼────────────────┐
         │      dispatch.py            │
         │  (Mac-1, 唯一控制器)         │
         │                             │
         │  SQLite DB (dispatch.db)    │
         │  ┌─────────────────────┐   │
         │  │ tasks table         │   │
         │  │ nodes table         │   │
         │  │ events log table    │   │
         │  └─────────────────────┘   │
         │                             │
         │  主循环 (每 30 秒):          │
         │  1. Pull 各节点 status      │
         │  2. 更新 DB                 │
         │  3. 分配 pending → 空闲节点  │
         │  4. SSH 启动任务             │
         │  5. 检查超时/失败            │
         │  6. 全部完成 → 收集产物      │
         └──┬──────┬──────┬──────┬─────┘
            │      │      │      │
        SSH pull  SSH   SSH    SSH
        + start   pull  pull   pull
            │      │      │      │
       ┌────▼──┐ ┌─▼───┐ ┌▼────┐ ┌▼────┐
       │Mac-1  │ │Mac-2│ │GCP-1│ │GCP-2│
       │local  │ │     │ │     │ │     │
       │2 slot │ │5 slt│ │8 slt│ │8 slt│
       └───────┘ └─────┘ └─────┘ └─────┘

  每个节点:
  ~/dispatch/<project>/tasks/<id>/
    spec.md       ← controller SCP 过来
    status.json   ← wrapper 写
    heartbeat     ← wrapper 每 10s 写
    output/       ← claude 产出
    task.log      ← 完整日志
```

---

## 为什么用 Python 不用 Bash

V2 用 bash 写 controller，但 Codex 分析发现 35 个 edge case，大部分来自 bash 的脆弱性。

| 问题 | Bash | Python |
|------|------|--------|
| SQLite 操作 | 需要 sqlite3 CLI + 字符串拼接 | `import sqlite3` 原生 |
| JSON 解析 | jq 外部依赖 | `json.loads()` 内置 |
| SSH 管理 | 裸 ssh + 字符串拼接 | `subprocess` + ControlMaster |
| 并发控制 | `&` + wait + trap | `ThreadPoolExecutor` |
| 错误处理 | set -e 不够 | try/except 精确 |
| 跨平台 | BSD vs GNU 不兼容 | 一致 |
| 状态机 | 手写 if/case | enum + 明确转换规则 |

Python3 在所有 4 个节点都有。

---

## 组件清单

### 1. dispatch.py — 控制器 (Mac-1)

```bash
# 用法
python3 dispatch.py start <project>        # 初始化 + 开始调度
python3 dispatch.py status [<project>]      # 查看状态
python3 dispatch.py report <project>        # 生成报告
python3 dispatch.py stop <project>          # 停止调度
python3 dispatch.py cleanup <project>       # 清理远程残留
```

**职责**:
1. 扫描 `specs/<project>/S*.md` → 初始化 DB
2. 复制 spec 到各节点 (`scp spec.md node:~/dispatch/<project>/tasks/<id>/`)
3. 主循环:
   - SSH pull 各节点 `status.json` + `heartbeat`
   - 更新 DB (唯一写者, 无锁竞争)
   - heartbeat 超过 2 分钟 + 进程不存在 → 标记 failed
   - 分配 pending 到空闲 slot → SSH 启动 `task-wrapper.sh`
   - 全部完成 → 收集产物 + 生成 report.md
4. 事件日志: 每次状态变更写 events 表 (可追溯)

### 2. task-wrapper.sh — 任务执行 (各节点)

如上面设计。简单、无依赖、写 status.json + heartbeat。

### 3. nodes.yaml — 节点配置

```yaml
nodes:
  - name: mac1
    host: localhost
    ssh: null  # 本地执行
    slots: 2
    api_mode: direct
    work_dir: ~/dispatch

  - name: mac2
    host: howard-mac2
    ssh: "ssh -i ~/.ssh/howard-mac2 howardlee@192.168.4.63"
    slots: 5
    api_mode: zai
    work_dir: ~/dispatch

  - name: codex-node-1
    host: codex-node-1
    ssh: "gcloud compute ssh codex-node-1 --zone=us-west1-b --command"
    slots: 8
    api_mode: direct
    work_dir: ~/dispatch

  - name: glm-node-2
    host: glm-node-2
    ssh: "gcloud compute ssh glm-node-2 --zone=us-west1-b --command"
    slots: 8
    api_mode: direct
    work_dir: ~/dispatch
```

### 4. dispatch.db — SQLite 数据库 (Mac-1)

```
tables:
  tasks    — 任务状态 (如上 schema)
  nodes    — 节点实时状态 (last_seen, running_count, available_slots)
  events   — 所有状态变更事件 (append-only, 用于审计和故障恢复)
```

---

## 改进: 智能 Context (解决 90K token 浪费)

ClawMarketing 每个 session 塞完整 SHARED_CONTEXT (5000 token)，80% 是无关内容。

**V3 方案**: spec 里用 `@import` 标签按需引入:

```markdown
# S01-database-schema.md
@context: database, conventions
...spec 内容...
```

Controller 启动时按标签提取 SHARED_CONTEXT 的相关章节，拼接到 spec 快照里。

```python
CONTEXT_SECTIONS = {
    "database": "## Database Schema\n...(表定义)...",
    "conventions": "## Coding Conventions\n...(命名规范)...",
    "api": "## API Patterns\n...(路由模板)...",
    "frontend": "## Frontend Patterns\n...(React 组件规范)...",
}
```

预估节省: 每 session 5000→1000 token, 18 session 省 72K token。

---

## 改进: 集成 Session (解决 router 注册遗漏)

ClawMarketing 18 个 session 完成后缺少集成步骤。

**V3 方案**: 自动生成 S99-integration spec:

```
所有任务完成后, controller 自动:
1. 收集所有 output/ 到一个临时 repo
2. 生成 S99-integration.md:
   "review all files, fix imports, register all routers,
    verify __init__.py, run pytest, report issues"
3. 在一个节点执行 S99
4. S99 完成后再生成最终 report
```

---

## 故障处理 (基于 Codex 35 个 edge case 的精简回应)

| 严重度 | 问题 | V3 的解决方式 |
|--------|------|--------------|
| Critical | JSON 文件损坏 | 用 SQLite, 消除 |
| Critical | Claim 重复 | 单写者 + SQL 原子 UPDATE, 消除 |
| Critical | GCP 不能 push | Pull 模式, controller 主动拉, 消除 |
| Critical | 锁遗留死锁 | 无外部锁, SQLite 事务, 消除 |
| High | macOS 没 flock | 不需要 flock, 消除 |
| High | PID 不准确 | wrapper + pidfile + heartbeat, 缓解 |
| High | SSH 中断 | 幂等启动 + status.json 对账, 缓解 |
| High | OOM kill | 动态 slot + heartbeat 检测, 缓解 |
| Medium | 超时判定 | heartbeat 2min + 进程存活检查, 缓解 |
| Medium | 时钟漂移 | controller 统一计算, 不依赖远端时间 |
| Low | 文件编码 | spec 快照时规范化 |

**35 个 edge case → 14 个消除, 15 个缓解, 6 个接受**

---

## Codex + GLM 协作模型 (核心)

### 错误模式: "GLM 写代码, Codex 做部署"

这把 Codex 当搬运工用, 浪费了 GPT-5.3 xhigh 的强推理能力。

### 正确模式: 按复杂度 + 能力分工

```
任务类型                    │ 执行者  │ 原因
────────────────────────────┼────────┼────────────────────────────
dispatch.py 核心调度逻辑     │ Codex  │ 并发/状态机/edge case 密集
feedback loop 验证+修复     │ Codex  │ 需要跨文件推理 + 判断力
task-wrapper.sh             │ GLM    │ 简单线性脚本
节点部署 + 测试             │ Codex  │ 需要 SSH + 多节点协调
单 session 代码生成 (S01等)  │ GLM    │ 按 spec 写代码, GLM 擅长
跨 session 集成 (S99)       │ Codex  │ 需要理解全局 + 跨文件修改
Bug 修复 (复杂)             │ Codex  │ 需要推理根因
Bug 修复 (简单)             │ GLM    │ 改一两个文件
测试编写                     │ GLM    │ 按模式批量生成
测试调试 (flaky/complex)    │ Codex  │ 需要理解测试为什么失败
```

### 核心原则

1. **GLM 是量, Codex 是质** — 20 个并行的简单任务给 GLM, 3 个复杂的关键任务给 Codex
2. **GLM 先跑, Codex 收尾** — GLM 生成 80% 代码, Codex 做集成 + 验证 + 修复
3. **Codex 做决策, GLM 做执行** — 需要判断力的任务给 Codex (哪个 import 缺了? 这个 bug 的根因是什么?)
4. **不要让 Codex 等 GLM** — 两者并行, Codex 做独立的高价值任务, 同时 GLM 批量产出

### dispatch.py 中的 Codex 角色

```python
# nodes.json 中 Codex 不是普通 worker 节点
# Codex 是 "smart node" — 处理特殊任务类型

TASK_TYPES = {
    "implementation": "glm",    # S01-S18 常规实现 → GLM
    "integration": "codex",     # S99 集成 → Codex
    "verification": "codex",    # V01 验证 → Codex
    "fix": "codex",            # F01 修复 → Codex
    "test_debug": "codex",     # 测试调试 → Codex
    "simple_fix": "glm",       # 简单修复 → GLM
}
```

### 实际工作流示例

```
T+0min   Opus: 写 18 个 S*.md spec
T+1min   dispatch.py start:
         → 18 个 S* 任务分配给 GLM (23 并发)
         → 同时 Codex 开始做 dispatch.py 的 feedback loop 集成
T+12min  GLM 完成 15/18, Codex 完成 feedback loop
T+15min  GLM 全部完成
T+16min  Controller 自动触发 S99-integration → Codex 执行
T+18min  Codex 完成集成, 触发 V01-verify → Codex 执行
T+19min  Codex 发现 3 个问题, 生成 F01-fix → Codex 执行
T+20min  V02 验证通过, report.md 生成
T+20min  Opus: 读 report → PASS
```

---

## 实施计划 (Codex + GLM 协作)

| Phase | 内容 | 执行者 | 耗时 |
|-------|------|--------|------|
| 1a | task-wrapper.sh 基础框架 | GLM | 10min ✅ 完成 |
| 1b | dispatch.py 基础框架 | GLM | 20min ✅ 完成 |
| 2 | dispatch.py 加强: 本地执行/feedback loop/Codex 集成 | **Codex** | 20min |
| 3 | 部署到全部节点 + end-to-end 测试 | **Codex** | 15min |
| 4 | 清理旧脚本 + 更新 memory | GLM + Opus | 5min |
| **总计** | | | **~1h** |

### 验收标准

1. `python3 dispatch.py start clawmarketing` 一条命令完成 18 个任务的分发执行
2. 任何节点被 kill -9 一个 claude 进程后，controller 在 2 分钟内检测并重试
3. `python3 dispatch.py status` 正确显示全局进度
4. 换一个新项目只需要 `specs/<new-project>/S*.md` + `python3 dispatch.py start <new-project>`
5. Opus 全程不 SSH、不 SCP、不 ps aux
6. **Codex 负责集成/验证/修复**, GLM 负责批量实现

---

## Opus 新工作流 (最终版)

```
Howard: "做 <project>"
Opus:
  1. 写 specs/<project>/S*.md (≤3 轮)
  2. python3 dispatch.py start <project> (1 条命令, 1 轮)
  3. [等 15-20 分钟]
  4. python3 dispatch.py report <project> (读报告, 1 轮)
  5. PASS/FAIL (1 轮)

总计: ≤6 轮, 0 次 SSH, 0 次 SCP
```
