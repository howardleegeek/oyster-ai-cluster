---
task_id: S10-async-batch-scheduling
project: dispatch-infra
priority: 1
estimated_minutes: 45
depends_on: []
modifies: ["dispatch-controller.py"]
executor: glm
---

## 目标
优化 dispatch-controller.py 的调度循环 schedule_once()，将串行的 per-task DB 查询改为批量查询，减少 SQLite 锁竞争。

## 背景
当前 schedule_once() 对每个 pending task 做 3 次独立 DB 查询（deps check、conflict check、push 后 update）。
当 pending 队列有 100+ task 时，一个调度周期产生 300+ DB 操作，SQLite WAL lock 成为瓶颈。

## 改动

### 1. 批量依赖检查
```python
# 改前: 每个 task 单独查 deps
for dep_id in deps:
    dep = conn.execute("SELECT status FROM tasks WHERE id=?", (dep_id,)).fetchone()

# 改后: 一次查所有 deps
all_dep_ids = set()
for task in pending:
    all_dep_ids.update(json.loads(task.get("depends_on") or "[]"))
dep_statuses = {r["id"]: r["status"] for r in conn.execute(
    f"SELECT id, status FROM tasks WHERE id IN ({','.join('?'*len(all_dep_ids))})",
    list(all_dep_ids)
).fetchall()} if all_dep_ids else {}
```

### 2. 批量文件冲突检查
```python
# 改前: 每个 task 调 check_file_conflicts (内含 DB 查询)
# 改后: 一次查所有 file_locks，在内存中比对
active_locks = {r["file_path"]: r["task_id"] for r in conn.execute(
    "SELECT file_path, task_id FROM file_locks"
).fetchall()}
```

### 3. 批量 lease 获取
```python
# 改前: 每个 task 单独 UPDATE + COMMIT
# 改后: 攒一批后一次 COMMIT
assignments = []  # [(task_id, node, lease_owner, lease_expires), ...]
for task_id, node, lease_owner, lease_expires in assignments:
    conn.execute(...)
conn.commit()  # 一次 commit
```

## 约束
- 不改变 _push_task 的异步推送逻辑（已经是 asyncio.create_task）
- 不改变 _select_best_worker 的选择逻辑
- 不改变 DB schema
- 不碰 aiohttp HTTP handler
- 只改 schedule_once() 函数体

## 验收标准
- [ ] 100 个 pending task 的调度周期从 300+ DB 操作降到 <10
- [ ] 现有 pytest 全绿（如果有测试）
- [ ] 日志输出格式不变
- [ ] 不影响 DAG 依赖判断的正确性
