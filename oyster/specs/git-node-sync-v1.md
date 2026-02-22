# Git-Based Node Sync System — Spec v1

> Priority: HIGH — 解决多节点文件覆盖/丢失的根本问题
> Owner: Opus 设计 → Codex/GLM 实现
> 影响: dispatch.py, task-wrapper.sh, nodes.json

---

## 1. 问题分析

### 当前流程
```
Mac-1 (Opus) → SCP spec.md → 远程节点
远程节点 → GLM 在 ~/dispatch/<project>/tasks/S01/output/ 写代码
任务完成 → 手动 rsync/scp 拉回 Mac-1 → 覆盖进项目目录
```

### 故障模式 (已发生)
- **basename 冲突**: `schemas/pack.py` 和 `api/pack.py` 同名，rsync 扁平拷贝时后者被前者覆盖
- **无冲突检测**: rsync overlay 是 last-writer-wins，静默覆盖
- **无版本追踪**: 产出文件没有 git history，无法 diff/回滚
- **手动合并**: collect_and_merge() 未实现，全靠人工 scp

### 根因
**纯文件复制 (SCP/rsync) 不保证目录结构完整性，且无冲突检测机制**

---

## 2. 设计目标

| 目标 | 约束 |
|------|------|
| 消除 basename 冲突 | git 保证完整路径 |
| 冲突可检测 | merge conflict 而非静默覆盖 |
| 可回滚 | git log + revert |
| 自动化 ≥ 现有水平 | 不增加人工步骤 |
| 兼容现有 dispatch.py | 最小改动，增量升级 |
| Mac-1 无 sshd 限制不变 | Pull 模式不变 |

---

## 3. 架构方案

### 核心思想
**每个任务在 feature branch 上工作，完成后 controller 拉回并合并**

### 前提条件
- 每个项目仓库 (如 `gem-platform/`) 必须是 git repo
- 远程节点能 clone/pull 项目 repo（通过 GitHub/private repo）
- 或：Mac-1 维护 bare repo，通过 SCP 分发 bundle

### 方案 A: GitHub 中心化 (推荐)

```
┌───────────────────────────────────────────────────┐
│                  GitHub (origin)                   │
│           main branch = 项目最新状态               │
└──────┬──────────────┬──────────────┬──────────────┘
       │              │              │
  ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
  │ Mac-1   │   │ GCP-1   │   │ Mac-2   │
  │ clone   │   │ clone   │   │ clone   │
  │ main    │   │ task/S01 │   │ task/S03│
  └─────────┘   └─────────┘   └─────────┘
```

**流程**:

1. **Dispatch 阶段** (dispatch.py 改动):
   ```
   # 替代 SCP spec.md
   a. controller 在 GitHub 创建 branch: task/<project>-S01
   b. SSH 到远程节点: git clone --branch task/<project>-S01 --single-branch <repo_url> ~/dispatch/<project>/tasks/S01/repo
   c. SCP spec.md 到节点 (不变)
   ```

2. **执行阶段** (task-wrapper.sh 改动):
   ```
   # GLM 在 repo 目录内工作，而非 output/
   cd ~/dispatch/<project>/tasks/$TASK_ID/repo
   claude -p "$(cat ../spec.md)" --dangerously-skip-permissions

   # 完成后 commit + push
   git add -A
   git commit -m "task/$TASK_ID: $(head -1 ../spec.md)"
   git push origin task/<project>-$TASK_ID
   ```

3. **Collect 阶段** (dispatch.py 新增 `collect_git()`):
   ```
   # Mac-1 pull 回来
   cd ~/Downloads/<project>
   git fetch origin

   for task in completed_tasks:
       branch = f"task/{project}-{task.id}"
       # 尝试合并
       result = git merge origin/{branch} --no-ff
       if conflict:
           log_conflict(task, conflict_files)
           git merge --abort
           # 标记需要人工/Codex 介入
       else:
           log_success(task)
   ```

### 方案 B: Git Bundle 离线传输 (备选，用于无 GitHub 的项目)

```
Mac-1 → git bundle create project.bundle main
     → SCP bundle → 远程节点
远程节点 → git clone project.bundle repo/
         → git checkout -b task/S01
         → GLM 工作
         → git bundle create result.bundle task/S01 ^main
Mac-1 ← SSH cat result.bundle > local (Pull 模式)
     → git fetch result.bundle
     → git merge task/S01
```

**选用场景**: 项目未上 GitHub、敏感代码不能上云

---

## 4. 实现计划

### Phase 1: task-wrapper.sh 改造 (最小 MVP)

**文件**: `dispatch/task-wrapper.sh`

