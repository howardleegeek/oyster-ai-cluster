# Dispatch v4: Task DAG + Git Sync — Unified Spec

> Priority: CRITICAL — 解决今天 P2/P3 互踩问题 + 长期文件同步
> Supersedes: `git-node-sync-v1.md` (合并进本 spec)
> Owner: Opus 设计 → Codex 实现核心 → GLM 实现辅助
> 影响: dispatch.py, task-wrapper.sh, nodes.json, projects.json

---

## 1. 问题全景

今天暴露了 dispatch 系统的 **两层缺陷**:

### Layer 1: 文件传输 (git-node-sync-v1 已覆盖)
- rsync/scp 扁平拷贝 → basename 冲突 (schemas/pack.py 覆盖 api/pack.py)
- 无版本追踪、无冲突检测、无回滚能力

### Layer 2: 任务调度 (今天新发现, 本 spec 核心)
- **无依赖声明**: P3 需要原 dispatch.py 作为输入，但 P2 会覆盖它，调度器不知道
- **无文件互斥**: 两个任务修改同一文件时无锁，后执行的覆盖先执行的
- **无执行顺序**: 所有任务并行调度，不区分 "可并行" vs "必须串行"
- **同节点文件冲突**: P2 在 codex-node-1 覆盖了原文件，P3 到同节点时原文件已丢

### 根因
**dispatch.py 把任务视为独立原子单元，实际上任务之间存在：**
1. **数据依赖** (P3 读 P2 的输入文件)
2. **文件互斥** (两个任务写同一个文件)
3. **顺序约束** (合并必须在两个分支都完成后)

---

## 2. 设计目标

| 目标 | 解决的问题 |
|------|-----------|
| 任务 DAG 依赖 | P3 声明依赖 P2，调度器等 P2 完成才启动 P3 |
| 文件级互斥 | 两个任务声明修改同文件 → 调度器串行化 |
| Git 隔离 | 每个任务在独立 branch 工作，不互相干扰 |
| 自动合并 | 完成后 controller 拉回 merge，冲突检测 |
| 向后兼容 | 无 DAG/git 配置时行为完全不变 |

---

## 3. Spec 文件增强

### 3.1 任务依赖声明 (新增 YAML front-matter)

```markdown
---
task_id: P3
depends_on: [P2]          # 等 P2 完成才能开始
modifies: [dispatch/dispatch.py]  # 声明要修改的文件
exclusive: true            # 需要独占 modifies 中的文件
executor: glm              # glm | codex
priority: 2                # 1=高 2=中 3=低
---

# Task P3: 合并 git-sync 功能到 dispatch.py

...spec 内容...
```

### 3.2 调度器解析

dispatch.py 解析 spec 文件时提取 front-matter:

```python
import yaml

def parse_spec_metadata(spec_path):
    """Extract YAML front-matter from spec file"""
    text = Path(spec_path).read_text()
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) >= 3:
            meta = yaml.safe_load(parts[1])
            content = parts[2].strip()
            return meta, content
    return {}, text
```

---

## 4. DAG 调度引擎

### 4.1 数据模型变更

```sql
-- tasks 表新增列
ALTER TABLE tasks ADD COLUMN depends_on TEXT DEFAULT '[]';  -- JSON array
ALTER TABLE tasks ADD COLUMN modifies TEXT DEFAULT '[]';     -- JSON array of file paths
ALTER TABLE tasks ADD COLUMN exclusive INTEGER DEFAULT 0;
ALTER TABLE tasks ADD COLUMN priority INTEGER DEFAULT 2;

-- 新表: 文件锁
CREATE TABLE IF NOT EXISTS file_locks (
    file_path TEXT NOT NULL,
    task_id TEXT NOT NULL,
    locked_at TEXT NOT NULL,
    PRIMARY KEY (file_path, task_id),
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);
```

### 4.2 调度算法

