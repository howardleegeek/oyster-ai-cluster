# 并行执行体系 V2 — 战略重设计

> Opus 规划。目标: 任何 app 级任务，从 spec 到代码+测试+验收，20 分钟内完成。

---

## 一、当前问题诊断

### 根本问题: 8 个脚本，0 个系统

| 问题 | 影响 | 发生次数 |
|------|------|---------|
| Session 互相不知道状态 | 同一任务被 2-3 个节点重复执行 | 多次 |
| 串行 dispatch 是默认 | 18 个任务排队等，本该 20 分钟的活跑了 2 小时 | ClawMarketing |
| Opus 亲自部署/监控 | 烧掉 80% token 在 SCP、SSH、ps aux 上 | 每次 |
| 脚本硬编码任务分配 | 换个项目要重写脚本，不可复用 | 每个项目 |
| 没有自动故障恢复 | 任务挂了要人工发现、人工重跑 | S18 空日志 |
| Mac-2 hostname 记错 | 连接失败浪费 2-3 轮排查 | 2 次 |
| 僵尸进程累积 | Mac-2 还有周日的 session 在跑 | 持续 |
| 远程节点 spec 同步靠手动 SCP | 忘了同步 = 节点跑空 | 多次 |

### 核心矛盾

**我们有 23-24 并发槽位，但没有调度系统。** 相当于有 24 台机器但没有 Kubernetes。

---

## 二、目标架构: Dispatch Controller

### 设计原则

1. **一个命令启动一切** — `./dispatch.sh <project>` 完事
2. **Spec 驱动** — 放 spec 文件进目录 = 自动调度
3. **去中心化状态** — registry.json 文件锁，不需要额外服务
4. **故障自愈** — 任务挂了自动重试，节点掉了自动重分配
5. **Opus 零接触执行** — Opus 只写 spec + 看报告，中间不碰

### 架构图

```
┌─────────────────────────────────────────────────────────┐
│                    Opus (总司令)                         │
│  Phase 1: 写 specs/ → Phase 5: 读 report.md → PASS     │
└───────────────┬─────────────────────────┬───────────────┘
                │ 写 spec                  │ 读 report
                ▼                          ▲
┌─────────────────────────────────────────────────────────┐
│              dispatch-controller.sh                      │
│                                                          │
│  1. 读 specs/<project>/S*.md                            │
│  2. 生成 dispatch-registry.json                          │
│  3. 同步 specs 到所有节点 (rsync)                        │
│  4. 在所有节点启动 worker (SSH + nohup)                  │
│  5. 轮询状态直到全部完成                                  │
│  6. 收集日志 + 生成 report.md                            │
│                                                          │
│  输入: project name + specs 目录                         │
│  输出: report.md (成功/失败/耗时)                        │
└──────┬──────────┬──────────┬──────────┬─────────────────┘
       │          │          │          │
       ▼          ▼          ▼          ▼
   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
   │Mac-1   │ │Mac-2   │ │codex   │ │glm     │
   │worker  │ │worker  │ │node-1  │ │node-2  │
   │2-3 slots│ │5 slots │ │8 slots │ │8 slots │
   │direct  │ │zai     │ │direct  │ │direct  │
   └────────┘ └────────┘ └────────┘ └────────┘

   每个 worker 运行 dispatch-worker.sh:
   - 从 registry 领取 pending 任务 (flock claim)
   - 执行 claude -p
   - 更新 registry: running → completed/failed
   - 循环直到没有 pending 任务
```

---

## 三、核心组件设计

### 3.1 dispatch-controller.sh (控制器 — 在 Mac-1 运行)

```bash
# 用法
./dispatch-controller.sh <project> [--max-concurrent=20] [--timeout=30m]

# 例子
./dispatch-controller.sh clawmarketing
./dispatch-controller.sh gem-platform --max-concurrent=15
```

