---
task_id: DI13-factory-temporal-bridge
project: dispatch-infra
priority: 0
estimated_minutes: 45
depends_on: []
modifies: ["oyster/infra/dispatch/pipeline/factory_daemon.py", "oyster/infra/dispatch/temporal/activities.py"]
executor: glm
---

## 目标

连通 Factory daemon 和 Temporal 生产系统，实现完整闭环：Factory 生成 spec → 自动触发 Temporal 执行 → 结果回写 dispatch.db → Factory 看到结果 → 自动迭代。

## 背景

当前 Factory 写 spec 到 `specs/` + `dispatch.db`，但 Temporal 从不读 dispatch.db，也从不写回结果。Factory 的 `monitor_cluster` / `auto_iterate` / `fill_pipeline` 全部读 dispatch.db，看不到 Temporal 的执行结果。闭环断裂。

## 设计文档

详见 `oyster/docs/plans/2026-02-20-factory-temporal-bridge-design.md`

## 约束

- 不改 dispatch.db schema
- 不改 Factory 的 monitor_cluster / auto_iterate / fill_pipeline 读逻辑
- 不改 task-wrapper.sh
- 不改 Temporal workflow 定义
- 不引入新进程/daemon
- 不引入新依赖（temporalio 已安装）

## 实现步骤

### Step 1: factory_daemon.py — 初始化 Temporal client

在 `main()` 函数里，启动循环前：

```python
import asyncio
from pathlib import Path

# Load Temporal env (same logic as temporal/worker.py)
env_file = Path.home() / ".oyster-keys" / "temporal.env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

# Initialize Temporal client
from temporalio.client import Client as TemporalClient

async def _init_temporal():
    address = os.environ.get("TEMPORAL_ADDRESS", "localhost:7233")
    namespace = os.environ.get("TEMPORAL_NAMESPACE", "default")
    api_key = os.environ.get("TEMPORAL_API_KEY", "")
    if api_key:
        return await TemporalClient.connect(address, namespace=namespace, api_key=api_key, tls=True)
    return await TemporalClient.connect(address, namespace=namespace)

temporal_client = asyncio.get_event_loop().run_until_complete(_init_temporal())
print(f"  Temporal: connected to {os.environ.get('TEMPORAL_ADDRESS', 'localhost:7233')}")
```

将 `temporal_client` 作为参数传入 `run_factory_cycle` 和 `save_and_register_specs`。

### Step 2: factory_daemon.py — save_and_register_specs 加 Temporal 触发

在 `save_and_register_specs` 里，dispatch.db 注册成功后，触发 Temporal workflow：

```python
# After DB insert succeeds:
try:
    from temporalio.client import WorkflowAlreadyStartedError
    # 需要在文件顶部 import: from activities import SpecTask (或内联 dataclass)
    # 但 factory_daemon.py 不在 temporal/ 目录下，所以用 dict 传参

    # Round-robin node selection from nodes.json
    node = _pick_next_node()  # 新函数，见下方

    spec_task = {
        "task_id": s["id"],
        "project": s["project"],
        "spec_file": str(spec_file),
        "node": node,
        "work_dir": "~/dispatch",
        "estimated_minutes": s.get("estimated_minutes", 30),
        "repo_url": PROJECTS.get(s["project"], {}).get("repo_url", ""),
        "branch": f"task/{s['id']}",
    }

    asyncio.get_event_loop().run_until_complete(
        temporal_client.start_workflow(
            "SpecExecutionWorkflow",
            spec_task,
            id=f"spec-{s['id']}",
            task_queue="orchestrator",
        )
    )
    print(f"    → Temporal workflow started: spec-{s['id']} on {node}")
except WorkflowAlreadyStartedError:
    print(f"    → Temporal: spec-{s['id']} already running (skip)")
except Exception as e:
    print(f"    → Temporal trigger failed: {e} (spec registered in DB, manual trigger needed)")
```

### Step 3: factory_daemon.py — _pick_next_node 函数