```python
def get_ready_tasks(db_path, project):
    """返回可以立即执行的任务 (依赖已满足 + 无文件冲突)"""
    with get_db(db_path) as conn:
        pending = conn.execute(
            "SELECT * FROM tasks WHERE project=? AND status='pending' ORDER BY priority, id",
            (project,)
        ).fetchall()

        ready = []
        for task in pending:
            deps = json.loads(task['depends_on'] or '[]')
            modifies = json.loads(task['modifies'] or '[]')

            # Check 1: 所有依赖已完成
            if deps:
                dep_statuses = conn.execute(
                    f"SELECT id, status FROM tasks WHERE id IN ({','.join('?' * len(deps))})",
                    deps
                ).fetchall()
                if not all(d['status'] == 'completed' for d in dep_statuses):
                    continue  # 依赖未满足，跳过

            # Check 2: 无文件冲突
            if modifies and task['exclusive']:
                locked = conn.execute(
                    f"SELECT file_path FROM file_locks WHERE file_path IN ({','.join('?' * len(modifies))})",
                    modifies
                ).fetchall()
                if locked:
                    continue  # 文件被其他任务锁定，跳过

            ready.append(task)

        return ready

def acquire_file_locks(db_path, task_id, modifies):
    """获取文件锁"""
    with get_db(db_path) as conn:
        for f in modifies:
            conn.execute(
                "INSERT INTO file_locks (file_path, task_id, locked_at) VALUES (?, ?, ?)",
                (f, task_id, datetime.now().isoformat())
            )
        conn.commit()

def release_file_locks(db_path, task_id):
    """释放文件锁"""
    with get_db(db_path) as conn:
        conn.execute("DELETE FROM file_locks WHERE task_id=?", (task_id,))
        conn.commit()
```

### 4.3 主循环改造

```python
def run_scheduler(db_path, project, nodes):
    """改造后的主循环"""
    while RUNNING:
        ready_tasks = get_ready_tasks(db_path, project)

        if not ready_tasks:
            # 检查是否全部完成或死锁
            pending = count_pending(db_path, project)
            running = count_running(db_path, project)
            if pending > 0 and running == 0:
                log("WARNING: 可能存在循环依赖或死锁")
                break
            if pending == 0 and running == 0:
                log("所有任务完成")
                break
            time.sleep(10)
            continue

        for task in ready_tasks:
            node = find_available_node(db_path, nodes, task)
            if node:
                modifies = json.loads(task['modifies'] or '[]')
                if modifies:
                    acquire_file_locks(db_path, task['id'], modifies)
                dispatch_task(db_path, task, node, project)

        # 检查运行中任务状态
        check_running_tasks(db_path, project, nodes)
        time.sleep(15)
```

---

## 5. Git 隔离 (整合 git-node-sync-v1)

### 5.1 Git 模式流程

```
Dispatch 阶段:
  1. controller (Mac-1) 创建 branch: task/<project>-<task_id>
  2. push 到 GitHub
  3. SSH 到节点: git clone --branch task/<project>-<task_id> --single-branch <repo>

执行阶段 (task-wrapper.sh):
  1. cd repo/
  2. claude 执行 spec
  3. git add -A && git commit && git push

Collect 阶段 (controller):
  1. git fetch origin
  2. 按拓扑序 merge 各 branch (依赖先 merge)
  3. 冲突 → 记录 + dispatch 修复任务
  4. 成功 → 删远程 branch
```

### 5.2 与 DAG 的协同

**关键洞察**: git branch 天然提供文件隔离。即使 P2 和 P3 同时运行:
- P2 在 `task/dispatch-P2` branch 上重写 dispatch.py
- P3 在 `task/dispatch-P3` branch 上修改 dispatch.py (从 main 分叉)
- **两者互不影响**，因为各自在独立 branch

但合并时仍需顺序:
- 如果 P3 depends_on P2: 先 merge P2 到 main，再 merge P3（可能有 conflict）
- 如果无依赖: 合并顺序由 priority 决定

**结论**: git 隔离减轻了 file_locks 的必要性 (scp 模式仍需要)，但 DAG 顺序在 merge 阶段仍然关键。

### 5.3 项目配置 (projects.json)

```json
{
  "gem-platform": {
    "repo_url": "git@github.com:oysterlabs/gem-platform.git",
    "repo_local": "~/Downloads/gem-platform",
    "sync_mode": "git",
    "main_branch": "main"
  },
  "dispatch": {
    "repo_url": null,
    "repo_local": "~/Downloads/dispatch",
    "sync_mode": "scp",
    "main_branch": null
  }
}
```

---

## 6. Spec 文件示例 (今天场景的正确写法)

### specs/dispatch-upgrade/P2.md
```markdown
---
task_id: P2
depends_on: []
modifies: [dispatch/dispatch.py]
exclusive: true
executor: codex
priority: 1
---

# P2: 重写 dispatch.py 核心调度引擎
...
```

