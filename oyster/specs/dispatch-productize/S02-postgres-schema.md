---
task_id: S02-postgres-schema
project: dispatch-productize
priority: 0
estimated_minutes: 30
depends_on: ["S01-db-abstraction"]
modifies: ["oyster/infra/dispatch/schema.sql", "oyster/infra/dispatch/migrate.py"]
executor: glm
---

## 目标

创建 PostgreSQL schema 文件和自动迁移脚本，与现有 SQLite schema 完全等价。

## 实现

### 1. `schema.sql` — PostgreSQL DDL

从 dispatch.py `init_database()` 提取现有 schema，翻译为 PostgreSQL：

```sql
-- Dispatch PostgreSQL Schema
-- 等价于 dispatch.py init_database() 中的 SQLite schema

CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    project TEXT NOT NULL,
    spec_file TEXT NOT NULL,
    spec_hash TEXT,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending','claimed','running','completed','failed','deadletter')),
    node TEXT,
    pid INTEGER,
    attempt INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 10,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    collected_at TIMESTAMPTZ,
    heartbeat_at TIMESTAMPTZ,
    error TEXT,
    log_file TEXT,
    duration_seconds DOUBLE PRECISION,
    depends_on JSONB DEFAULT '[]',
    modifies JSONB DEFAULT '[]',
    exclusive INTEGER DEFAULT 0,
    priority INTEGER DEFAULT 2,
    lease_owner TEXT,
    lease_expires_at BIGINT,
    visibility_timeout INTEGER DEFAULT 300,
    idempotency_key TEXT,
    updated_at BIGINT,
    estimated_minutes INTEGER DEFAULT 30,
    artifact_hash TEXT,
    artifact_patch TEXT,
    loc_added INTEGER DEFAULT 0,
    loc_removed INTEGER DEFAULT 0,
    files_changed INTEGER DEFAULT 0,
    peer_validated TEXT DEFAULT 'pending',
    peer_node TEXT,
    peer_result TEXT
);

CREATE TABLE IF NOT EXISTS file_locks (
    file_path TEXT NOT NULL,
    task_id TEXT NOT NULL,
    locked_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (file_path, task_id)
);

CREATE TABLE IF NOT EXISTS nodes (
    name TEXT PRIMARY KEY,
    ssh_host TEXT,
    slots INTEGER DEFAULT 8,
    api_mode TEXT DEFAULT 'direct',
    work_dir TEXT DEFAULT '~/dispatch',
    running_count INTEGER DEFAULT 0,
    last_seen TIMESTAMPTZ,
    enabled INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    task_id TEXT,
    event_type TEXT,
    node TEXT,
    details TEXT
);

CREATE TABLE IF NOT EXISTS node_reputation (
    node TEXT PRIMARY KEY,
    score INTEGER DEFAULT 100,
    total_tasks INTEGER DEFAULT 0,
    passed_validations INTEGER DEFAULT 0,
    failed_validations INTEGER DEFAULT 0,
    fake_successes INTEGER DEFAULT 0,
    last_updated TIMESTAMPTZ,
    quarantined INTEGER DEFAULT 0,
    quarantine_reason TEXT,
    quarantine_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS peer_validations (
    id SERIAL PRIMARY KEY,
    task_id TEXT NOT NULL,
    project TEXT NOT NULL,
    executor_node TEXT NOT NULL,
    validator_node TEXT,
    status TEXT DEFAULT 'pending',
    result TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_tasks_lease ON tasks(lease_expires_at) WHERE status = 'claimed';
```

### 2. `migrate.py` — SQLite → PostgreSQL 数据迁移

```python
"""一次性迁移：从 SQLite dispatch.db 导入所有数据到 PostgreSQL"""
# 读 SQLite → 批量 INSERT 到 PostgreSQL
# 保留所有历史数据
```

## 约束

- schema.sql 必须与 dispatch.py init_database() 完全等价（所有表、所有列）
- `TEXT` 日期列改为 `TIMESTAMPTZ`
- `INTEGER PRIMARY KEY AUTOINCREMENT` 改为 `SERIAL PRIMARY KEY`
- JSON 字符串列（depends_on, modifies）改为 `JSONB`
- migrate.py 幂等（可重复运行不重复插入）

## 验收标准

- [ ] `psql -f schema.sql` 无错误
- [ ] `python migrate.py` 成功迁移 dispatch.db 全部数据
- [ ] 迁移后 `SELECT count(*) FROM tasks` 匹配
- [ ] 所有索引创建成功

## 不要做

- 不动 dispatch.py
- 不做 schema 优化（按现有结构 1:1 翻译）
