---
task_id: S02-consolidate-status
project: dispatch
priority: 1
estimated_minutes: 25
depends_on: []
modifies: ["oyster/infra/dispatch/dispatch.py"]
executor: glm
---

## Goal

Consolidate `check_remote_task_status()` from 3 separate SSH calls into 1 single SSH call that returns a JSON blob.

## Context

Current `check_remote_task_status()` (line 1265-1301) makes up to 3 SSH calls per task check:
1. `cat status.json`
2. `cat heartbeat` (if no status.json)
3. `cat pid` + `ps -p` (if heartbeat stale)

With 20+ running tasks, this means 60+ SSH roundtrips per check cycle. Each SSH call has 30s timeout potential.

## What to Change

### Replace `check_remote_task_status()` (line 1265-1301)

Replace the function body with a single SSH command that runs a small inline script:

```python
def check_remote_task_status(node, project, task_id):
    """Check task status on remote node via single SSH call"""
    task_dir = f"~/dispatch/{project}/tasks/{task_id}"
    # Single SSH call: read status.json, heartbeat, and check pid — output as JSON
    check_script = f"""
python3 -c "
import json, os, subprocess, time
d = '{task_dir}'
r = {{}}
# Read status.json
try:
    with open(os.path.expanduser(d + '/status.json')) as f:
        r['status_data'] = json.load(f)
except: pass
# Read heartbeat
try:
    with open(os.path.expanduser(d + '/heartbeat')) as f:
        r['heartbeat'] = f.read().strip()
except: pass
# Read pid and check alive
try:
    with open(os.path.expanduser(d + '/pid')) as f:
        pid = f.read().strip()
    r['pid'] = pid
    r['alive'] = subprocess.run(['ps', '-p', pid], capture_output=True).returncode == 0
except: pass
print(json.dumps(r))
"
"""
    out, err = run_ssh(node["ssh_host"], check_script)
    if not out:
        return None, err

    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return None, "Invalid JSON from remote check"

    # If status.json exists, return it directly
    if "status_data" in data:
        return data["status_data"], None

    # If heartbeat exists, check staleness
    if "heartbeat" in data:
        try:
            from datetime import datetime
            heartbeat_time = datetime.fromisoformat(data["heartbeat"])
            if (utcnow() - heartbeat_time).total_seconds() > 120:
                if data.get("pid") and not data.get("alive", True):
                    return {
                        "status": "failed",
                        "error": "Process died (heartbeat timeout)",
                    }, None
        except Exception:
            pass

    return None, err
```

### Also fix the duplicate code in `cmd_refresh()` (line 2220-2282)

That function duplicates the same 3-SSH-call pattern. Replace it with a call to `check_remote_task_status()` instead of inline SSH commands.

## Constraints

- DO NOT change `run_ssh()` function
- DO NOT change `task-wrapper.sh` or `guardian.py`
- DO NOT change the status.json format
- DO NOT add new dependencies (only stdlib: json, os, subprocess)
- The remote inline script must work on all nodes (python3 is guaranteed available)
- Keep the same return signature: `(status_dict, error_string)`

## Acceptance Criteria

- [ ] `check_remote_task_status()` makes exactly 1 SSH call per invocation
- [ ] Same behavior: returns status_data if status.json exists, detects dead processes if heartbeat stale
- [ ] `cmd_refresh()` uses `check_remote_task_status()` instead of inline SSH
- [ ] No change to how callers handle the return value

## Do Not

- Do not add new dependencies
- Do not refactor other functions
- Do not change UI/CSS
- Do not modify task-wrapper.sh