**流程**:
```
1. 读 ~/Downloads/specs/<project>/S*.md
2. 运行 init_registry (生成 registry.json)
3. 清理所有节点僵尸进程
4. rsync specs 到所有节点的 ~/<project>-specs/
5. SSH 启动各节点 worker (nohup dispatch-worker.sh &)
6. 每 60 秒轮询 registry 状态 (本地文件，不需 SSH)
7. 全部 completed → 收集日志 → 生成 report.md
8. 有 failed → 自动重试最多 2 次
9. 超时 → 报告哪些任务卡住
```

**关键**: 控制器跑在 Mac-1，registry.json 也在 Mac-1。远程节点通过 rsync 同步。

### 3.2 dispatch-worker.sh (工作节点 — 每个节点运行)

```bash
# 由 controller 自动启动，也可手动运行
./dispatch-worker.sh <project> [--slots=N] [--api-mode=direct|zai]
```

**流程**:
```
while true:
  1. rsync pull registry from Mac-1
  2. 扫描 pending 任务
  3. 如果当前运行数 < slots → claim 下一个 pending 任务
  4. 后台启动 claude -p (记录 PID)
  5. 更新 registry: claimed → running
  6. rsync push registry to Mac-1
  7. 检查已完成的后台任务 → 更新 completed/failed
  8. sleep 10
  9. 没有 pending 且没有 running → 退出
```

**并发控制**: 每个 worker 维护 `slots` 个并发槽位。Mac-2 = 5, GCP = 8。

### 3.3 dispatch-registry.json (状态中心)

沿用已有设计，增加字段:

```json
{
  "version": 2,
  "project": "clawmarketing",
  "created_at": "...",
  "updated_at": "...",
  "config": {
    "max_retries": 2,
    "timeout_minutes": 30
  },
  "tasks": {
    "S01": {
      "status": "pending|claimed|running|completed|failed",
      "spec": "S01-database-schema.md",
      "node": "mac2",
      "pid": 9341,
      "attempt": 1,
      "started_at": "...",
      "completed_at": "...",
      "duration_seconds": 720,
      "error": null,
      "log_size_bytes": 45230
    }
  }
}
```

### 3.4 节点配置文件 nodes.json

```json
{
  "nodes": [
    {
      "name": "mac1",
      "host": "localhost",
      "slots": 2,
      "api_mode": "direct",
      "ssh": null,
      "enabled": true,
      "note": "Opus 运行时只留 2 slot"
    },
    {
      "name": "mac2",
      "host": "howard-mac2",
      "slots": 5,
      "api_mode": "zai",
      "ssh": "ssh -i ~/.ssh/howard-mac2 howardlee@192.168.4.63",
      "enabled": true
    },
    {
      "name": "codex-node-1",
      "host": "codex-node-1",
      "slots": 8,
      "api_mode": "direct",
      "ssh": "gcloud compute ssh codex-node-1 --zone=us-west1-b",
      "enabled": true
    },
    {
      "name": "glm-node-2",
      "host": "glm-node-2",
      "slots": 8,
      "api_mode": "direct",
      "ssh": "gcloud compute ssh glm-node-2 --zone=us-west1-b",
      "enabled": true
    }
  ]
}
```

**好处**: 加节点只改配置，不改代码。Mac-1 Opus 干活时把 slots 降到 0。

---

## 四、典型工作流 (20 分钟闪电战)

```
T+0min   Howard: "做 ClawMarketing"
T+0min   Opus: 读已有 specs，确认 18 个 task (≤1 轮)
T+1min   Opus: ./dispatch-controller.sh clawmarketing (≤1 轮)
         Controller 自动:
           → 生成 registry (18 tasks pending)
           → 清理 4 节点僵尸进程
           → rsync specs 到 4 节点
           → SSH 启动 4 个 worker
           → Mac-2: 5 并发 | codex-node-1: 8 并发 | glm-node-2: 8 并发 | Mac-1: 2 并发
           → 23 并发 = 18 任务瞬间被 claim
T+1min   所有 18 个任务同时开始执行
T+10min  简单任务 (S01-S05) 完成，worker 自动 claim 重试 failed 的
T+15min  大部分完成，1-2 个 failed 自动重试中
T+18min  Controller 检测全部 completed
T+19min  Controller 收集日志，生成 report.md
T+20min  Opus: 读 report.md → PASS/FAIL (≤1 轮)

Opus 总共用了 3 轮。
```

