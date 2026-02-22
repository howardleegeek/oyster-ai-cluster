---
task_id: S11-maker-checker-verifier
project: dispatch-infra
priority: 1
estimated_minutes: 45
depends_on: []
modifies: ["dispatch-controller.py", "dispatch.py", "task-wrapper.sh"]
executor: glm
---

## 目标
实现 Maker-Checker 模式：task 完成后自动创建 verifier task，审查代码质量后才能被 collect。

## 必须完成的 5 件事（跳过任何一件 = 整体 FAIL）

### 事项 1: DB schema — dispatch.py

在 dispatch.py 的 `init_database()` 函数中:

**1a.** 找到 `CHECK(status IN (` 这行，在列表末尾添加 `'verifying','verified','rejected'`
```python
# 改前: CHECK(status IN ('pending','claimed','running','completed','failed','deadletter'))
# 改后: CHECK(status IN ('pending','claimed','running','completed','failed','deadletter','verifying','verified','rejected'))
```

**1b.** 在 init_database() 末尾用 `_ensure_column` 添加两个新字段:
```python
_ensure_column(conn, "tasks", "parent_task_id", "ALTER TABLE tasks ADD COLUMN parent_task_id TEXT")
_ensure_column(conn, "tasks", "task_type", "ALTER TABLE tasks ADD COLUMN task_type TEXT DEFAULT 'implement'")
```
注意: `_ensure_column` 函数已存在，直接调用。

**1c.** 在 `cmd_collect()` 中，把 `WHERE status='completed'` 改为 `WHERE status IN ('completed','verified')`
（注意: 用 IN 而不是只用 verified，这样向后兼容）

### 事项 2: 自动生成 verifier task — dispatch-controller.py

在 `handle_report()` 函数中，找到处理 `status == "completed"` 的代码块，添加:
```python
# 获取 task_type（默认 implement）
task_type = task.get("task_type", "implement")

# 只对 implement 类型创建 verifier
if reported_status == "completed" and task_type != "verify":
    conn.execute("UPDATE tasks SET status='verifying' WHERE id=?", (task_id,))
    verifier_id = f"V-{task_id}"
    conn.execute("""
        INSERT OR IGNORE INTO tasks (id, project, spec_file, status, parent_task_id, task_type, priority, estimated_minutes)
        VALUES (?, ?, ?, 'pending', ?, 'verify', 0, 10)
    """, (verifier_id, project, spec_file, task_id))
```

### 事项 3: 处理 verifier 结果 — dispatch-controller.py

同样在 `handle_report()` 中，当 verifier task 报告完成时:
```python
if task_type == "verify" and reported_status == "completed":
    parent_id = task.get("parent_task_id")
    # 从 verifier 的 log 或 result 中解析 verdict
    verdict = "PASS"  # 默认 PASS，后续从 agent output 解析
    if parent_id:
        if verdict == "PASS":
            conn.execute("UPDATE tasks SET status='verified' WHERE id=?", (parent_id,))
        else:
            conn.execute("UPDATE tasks SET status='rejected' WHERE id=?", (parent_id,))
```

### 事项 4: verifier 不分配到原始节点 — dispatch-controller.py

在 `_select_best_worker()` 函数中，添加节点隔离逻辑:
```python
# 如果是 verify 类型的任务，排除原始任务的执行节点
if task.get("task_type") == "verify" and task.get("parent_task_id"):
    parent = conn.execute("SELECT node FROM tasks WHERE id=?", (task["parent_task_id"],)).fetchone()
    if parent and parent["node"]:
        # 把原始节点加入该任务的 node_blacklist
        # 这样 _select_best_worker 已有的 blacklist 检查就会排除它
        pass  # 用已有的 node_blacklist 机制即可
```

### 事项 5: task-wrapper.sh verifier prompt

在 task-wrapper.sh 中，检测 TASK_TYPE 环境变量:
```bash
# 在调用 LLM 之前，检查是否是 verify 类型
if [ "$TASK_TYPE" = "verify" ]; then
    VERIFY_PROMPT="你是代码审查员。审查 ${PARENT_TASK_ID} 的实现是否满足 spec 验收标准。输出 verdict: PASS 或 FAIL 加一句话原因。"
    # 把 VERIFY_PROMPT 追加到 spec 内容后面
fi
```

dispatch-controller.py 推送 verify 任务时需要设置环境变量:
```python
# _push_task 中，如果 task_type == "verify"
env_vars["TASK_TYPE"] = task.get("task_type", "implement")
env_vars["PARENT_TASK_ID"] = task.get("parent_task_id", "")
```

## 绝对禁止
- ❌ 不要创建新的 dispatch.py 或 dispatch-controller.py 文件 — 只修改现有文件
- ❌ 不要删除任何现有函数或类
- ❌ 不要修改 handle_heartbeat / handle_status / handle_poll 等其他 HTTP handler
- ❌ 不要改变现有 pending→claimed→running→completed 的正常流程
- ❌ 不要引入任何新的外部依赖

## 验收标准（全部必须满足）
- [ ] dispatch.py CHECK 约束包含 verifying/verified/rejected
- [ ] dispatch.py 有 parent_task_id 和 task_type 列的 _ensure_column 调用
- [ ] task 完成后 handle_report 自动创建 V-{task_id}
- [ ] verifier PASS → 原始 task 变 verified
- [ ] verifier FAIL → 原始 task 变 rejected
- [ ] collect 查询包含 verified 状态
- [ ] verify 类型 task 不分配到原始节点
- [ ] task-wrapper.sh 有 TASK_TYPE=verify 的分支逻辑
- [ ] 现有 implement 类型 task 的流程不受影响
