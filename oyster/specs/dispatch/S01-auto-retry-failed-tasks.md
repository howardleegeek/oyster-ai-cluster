---
task_id: S01-auto-retry
project: dispatch
priority: 0
estimated_minutes: 30
depends_on: []
modifies: ["oyster/infra/dispatch/dispatch.py"]
executor: glm
---

## Goal

Add automatic retry for failed tasks (max 2 retries) before sending to deadletter.

## Context

- DB schema already has `attempt INTEGER DEFAULT 0` and `max_retries INTEGER DEFAULT 2` columns (line 97-98)
- Failed tasks currently go straight to `status='failed'` and stay there
- The `mark_deadletter()` function exists (line 650) but is only called manually
- Task status updates flow through `apply_task_updates()` at line 1455

## What to Change

### 1. In `apply_task_updates()` (line 1491-1507)

When a task fails (`update["status"] == "failed"`), instead of always setting `status='failed'`:

```python
elif update["status"] == "failed":
    # Check if task can be retried
    row = conn.execute(
        "SELECT attempt, max_retries FROM tasks WHERE id = ?",
        (update["id"],)
    ).fetchone()

    if row and row[0] < row[1]:
        # Retry: reset to pending with incremented attempt
        conn.execute("""
            UPDATE tasks
            SET status = 'pending', attempt = attempt + 1,
                error = ?, lease_owner = NULL, lease_expires_at = NULL,
                node = NULL, pid = NULL, started_at = NULL,
                completed_at = NULL, updated_at = ?
            WHERE id = ?
        """, (
            f"Retry {row[0]+1}/{row[1]}: {update['error']}",
            now, update["id"]
        ))
        # Log retry event instead of failure
        event_type = "task_retry"
    else:
        # Max retries exhausted, mark as deadletter
        conn.execute("""
            UPDATE tasks
            SET status = 'deadletter', completed_at = ?, error = ?,
                lease_owner = NULL, lease_expires_at = NULL, updated_at = ?
            WHERE id = ?
        """, (
            update["completed_at"],
            f"Exhausted {row[1] if row else 2} retries: {update['error']}",
            now, update["id"]
        ))
        event_type = "task_deadlettered"
    release_file_locks(db_path, update["id"], conn=conn)
```

Then update the event logging below (line 1510-1522) to use `event_type` variable instead of `f"task_{update['status']}"`.

### 2. In `cmd_mark()` (line 2940-2959)

Same retry logic for the CLI `mark` command. When `status == "failed"`, check attempt < max_retries before marking failed.

### 3. Add log message

When retrying, log: `[Retry] Task {task_id} attempt {n}/{max} - reason: {error}`

## Constraints

- DO NOT change the DB schema
- DO NOT change `mark_deadletter()` function signature
- DO NOT touch task-wrapper.sh or guardian.py
- DO NOT change how `completed` status is handled
- Keep the existing `release_file_locks` call for both retry and deadletter paths
- `attempt` column already exists, just increment it

## Acceptance Criteria

- [ ] Failed task with attempt < max_retries resets to 'pending' with attempt+1
- [ ] Failed task with attempt >= max_retries goes to 'deadletter' (not 'failed')
- [ ] Retry event logged as 'task_retry' in events table
- [ ] Deadletter event logged as 'task_deadlettered'
- [ ] `dispatch.py mark <task_id> failed` also respects retry logic
- [ ] Log message shows retry count

## Do Not

- Do not add new dependencies
- Do not refactor surrounding code
- Do not change UI/CSS
- Do not modify other commands
