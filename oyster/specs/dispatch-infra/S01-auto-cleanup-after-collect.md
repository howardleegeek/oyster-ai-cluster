---
task_id: S01-auto-cleanup-after-collect
project: dispatch-infra
priority: 0
estimated_minutes: 30
depends_on: []
modifies: ["oyster/infra/dispatch/dispatch-worker/node-guardian.py"]
executor: glm
---

## Goal
Fix the node-guardian disk cleanup logic so nodes never fill up. Currently guardian has `DISK_CLEANUP_THRESHOLD = 5` (only cleans at 5% free) and only kills stalled processes — it does NOT clean completed task work directories. This causes cascading failure: disk fills → sshd hangs → node becomes unreachable.

## Context
- systemd dispatch-worker.service and node-guardian.service are ALREADY deployed and running on all nodes
- guardian already detects disk pressure and kills stalled wrappers
- But guardian does NOT clean up completed task work directories (the actual disk hog)
- Each project clone is 100M-1.4G, dirs pile up at `~/dispatch/<project>/`
- Nodes have 28-49G disks — 50+ tasks fills them
- On 2026-02-20, ALL GCP nodes + mac2 went down because of this

## Root Cause Analysis
```
task completes → work dir stays at ~/dispatch/<project>/ → disk >95%
→ sshd can't create temp files → SSH drops → controller can't reach node
→ worker process alive but IO-blocked → systemd Restart=always never triggers
→ guardian runs locally but only kills processes, doesn't clean dirs
→ node permanently stuck until manual GCP console reboot
```

## Requirements

### 1. Raise guardian disk cleanup threshold
In `node-guardian.py`:
```python
# Change from:
DISK_CLEANUP_THRESHOLD = 5   # way too late, sshd already dead
# Change to:
DISK_CLEANUP_THRESHOLD = 20  # start cleanup at 20% free (80% used)
DISK_CRITICAL_THRESHOLD = 10 # aggressive cleanup below 10% free
```

### 2. Add work directory cleanup to guardian loop
In the guardian's periodic check, when disk_free < DISK_CLEANUP_THRESHOLD:
```python
def cleanup_disk():
    """Clean completed task work directories to free disk space."""
    dispatch_dir = Path.home() / "dispatch"

    # Phase 1 (disk < 20% free): Clean node_modules, .git, __pycache__, *.log
    for d in dispatch_dir.rglob("node_modules"):
        shutil.rmtree(d, ignore_errors=True)
    for d in dispatch_dir.rglob(".git"):
        shutil.rmtree(d, ignore_errors=True)
    for d in dispatch_dir.rglob("__pycache__"):
        shutil.rmtree(d, ignore_errors=True)
    for f in dispatch_dir.rglob("*.log"):
        if f.stat().st_mtime < time.time() - 3600:  # older than 1h
            f.unlink(missing_ok=True)

    # Also vacuum journal logs
    subprocess.run(["sudo", "journalctl", "--vacuum-size=50M"], capture_output=True)

    # Phase 2 (disk < 10% free): Remove entire project dirs that have no running tasks
    if disk_free_pct < DISK_CRITICAL_THRESHOLD:
        running_projects = {t["project"] for t in get_running_tasks()}
        for project_dir in dispatch_dir.iterdir():
            if project_dir.is_dir() and project_dir.name not in running_projects:
                if project_dir.name not in ("dispatch-worker", "output", "task-wrapper.sh"):
                    shutil.rmtree(project_dir, ignore_errors=True)
                    logger.warning(f"Emergency cleanup: removed {project_dir}")
```

### 3. Task-wrapper post-completion cleanup
At the END of task-wrapper.sh, after pushing results, clean up the task's own repo clone:
```bash
# After git push or task completion:
if [ -d "$REPO_DIR" ]; then
    rm -rf "$REPO_DIR"
    log "Cleaned up repo clone: $REPO_DIR"
fi
```

## Acceptance Criteria
- [ ] Guardian starts cleaning at 20% free (not 5%)
- [ ] node_modules, .git, __pycache__ are cleaned in Phase 1
- [ ] Entire project dirs removed in Phase 2 (critical, <10% free), excluding dirs with running tasks
- [ ] task-wrapper.sh cleans its own repo clone after completion
- [ ] Test: fill a node to 82% used → guardian cleans within 1 minute
- [ ] No data deleted for currently running tasks

## Do Not
- Do not change the systemd service files (they work fine)
- Do not change worker.py HTTP server logic
- Do not change dispatch.db schema
- Do not change the controller-side dispatch.py