改动点:
- 新增参数 `$4 = REPO_URL` (可选，为空则走旧逻辑)
- 如果有 REPO_URL:
  - `git clone --branch $BRANCH --single-branch $REPO_URL repo/`
  - `cd repo/` 代替 `cd $OUTPUT_DIR`
  - 执行完毕后 `git add -A && git commit && git push`
- 向后兼容：无 REPO_URL 时行为不变

### Phase 2: dispatch.py 增加 git 模式

**文件**: `dispatch/dispatch.py`

改动点:
- `nodes.json` 新增字段:
  ```json
  {
    "git_mode": true,
    "github_token_env": "GITHUB_TOKEN"
  }
  ```
- 项目配置新增:
  ```json
  {
    "project": "gem-platform",
    "repo_url": "git@github.com:oyster-labs/gem-platform.git",
    "sync_mode": "git"  // "git" | "scp" (默认)
  }
  ```
- `dispatch_task()` 增加分支:
  - `sync_mode == "git"`: 创建 branch → SSH clone → SCP spec → SSH 执行
  - `sync_mode == "scp"`: 现有逻辑不变
- 新增 `collect_git(project)`:
  - fetch all remote branches
  - 按 task 顺序合并
  - 冲突检测 → 记录到 SQLite events 表
  - 生成 merge_report.md

### Phase 3: 自动冲突解决

- 简单冲突 (不同文件): 自动合并 ✅
- 同文件不同区域: git 自动合并 ✅
- 同文件同区域: 标记冲突 → dispatch 修复任务给 Codex
- 生成 `conflict_resolution_spec.md` → Codex 执行

### Phase 4: 清理

- 合并成功的 branch → 删除远程 branch
- 远程节点 `~/dispatch/<project>/tasks/` → 定期清理
- SQLite 记录保留 30 天

---

## 5. 配置变更

### nodes.json 新增字段
```json
{
  "nodes": [...],
  "git_config": {
    "default_sync_mode": "git",
    "github_org": "oyster-labs",
    "branch_prefix": "task/",
    "auto_cleanup_branches": true,
    "conflict_handler": "codex"
  }
}
```

### 项目级配置: `dispatch/projects.json` (新文件)
```json
{
  "gem-platform": {
    "repo_url": "git@github.com:oyster-labs/gem-platform.git",
    "repo_local": "~/Downloads/gem-platform",
    "sync_mode": "git",
    "main_branch": "main"
  },
  "claw-nation": {
    "repo_url": "git@github.com:oyster-labs/claw-nation.git",
    "repo_local": "~/Downloads/claw-nation",
    "sync_mode": "git",
    "main_branch": "main"
  }
}
```

---

## 6. 安全要求

- GitHub SSH key 部署到所有节点 (deploy key, read-write)
- 或使用 GITHUB_TOKEN 环境变量 (HTTPS clone)
- `.env` / API keys 不进 git (确保 .gitignore)
- branch 命名包含 node name 避免冲突: `task/<project>-<task_id>-<node>`

---

## 7. 回退策略

- `sync_mode: "scp"` 保留为默认值
- 任何项目可随时切回旧模式
- git 模式失败 (clone 超时等) → 自动降级到 scp 模式 + 告警

---

## 8. 预期收益

| Before (rsync) | After (git) |
|----------------|-------------|
| basename 冲突 → 静默数据丢失 | 冲突 → 检测 + 报告 |
| 无法回滚 | git log + revert |
| 手动合并 | 自动 merge + 冲突报告 |
| 无 diff 可查 | 每个 task 有清晰 commit |
| 目录结构丢失风险 | git 保证完整路径 |

---

## 9. 执行分配

| Phase | 执行者 | 预估 |
|-------|--------|------|
| Phase 1 (task-wrapper.sh) | GLM | 1 task |
| Phase 2 (dispatch.py git 模式) | Codex | 1 task (跨文件逻辑) |
| Phase 3 (冲突解决) | Codex | 1 task |
| Phase 4 (清理) | GLM | 1 task |
| 节点 deploy key 部署 | Howard 手动 | 10 min |

---

## 10. 验收标准

- [ ] `sync_mode: "git"` 时，task-wrapper.sh 在 git repo 内执行并 push
- [ ] dispatch.py 自动创建 branch、clone、合并
- [ ] 两个 task 修改同名文件 → 冲突检测，不静默覆盖
- [ ] 合并成功后远程 branch 自动清理
- [ ] `sync_mode: "scp"` 时行为完全不变 (向后兼容)
- [ ] 端到端测试: 2 个 GCP 节点并行执行 → Mac-1 自动合并