---

## 五、与现有体系的关系

### 替代

| 旧 | 新 | 说明 |
|----|----|------|
| dispatch_node1.sh | 删除 | 被 controller + worker 替代 |
| dispatch_node2.sh | 删除 | 同上 |
| dispatch_mac2.sh | 删除 | 同上 |
| parallel_dispatch_*.sh | 删除 | 同上 |
| dispatch_with_registry.sh | 演进为 worker | claim 逻辑保留 |
| init_registry.sh | 合并进 controller | 自动初始化 |

### 保留

| 组件 | 说明 |
|------|------|
| dispatch-registry.json | 核心状态文件，schema 升级到 v2 |
| nodes.json | 新增，节点配置 |
| specs/ 目录结构 | 保持不变 |
| CodexClaudeSync/ | 保留，用于 Opus↔副元帅 通信 |
| claude-mem | 保留，用于跨 session 决策记忆 |

### 复用

新项目只需:
1. 在 `specs/<project>/` 放 S*.md 文件
2. 运行 `./dispatch-controller.sh <project>`
3. 完事

---

## 六、故障处理矩阵

| 故障 | 检测方式 | 自动处理 |
|------|---------|---------|
| 任务超时 (>30min) | Controller 轮询 started_at | 标记 failed + 自动重试 |
| Claude 进程崩溃 | Worker 检查 PID 存活 | 标记 failed + claim 给其他节点 |
| 节点离线 | SSH 连不上 | 跳过该节点，其他节点接管 pending |
| rsync 失败 | 返回码非 0 | 用本地缓存继续，下次轮询重试 |
| 同一任务被重复 claim | flock 原子操作 | 不可能发生 |
| 所有节点满载 | 没有空闲 slot | 等待，每 10 秒检查 |
| 连续失败 3 次 | attempt >= max_retries+1 | 标记 permanent_failed，报告人工处理 |

---

## 七、实施计划

### Phase 1: 核心脚本 (GLM 实现，~30min)
- [ ] `dispatch-controller.sh` — 控制器
- [ ] `dispatch-worker.sh` — 工作节点
- [ ] `nodes.json` — 节点配置
- [ ] 升级 `init_registry.sh` — 支持 v2 schema

### Phase 2: 部署 (Codex 副元帅，~10min)
- [ ] SCP worker 到所有节点
- [ ] 清理旧的 dispatch_*.sh
- [ ] 测试 controller → 单任务 dry-run

### Phase 3: 验证 (GLM，~10min)
- [ ] 用 3 个 dummy task 测试 4 节点并发
- [ ] 测试故障恢复 (kill 一个进程，看是否自动重试)
- [ ] 测试节点离线 (disable 一个节点，看任务重分配)

### Phase 4: 文档 + Memory (Opus，≤1 轮)
- [ ] 更新 CLAUDE.md dispatch 章节
- [ ] 更新 memory/dispatch-reference.md

---

## 八、Opus 铁律更新

### 新规则

```
Opus 在批量任务中只做 3 件事:
1. 写/审 specs (≤3 轮)
2. 运行 dispatch-controller.sh (1 轮, 1 条命令)
3. 读 report.md 审批 (≤2 轮)

绝对不做:
- SSH 到任何节点
- SCP 任何文件
- ps aux 看进程
- 手动重跑失败的任务
- 修 dispatch 脚本的 bug (dispatch 给 GLM)
```

---

## 执行者分配

| 组件 | 执行者 | 原因 |
|------|--------|------|
| 本 spec | Opus | 架构规划 |
| controller + worker 实现 | GLM 并发 (2 个 session) | 纯 bash 脚本 |
| 部署到节点 | Codex 副元帅 | 需要 SSH 到多节点 |
| 集成测试 | GLM | 跑 dummy task |
| 最终审批 | Opus | 读报告 |
