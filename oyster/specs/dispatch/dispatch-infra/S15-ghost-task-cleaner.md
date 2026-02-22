---
task_id: S15-ghost-task-cleaner
project: dispatch-infra
priority: 1
depends_on: []
modifies:
  - dispatch/ghost_cleaner.py
  - dispatch/dispatch.py
executor: glm
---

# Ghost Task Cleaner: 自动清理卡死任务

## 目标
自动检测并清理运行超过阈值时间的 ghost tasks，释放节点 slots

## 背景
当前有多个任务运行超过 8 小时但未完成，实际上已经卡死但仍占用节点 slots：
- S02-agent-self-evolve: 10.6h
- S50-strategy-api: 8.5h
- S51-content-review: 8.5h
- S11-predictive-scheduling: 8.1h
- S12-code-self-audit: 8.1h

## 具体改动

### 1. 新增 ghost_cleaner.py
```python
import sqlite3
import subprocess
from datetime import datetime, timedelta

class GhostCleaner:
    """检测并清理 ghost tasks"""
    
    def __init__(self, db_path: str, threshold_hours: float = 2.0):
        self.db_path = db_path
        self.threshold_hours = threshold_hours
    
    def find_ghost_tasks(self) -> list:
        """找出运行超过 threshold 的任务"""
        # SELECT tasks where status='running' AND 
        # (now - started_at) > threshold_hours
    
    def kill_process(self, task_id: str, pid: int) -> bool:
        """Kill the wrapper process on remote node"""
        # SSH to node and kill the process
    
    def cleanup_task(self, task_id: str) -> bool:
        """清理任务状态"""
        # 1. Kill remote process
        # 2. Update DB status to 'failed'
        # 3. Release node slots
    
    def run(self) -> dict:
        """执行清理，返回报告"""
        ghosts = self.find_ghost_tasks()
        cleaned = []
        for task in ghosts:
            if self.cleanup_task(task['id']):
                cleaned.append(task['id'])
        return {
            "ghosts_found": len(ghosts),
            "cleaned": cleaned,
            "timestamp": datetime.now().isoformat()
        }
```

### 2. 集成到 dispatch.py
```python
# 在主循环中添加 ghost 检测
def schedule_loop(...):
    while not stop_file.exists():
        # ... existing code ...
        
        # 每 5 分钟检测 ghost tasks
        if cycle_count % 10 == 0:
            cleaner = GhostCleaner(db_path, threshold_hours=2.0)
            report = cleaner.run()
            if report['ghosts_found'] > 0:
                log(f"Ghost cleaner: {report}")
```

### 3. 配置
```json
// dispatch/ghost_config.json
{
  "enabled": true,
  "threshold_hours": 2.0,
  "check_interval_cycles": 10,
  "auto_kill": true,
  "notify_on_clean": true
}
```

## 修复当前卡死的任务

直接执行清理：
```bash
# Reset tasks that are clearly stuck
sqlite3 dispatch.db "
  UPDATE tasks SET status='failed', error='Ghost task auto-cleanup'
  WHERE id IN ('S02-agent-self-evolve', 'S50-strategy-api', 'S51-content-review', 
               'S11-predictive-scheduling', 'S12-code-self-audit')
  AND status = 'running';
"
```

## 文件清单

| 文件 | 操作 | 描述 |
|------|------|------|
| `dispatch/ghost_cleaner.py` | 新建 | Ghost 检测和清理模块 |
| `dispatch/ghost_config.json` | 新建 | 配置文件 |
| `dispatch/dispatch.py` | 修改 | 集成自动检测 |

## 验收标准

- [ ] 能检测运行超过 2 小时的任务
- [ ] 能 SSH 到节点 kill 进程
- [ ] 能更新 DB 状态
- [ ] 能释放节点 slots
- [ ] 能记录清理日志

## 不要做

- 不删除任务记录
- 不修改已完成的任务
- 不修改其他项目的任务状态
