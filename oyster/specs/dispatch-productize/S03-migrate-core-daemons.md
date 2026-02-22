---
task_id: S03-migrate-core-daemons
project: dispatch-productize
priority: 1
estimated_minutes: 60
depends_on: ["S01-db-abstraction", "S02-postgres-schema"]
modifies: ["oyster/infra/dispatch/dispatch.py", "oyster/infra/dispatch/guardian.py", "oyster/infra/dispatch/pipeline/reaper_daemon.py"]
executor: glm
---

## 目标

将三个核心文件（dispatch.py, guardian.py, reaper_daemon.py）的所有 `sqlite3.connect()` 调用替换为 `from db import get_db`。

## 当前状态

| 文件 | sqlite3 调用次数 | 行数 |
|------|-----------------|------|
| dispatch.py | 10 | 3596 |
| guardian.py | 12 (刚统一过 WAL+timeout) | 1312 |
| reaper_daemon.py | 3 | 1222 |

## 实现

### 步骤

1. 在每个文件顶部替换：
   ```python
   # 旧
   import sqlite3
   # 新
   from db import get_db
   ```

2. 替换所有直连模式为 context manager：
   ```python
   # 旧
   conn = sqlite3.connect(DB_PATH, timeout=30.0)
   conn.execute("PRAGMA journal_mode=WAL")
   conn.row_factory = sqlite3.Row
   # ... 用 conn ...
   conn.close()

   # 新
   with get_db() as conn:
       # ... 用 conn ...
   ```

3. dispatch.py 特殊处理：
   - 保留 `init_database()` 但改为调用 `db.init_schema()`
   - 保留 `get_db()` 作为 re-export（向后兼容其他文件 import）
   - `_ensure_column()` 在 postgres 模式下改为 `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`

4. guardian.py：12 处全部替换
5. reaper_daemon.py：3 处全部替换

### 兼容性保证

- `DB_PATH` 变量保留，传给 `db.py` 作为 `DISPATCH_DB_URL` fallback
- 不设环境变量时行为 100% 不变（SQLite 模式）
- 所有 SQL 查询不改（`?` 占位符由 db.py 自动处理）

## 约束

- 不改 SQL 查询逻辑，只改连接方式
- 不重构函数，最小改动
- 保持 `import sqlite3` 在需要 `sqlite3.OperationalError` catch 的地方

## 验收标准

- [ ] `grep -c 'sqlite3.connect' dispatch.py` = 0（除了注释）
- [ ] `grep -c 'sqlite3.connect' guardian.py` = 0
- [ ] `grep -c 'sqlite3.connect' reaper_daemon.py` = 0
- [ ] `DISPATCH_DB_BACKEND=sqlite python dispatch.py status test` 正常工作
- [ ] 所有现有功能不变（start/status/collect/report）
- [ ] guardian 和 reaper 能正常启动运行

## 不要做

- 不改 SQL 查询
- 不重构函数签名
- 不改非核心文件（bridge.py, monitor.py 等后续 spec 做）
- 不加新功能
