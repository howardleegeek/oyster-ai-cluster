---
task_id: DI09-consolidate-daemons
project: dispatch-infra
priority: 0
estimated_minutes: 90
depends_on: []
modifies: ["dispatch-controller.py"]
executor: glm
---
## 目标
将 guardian.py、reaper_daemon.py、factory_daemon.py 三个独立 daemon 的核心逻辑合并进 dispatch-controller.py 的 async event loop，消除多进程抢 SQLite 锁的根本问题。

## 背景
当前 5 个进程同时写 dispatch.db（controller + guardian + reaper + factory + 偶发的临时脚本），SQLite 单写者锁导致 `database is locked` 错误，controller 调度循环被阻塞数小时。

## 技术方案

### 1. 在 dispatch-controller.py 中添加 3 个新 async 协程

```python
# ── Integrated Daemon Coroutines ──

async def reaper_loop():
    """Reaper: 每 60s 执行一次 (原 reaper_daemon.py)"""
    cycle = 0
    while RUNNING:
        cycle += 1
        try:
            await asyncio.get_event_loop().run_in_executor(None, _reaper_cycle, cycle)
        except Exception as e:
            logger.error(f"[reaper] cycle {cycle} error: {e}")
        await asyncio.sleep(60)

async def guardian_loop():
    """Guardian: 每 300s 执行一次 (原 guardian.py)"""
    cycle = 0
    while RUNNING:
        cycle += 1
        try:
            await asyncio.get_event_loop().run_in_executor(None, _guardian_cycle, cycle)
        except Exception as e:
            logger.error(f"[guardian] cycle {cycle} error: {e}")
        await asyncio.sleep(300)

async def factory_loop():
    """Factory: 每 60s 执行一次 (原 factory_daemon.py)"""
    cycle = 0
    while RUNNING:
        cycle += 1
        try:
            await asyncio.get_event_loop().run_in_executor(None, _factory_cycle, cycle)
        except Exception as e:
            logger.error(f"[factory] cycle {cycle} error: {e}")
        await asyncio.sleep(60)
```

### 2. 同步函数使用单连接+短事务模式

**关键约束：所有 DB 操作必须使用 `with get_db() as conn:` 短连接模式，用完立即关闭。**

```python
from contextlib import contextmanager

@contextmanager
def get_db():
    """短生命周期 DB 连接 — 进入时 connect，退出时 close"""
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")  # 30s 等锁
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
```

### 3. Reaper 同步逻辑 (_reaper_cycle)

从 reaper_daemon.py 提取以下函数（去掉独立 main loop，只保留 cycle 内逻辑）：
- `collect_task_status()` — SSH 到节点读 status.json，同步到 DB
- `reap_ghosts()` — 清理幽灵任务
- `reap_stuck()` — 清理超时任务
- `retry_failed()` — 重试失败任务
- `cleanup_stale_leases()` — 清理过期 lease
- `cleanup_stale_file_locks()` — 清理过期文件锁
- `sync_running_counts()` — 同步 running_count
- `cleanup_stale_processes()` — 每 10 个 cycle 清理僵尸进程
- `auto_recover_nodes()` — 每 5 个 cycle 恢复失联节点

```python
def _reaper_cycle(cycle_num: int):
    """One reaper cycle — runs in thread pool executor"""
    with get_db() as conn:
        collect_task_status(conn)
    with get_db() as conn:
        reap_ghosts(conn)
    with get_db() as conn:
        reap_stuck(conn)
    with get_db() as conn:
        retry_failed(conn)
    with get_db() as conn:
        cleanup_stale_leases(conn)
        cleanup_stale_file_locks(conn)
    with get_db() as conn:
        sync_running_counts(conn)
    if cycle_num % 10 == 0:
        with get_db() as conn:
            cleanup_stale_processes(conn)
    if cycle_num % 5 == 0:
        with get_db() as conn:
            auto_recover_nodes(conn)
```

### 4. Guardian 同步逻辑 (_guardian_cycle)

从 guardian.py 提取：
- `check_task_stuck()` — 检测 >4h 运行的任务
- `check_dag_stuck()` — 检测 DAG 卡住
- `auto_retry_failed_tasks()` — 自动重试
- `check_wrapper_version()` — 每 10 个 cycle 检查 wrapper 同步
- `check_ssh_connection()` — 每 10 个 cycle 检查 SSH

**不合并的功能** (低价值/已被 controller 覆盖)：
- `check_db_schema()` — 一次性操作，不需要循环
- `check_node_availability()` — controller 的 probe 已覆盖
- `check_task_watcher()` — 已废弃，不用 task-watcher 了
- `sync_task_status_from_nodes()` — reaper 的 collect_task_status 更完善
- `check_code_sync()` — controller git mode 已覆盖

### 5. Factory 同步逻辑 (_factory_cycle)

从 factory_daemon.py 提取：
- `check_and_iterate_projects()` — 检查项目完成度，自动出下一代 spec
- `auto_generate_specs()` — 当 pending < MIN_PENDING_TASKS 时自动补充
- `research_and_discover()` — 每小时调研趋势 (保持原有频率)

### 6. 在 main() 中启动所有协程

```python
async def main():
    # ... existing setup ...

    # Start all background loops
    tasks = [
        asyncio.create_task(scheduling_loop()),     # 已有
        asyncio.create_task(health_check_loop()),    # 已有
        asyncio.create_task(probe_workers_loop()),   # 已有
        asyncio.create_task(db_sync_loop()),          # 已有
        asyncio.create_task(reaper_loop()),            # 新增
        asyncio.create_task(guardian_loop()),           # 新增
        asyncio.create_task(factory_loop()),            # 新增
    ]

    # Start HTTP server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", CONTROLLER_PORT)
    await site.start()

    # Wait for shutdown
    await asyncio.gather(*tasks)
```

### 7. 禁用旧 launchd 服务

合并完成后，需要 unload 旧服务：
```bash
launchctl unload ~/Library/LaunchAgents/com.oyster.guardian.plist
launchctl unload ~/Library/LaunchAgents/com.oyster.reaper.plist
launchctl unload ~/Library/LaunchAgents/com.oyster.factory.plist
```

## 约束
- **只修改 dispatch-controller.py** — 把逻辑复制进来，不 import 原 daemon 文件
- 所有 DB 操作用 `with get_db() as conn:` 短连接，用完即关
- `PRAGMA busy_timeout=30000` 必须设置
- `PRAGMA journal_mode=WAL` 必须设置
- SSH 操作在 `run_in_executor(None, ...)` 中执行（不阻塞 event loop）
- 不改调度逻辑（scheduling_loop）
- 不改 DB schema
- 不改 dispatch.py

## 验收标准
- [ ] controller 单进程包含 reaper + guardian + factory 循环
- [ ] `lsof dispatch.db` 只显示 1 个 Python 进程
- [ ] 无 `database is locked` 错误（跑 10 分钟）
- [ ] reaper 功能正常：ghost 清理、stuck 重置、failed 重试
- [ ] guardian 功能正常：stuck task 检测、DAG 检查
- [ ] factory 功能正常：项目迭代、spec 生成
- [ ] 旧 launchd 服务已 unload

## 不要做
- 不要 import guardian.py / reaper_daemon.py / factory_daemon.py（复制需要的函数进来）
- 不改 dispatch.py
- 不改 DB schema
- 不删除旧 daemon 文件（留着做参考）
- 不改调度逻辑
- 不改 HTTP API endpoints
