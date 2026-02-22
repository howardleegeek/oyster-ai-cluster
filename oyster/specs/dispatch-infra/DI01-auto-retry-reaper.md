---
task_id: DI01-auto-retry-reaper
project: dispatch-infra
priority: 0
estimated_minutes: 30
depends_on: []
modifies: ["pipeline/reaper_daemon.py"]
executor: glm
---
## 目标
在 reaper_daemon.py 中添加自动重试逻辑：每2分钟检查 failed 任务，自动重置为 pending（最多15次）

## 技术方案
在 reaper_daemon.py 的主循环中添加一个 `auto_retry_failed()` 函数：

```python
def auto_retry_failed():
    """Auto-reset failed tasks back to pending for retry"""
    conn = get_db_connection()
    cur = conn.execute('''
        UPDATE tasks SET status='pending', max_retries=attempt+5, error='',
        node=NULL, pid=NULL, started_at=NULL, heartbeat_at=NULL,
        lease_owner=NULL, lease_expires_at=NULL
        WHERE status='failed' AND attempt < 15
    ''')
    conn.commit()
    if cur.rowcount > 0:
        logger.info(f"Auto-retried {cur.rowcount} failed tasks")
    conn.close()
```

在主循环中每2分钟调用一次。

## 约束
- 修改现有 reaper_daemon.py，不新建文件
- 使用现有的 DB 连接函数和 logger
- attempt >= 15 的任务不再重试（真正无法完成）
- 不改 reaper 的其他功能（超时收割等）

## 验收标准
- [ ] reaper daemon 每2分钟自动重置 failed tasks
- [ ] attempt >= 15 的任务不被重试
- [ ] 重试时清空 node/pid/error 等字段确保全新调度
- [ ] 日志记录每次重试的数量

## 不要做
- 不改 dispatch-controller.py
- 不改 task-wrapper.sh
- 不改 DB schema
