---
task_id: S07-migrate-secondary
project: dispatch-productize
priority: 1
estimated_minutes: 45
depends_on: ["S01-db-abstraction", "S03-migrate-core-daemons"]
modifies: ["oyster/infra/dispatch/dispatch-controller.py", "oyster/infra/dispatch/bridge-daemon.py", "oyster/infra/dispatch/monitor.py", "oyster/infra/dispatch/auto_iterate.py", "oyster/infra/dispatch/byzantine_fixer.py", "oyster/infra/dispatch/health_monitor.py", "oyster/infra/dispatch/memory_store.py", "oyster/infra/dispatch/memory_learner.py", "oyster/infra/dispatch/memory_api.py", "oyster/infra/dispatch/bridge.py", "oyster/infra/dispatch/bridge_dispatch_to_mc.py", "oyster/infra/dispatch/slot_agent.py", "oyster/infra/dispatch/pipeline/factory_daemon.py", "oyster/infra/dispatch/pipeline/scheduler.py", "oyster/infra/dispatch/pipeline/code_queue.py", "oyster/infra/dispatch/pipeline/reaper_daemon.py", "oyster/infra/dispatch/cluster/quarantine.py", "oyster/infra/dispatch/cluster/node_health.py", "oyster/infra/dispatch/cluster/watchdog.py", "oyster/infra/dispatch/cluster/peer_validator.py", "oyster/infra/dispatch/pipeline/clawcontrol/services/db.py"]
executor: glm
---

## 目标

将所有剩余文件（28 个）的 `sqlite3.connect()` 调用替换为 `from db import get_db`。

## 实现

机械替换，每个文件：
1. `import sqlite3` → `from db import get_db`
2. `conn = sqlite3.connect(...)` → `with get_db() as conn:`
3. 删除 `conn.execute("PRAGMA journal_mode=WAL")` 和 `conn.row_factory = sqlite3.Row`（db.py 自动处理）
4. 删除 `conn.close()`（context manager 自动关闭）
5. 保留 `except sqlite3.OperationalError` 的 catch（兼容两个后端）

## 约束

- 不改 SQL 查询逻辑
- 不重构函数
- 保持向后兼容

## 验收标准

- [ ] `grep -r 'sqlite3.connect' oyster/infra/dispatch/ --include='*.py' | grep -v db.py | grep -v __pycache__` 返回 0 结果
- [ ] 所有 daemon 能正常启动
- [ ] `dispatch.py status` 正常工作

## 不要做

- 不改 SQL 查询
- 不重构
- 不加新功能