### specs/dispatch-upgrade/P3.md
```markdown
---
task_id: P3
depends_on: [P2]
modifies: [dispatch/dispatch.py]
exclusive: true
executor: glm
priority: 2
---

# P3: 在 P2 产出基础上合并 git-sync 功能
注意: 等 P2 完成后，基于 P2 的新 dispatch.py 执行合并
...
```

调度器行为:
1. P1, P2 并行 (P1 不改 dispatch.py, 无冲突)
2. P3 等待 P2 完成
3. P2 完成 → release lock → P3 获取 lock → P3 开始
4. P3 获取的是 P2 产出的新文件 (通过 git merge P2 branch 后再 fork P3 branch)

---

## 7. 实现计划

### Phase 1: Spec 解析 + DAG 数据模型 (Codex)
- parse_spec_metadata() 解析 YAML front-matter
- DB schema 升级 (depends_on, modifies, exclusive, priority 列)
- file_locks 表
- 向后兼容: 无 front-matter 的 spec 视为无依赖无互斥

### Phase 2: 调度算法 (Codex)
- get_ready_tasks() 实现依赖检查 + 文件锁检查
- acquire/release file_locks
- 死锁检测 (循环依赖告警)
- 拓扑排序 merge 顺序

### Phase 3: Git 模式集成 (Codex)
- dispatch_task() 增加 git 分支: create branch → clone → execute
- collect_git() 实现: fetch → 按拓扑序 merge → conflict detection
- task-wrapper.sh git 模式

### Phase 4: task-wrapper.sh 升级 (GLM)
- 接收 REPO_URL 和 BRANCH 参数
- git clone + cd repo/ + execute + git add/commit/push
- 向后兼容: 无 REPO_URL 走旧逻辑

### Phase 5: 端到端测试 + 文档 (GLM)
- 测试 1: 两个无依赖任务并行执行
- 测试 2: P3 depends_on P2，验证等待行为
- 测试 3: 文件互斥，验证串行化
- 测试 4: git 模式 merge + 冲突检测
- 更新 CLAUDE.md dispatch 文档

---

## 8. 安全要求

- DAG 解析必须检测循环依赖 (A→B→A) 并报错
- file_locks 必须在任务 fail 时释放 (finally 块)
- git push 使用 deploy key (read-write), 不用 personal token
- branch 命名包含 node: `task/<project>-<task_id>-<node>` 避免冲突
- YAML front-matter 解析用 safe_load 防注入

---

## 9. 回退策略

- `sync_mode: "scp"` 保留为默认值
- 无 YAML front-matter 的 spec → 无依赖无互斥 (完全向后兼容)
- git 模式 clone 失败 → 自动降级 scp + 告警
- file_locks 表为空 → 所有任务可并行 (等同现有行为)

---

## 10. 验收标准

- [ ] spec 文件 YAML front-matter 正确解析
- [ ] depends_on 任务未完成时，依赖任务不被调度
- [ ] 两个任务声明修改同文件 + exclusive=true → 串行执行
- [ ] 循环依赖 → 报错而非死锁
- [ ] file_locks 在任务完成/失败后正确释放
- [ ] git 模式: branch 创建、clone、push、merge 全流程
- [ ] git merge 按拓扑序执行 (依赖先 merge)
- [ ] 冲突检测 + 报告生成
- [ ] 无 front-matter 的 spec → 行为不变 (向后兼容)
- [ ] 端到端: 2 节点并行 + 依赖等待 + 自动 merge

---

## 11. 执行分配

| Phase | 执行者 | 依赖 | 预估 |
|-------|--------|------|------|
| Phase 1 (解析+数据模型) | Codex | 无 | 1 task |
| Phase 2 (调度算法) | Codex | Phase 1 | 1 task |
| Phase 3 (Git 集成) | Codex | Phase 2 | 1 task |
| Phase 4 (task-wrapper.sh) | GLM | 无 (可与 1-2 并行) | 1 task |
| Phase 5 (测试+文档) | GLM | Phase 3+4 | 1 task |
| Deploy key 部署 | Howard | 无 | 10 min |

**估算**: Phase 1-3 串行 (Codex, ~3 tasks), Phase 4 并行 (GLM), Phase 5 等全部完成