```python
_node_index = 0

def _pick_next_node():
    """Round-robin active nodes from nodes.json."""
    global _node_index
    nodes_file = DISPATCH_DIR / "nodes.json"
    if not nodes_file.exists():
        return "codex-node-1"
    data = json.loads(nodes_file.read_text())
    active = [n["name"] for n in data.get("nodes", []) if n.get("slots", 0) > 0 and n.get("ssh_host")]
    if not active:
        return "codex-node-1"
    node = active[_node_index % len(active)]
    _node_index += 1
    return node
```

### Step 4: activities.py — dispatch_spec 结果回写 dispatch.db

在 `dispatch_spec` 的 return 前（在 retryable error raise 之前），加回写逻辑：

```python
# Write back to dispatch.db (Factory daemon reads this for state tracking)
try:
    import sqlite3
    db_path = DISPATCH_DIR / "dispatch.db"
    if db_path.exists():
        conn = sqlite3.connect(str(db_path), timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        final_status = "completed" if result.exit_code == 0 else "failed"
        conn.execute("""
            UPDATE tasks SET
                status = ?,
                node = ?,
                completed_at = ?,
                duration_seconds = ?,
                loc_added = ?,
                loc_removed = ?,
                files_changed = ?,
                artifact_hash = ?,
                error = ?,
                attempt = (COALESCE(attempt, 0) + 1)
            WHERE id = ?
        """, (
            final_status,
            result.node,
            time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()),
            result.duration_seconds,
            result.loc_added,
            result.loc_removed,
            result.files_changed,
            "",  # artifact_hash from status.json if available
            result.error[:500] if result.error else "",
            task.task_id,
        ))
        conn.commit()
        conn.close()
        activity.logger.info(f"[{task.task_id}] dispatch.db updated: {final_status}")
except Exception as e:
    activity.logger.warning(f"[{task.task_id}] dispatch.db writeback failed: {e}")
    # Non-fatal: Temporal Cloud still has the result
```

### Step 5: activities.py — scan_specs 改为读 dispatch.db pending

替换现有 `scan_specs`：

```python
@activity.defn
async def scan_specs(project: str) -> list[str]:
    """Scan for pending specs in dispatch.db (not just filesystem)."""
    import sqlite3
    db_path = DISPATCH_DIR / "dispatch.db"
    if not db_path.exists():
        # Fallback to filesystem scan
        specs_dir = DISPATCH_DIR.parent.parent / "specs" / project
        if not specs_dir.exists():
            return []
        return [str(f) for f in specs_dir.glob("S*.md")]

    conn = sqlite3.connect(str(db_path), timeout=10)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT spec_file FROM tasks WHERE project=? AND status='pending'",
        (project,)
    ).fetchall()
    conn.close()

    return [r["spec_file"] for r in rows if Path(r["spec_file"]).exists()]
```

### Step 0 (先决条件): 清理 zombie running tasks

```sql
-- 在 bridge 上线前执行一次
UPDATE tasks SET status='failed', error='stale: old controller zombie'
WHERE status='running' AND datetime(started_at) < datetime('now', '-1 hour');
```

## 验收标准

- [ ] Factory daemon 启动时打印 `Temporal: connected to ...`
- [ ] `save_and_register_specs` 生成 spec 后，Temporal Cloud 出现对应 workflow
- [ ] 重复注册同一个 spec，不会创建重复 workflow（打印 "already running"）
- [ ] Temporal 执行完一个 task 后，dispatch.db 对应行 status 变为 completed/failed
- [ ] `scan_specs` 只返回 dispatch.db 中 status='pending' 的 spec
- [ ] Factory 的 `monitor_cluster` 在下一个循环能看到正确的 completed 数量
- [ ] Factory 的 `auto_iterate` 在项目完成度 > 70% 时能触发下一代 spec 生成
- [ ] dispatch.db zombie running tasks 被清理

## 不要做

- 不改 dispatch.db schema
- 不改 Factory 的 monitor/iterate/fill 读逻辑
- 不改 task-wrapper.sh
- 不改 Temporal workflow 定义（SpecExecutionWorkflow 等）
- 不加新 daemon/进程
- 不要询问是否部署，直接部署
