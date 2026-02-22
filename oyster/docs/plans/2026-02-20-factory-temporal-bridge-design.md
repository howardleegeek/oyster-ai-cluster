# Factory-Temporal Bridge: Closed-Loop Design

**Date**: 2026-02-20
**Status**: Approved
**Problem**: Factory daemon and Temporal production system share `specs/` as a one-way interface. Factory writes specs but never learns Temporal's execution results. Temporal executes but never feeds back to dispatch.db. The loop is broken.

## Architecture Decision

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Trigger chain | Factory calls Temporal Client directly | Simplest, no extra process |
| Result sync | Activity writes back to dispatch.db inline | Zero latency, same machine |
| State truth | Temporal Cloud primary, dispatch.db is read mirror | Minimal change to Factory |
| Factory read logic | Unchanged (reads dispatch.db) | Zero refactoring |

## Changes (3 files, ~75 lines)

### 1. factory_daemon.py — Temporal trigger (~40 lines)

Add Temporal client initialization at startup. After `save_and_register_specs` writes .md + dispatch.db, call `client.start_workflow(SpecExecutionWorkflow, ...)`.

- Node selection: round-robin from nodes.json (active nodes with slots > 0)
- Workflow ID: `f"spec-{task_id}"` — Temporal auto-deduplicates
- On `WorkflowAlreadyStartedError`: skip silently (idempotent)
- Temporal client initialized once in `main()`, passed through cycle functions

### 2. activities.py — dispatch.db writeback (~25 lines)

In `dispatch_spec`, before returning `TaskResult`, update dispatch.db:

```sql
UPDATE tasks SET
    status = ?,        -- 'completed' or 'failed'
    node = ?,
    completed_at = ?,
    duration_seconds = ?,
    loc_added = ?,
    loc_removed = ?,
    files_changed = ?,
    artifact_hash = ?,
    error = ?
WHERE id = ?
```

Both dispatch.db and activities.py run on Mac-1. Direct sqlite3 connection, WAL mode.

### 3. activities.py — scan_specs status filter (~10 lines)

Change `scan_specs` from "return all S*.md" to "return only pending specs from dispatch.db":

```python
conn = sqlite3.connect(DB_PATH)
rows = conn.execute(
    "SELECT spec_file FROM tasks WHERE project=? AND status='pending'",
    (project,)
).fetchall()
return [r[0] for r in rows if Path(r[0]).exists()]
```

## Closed Loop

```
Factory (60s cycle)
  ├─ monitor_cluster() → dispatch.db → sees Temporal results
  ├─ save_and_register_specs()
  │     ├─ write .md
  │     ├─ write dispatch.db pending
  │     └─ start_workflow → Temporal Cloud
  ├─ auto_iterate() → completion > 70% → next gen
  └─ fill_pipeline() → pending < 80 → generate more
         │
         ▼
Temporal Cloud → Mac-1 Worker → SSH → Node → wrapper → OpenCode
         │
         ▼
activity completes → write dispatch.db → Factory sees it next cycle
```

## Pre-requisites

1. Clean zombie "running" tasks in dispatch.db:
   `UPDATE tasks SET status='failed', error='stale: old controller' WHERE status='running';`

2. Verify factory_daemon.py can import temporalio (same Python env as worker)

## Risks

| Risk | Mitigation |
|------|------------|
| Factory triggers too fast | Temporal dedup by workflow ID; MIN_PENDING_TASKS throttle |
| SQLite concurrent write | WAL mode; activity writes infrequently (once per task completion) |
| Factory crash mid-trigger | Temporal workflows already started continue independently |
| Node selection naive | Start with round-robin; DI11 health scoring upgrades later |

## Not Doing

- Not changing dispatch.db schema
- Not changing Factory read logic
- Not changing task-wrapper.sh
- Not changing Temporal workflow definitions
- Not adding a separate sync daemon
- Not deprecating dispatch.db
