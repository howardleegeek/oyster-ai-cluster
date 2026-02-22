---
task_id: S01-db-abstraction
project: dispatch-productize
priority: 0
estimated_minutes: 45
depends_on: []
modifies: ["oyster/infra/dispatch/db.py"]
executor: glm
---

## 目标

创建统一的数据库抽象层 `db.py`，支持 SQLite（开发）和 PostgreSQL（生产），通过环境变量切换。

## 背景

当前 31 个文件中有 139 处直接调用 `sqlite3.connect()`，导致：
- SQLite 锁竞争（`database is locked`）频繁 crash daemon
- 无法水平扩展（SQLite 不支持多进程写入）
- 不可卖给客户

## 实现

创建 `oyster/infra/dispatch/db.py`：

```python
"""
Dispatch DB abstraction layer.
Usage:
    from db import get_db, init_schema

    with get_db() as conn:
        conn.execute("SELECT * FROM tasks WHERE status=?", ("pending",))
"""
import os
from contextlib import contextmanager

DB_BACKEND = os.environ.get("DISPATCH_DB_BACKEND", "sqlite")  # "sqlite" | "postgres"
DB_URL = os.environ.get("DISPATCH_DB_URL", "dispatch.db")     # file path or postgres://...

@contextmanager
def get_db(timeout=30.0):
    """统一数据库连接。SQLite 或 PostgreSQL 取决于环境变量。"""
    if DB_BACKEND == "postgres":
        import psycopg2
        import psycopg2.extras
        conn = psycopg2.connect(DB_URL)
        conn.autocommit = False
        try:
            yield conn
        finally:
            conn.close()
    else:
        import sqlite3
        conn = sqlite3.connect(DB_URL, timeout=timeout)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

def init_schema():
    """初始化数据库 schema（兼容 SQLite 和 PostgreSQL）"""
    ...

def execute(query, params=None):
    """单次查询快捷方式"""
    with get_db() as conn:
        cur = conn.execute(query, params or ())
        conn.commit()
        return cur
```

### 关键设计决策

1. **参数占位符兼容**：SQLite 用 `?`，PostgreSQL 用 `%s`。在 `get_db()` 返回的连接上添加 wrapper，自动转换 `?` → `%s`（仅 postgres 模式）
2. **Row 对象兼容**：PostgreSQL 用 `psycopg2.extras.RealDictCursor` 模拟 `sqlite3.Row` 的字典访问
3. **Schema DDL 兼容**：`AUTOINCREMENT` → `SERIAL`，`TEXT PRIMARY KEY` 保留（PostgreSQL 支持）
4. **事务语义**：SQLite autocommit + 手动 commit；PostgreSQL 显式事务
5. **DB_URL 默认值**：保持向后兼容，默认 SQLite 模式

## 约束

- 不改动任何现有文件（本 spec 只创建 db.py）
- 不引入 ORM（SQLAlchemy 太重）
- psycopg2 作为 optional dependency（`pip install psycopg2-binary`）
- 100% 向后兼容：不设环境变量 = 和现在完全一样

## 验收标准

- [ ] `db.py` 存在且可 import
- [ ] `DISPATCH_DB_BACKEND=sqlite python -c "from db import get_db; ..."` 正常
- [ ] `DISPATCH_DB_BACKEND=postgres DISPATCH_DB_URL=postgres://... python -c "from db import get_db; ..."` 正常
- [ ] 参数占位符 `?` 自动转换为 `%s`（postgres 模式）
- [ ] `pytest tests/test_db.py` 全绿（含 SQLite 模式测试）

## 不要做

- 不要修改 dispatch.py / guardian.py / reaper_daemon.py（后续 spec 做）
- 不要引入 SQLAlchemy 或其他 ORM
- 不要改动任何现有功能
