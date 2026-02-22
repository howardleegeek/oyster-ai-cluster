---
task_id: DI12-idempotency-key-guard
project: dispatch-infra
priority: 1
estimated_minutes: 30
depends_on: []
modifies: ["oyster/infra/dispatch/task-wrapper.sh", "oyster/infra/dispatch/temporal/activities.py"]
executor: glm
---

## 目标

在 task-wrapper.sh 和 activities.py 中添加 idempotency_key 硬护栏，防止 Temporal retry 造成重复 git commit/push。

## 背景

当前 wrapper 有 status.json 幂等检查（line 37-43），但只检查本地 task dir。如果 Temporal retry 发生在 push 成功后、cleanup 之后，retry 会重新 clone 一个新 repo，看不到已有的 status.json，导致重复执行 + 重复 push。

Git 本身能容忍重复 push（same commit = no-op），但如果 LLM 生成不同代码，会产生冲突 commit。

## 约束

- 幂等标记存储: git tag/branch marker（分布式，不依赖本地文件）
- 不改 status.json 格式
- 不引入新依赖
- 不改 workflow 逻辑

## 实现

### 1. task-wrapper.sh — Git push 前检查远程是否已有该 branch 的 merge commit

在 line 754（`=== Git commit/push ===`）之前添加：

```bash
# === IDEMPOTENCY GUARD: check if this task already pushed ===
if [[ "$GIT_MODE" == true ]] && [[ $LLM_EXIT_CODE -eq 0 ]]; then
    # Check if remote already has commits on this branch
    REMOTE_COMMITS=$(cd "$REPO_DIR" && git ls-remote --heads origin "$BRANCH" 2>/dev/null | wc -l | tr -d ' ')
    if [[ ${REMOTE_COMMITS:-0} -gt 0 ]]; then
        # Remote branch exists — check if it already has our task commit
        REMOTE_HEAD=$(cd "$REPO_DIR" && git ls-remote --heads origin "$BRANCH" | cut -f1)
        LOCAL_BASE=$(cd "$REPO_DIR" && git rev-parse HEAD 2>/dev/null)
        if [[ "$REMOTE_HEAD" != "$LOCAL_BASE" ]] && [[ -n "$REMOTE_HEAD" ]]; then
            echo "[$(get_timestamp)] IDEMPOTENCY: Remote branch $BRANCH already has commits ($REMOTE_HEAD), skipping push"
            echo "[$(get_timestamp)] This task was likely already completed in a previous attempt"
            # Mark as success — the work is already on GitHub
            EXIT_CODE=0
            GIT_PUSH_OK=0
            SKIP_GIT_PUSH=true
        fi
    fi
fi
```

然后修改 git push 块，在 push 前检查 `SKIP_GIT_PUSH`：

```bash
if [[ "$GIT_MODE" == true ]] && [[ $LLM_EXIT_CODE -eq 0 ]] && [[ "${SKIP_GIT_PUSH:-false}" != "true" ]]; then
    # existing push logic
fi
```

### 2. activities.py — dispatch_spec 开始前检查

在 `dispatch_spec` 的 Step 1 (mkdir) 之前添加：

```python
# Idempotency: check if task already completed on this node
try:
    rc, status_out, _ = await _ssh_run(task.node, f"cat {work_dir}/status.json", timeout=10)
    if rc == 0 and status_out.strip():
        existing = json.loads(status_out)
        if existing.get("status") == "completed" and existing.get("exit_code") == 0:
            activity.logger.info(f"[{task.task_id}] Already completed on {task.node}, skipping")
            return TaskResult(
                task_id=task.task_id, node=task.node, exit_code=0,
                loc_added=existing.get("loc_added", 0),
                loc_removed=existing.get("loc_removed", 0),
                files_changed=existing.get("artifact_files_changed", 0),
                duration_seconds=0.0,
            )
except Exception:
    pass  # No existing status = fresh execution
```

## 验收标准

- [ ] 同一个 spec 的 task 在 wrapper 层重试时，如果远程 branch 已有 commits，跳过 push
- [ ] activities.py 在 dispatch 前检查远程 status.json，已完成则直接返回 success
- [ ] 正常首次执行不受影响（REMOTE_COMMITS=0 时走正常流程）
- [ ] Temporal retry 3 次，只产生 1 次 git push

## 不要做

- 不引入分布式锁
- 不改 Temporal workflow 逻辑
- 不改 status.json schema
- 不要询问是否部署，直接部署
