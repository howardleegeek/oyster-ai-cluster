---
task_id: S06-supervisor-watchdog
project: dispatch-productize
priority: 1
estimated_minutes: 30
depends_on: ["S04-health-endpoints"]
modifies: ["oyster/infra/dispatch/supervisor.py"]
executor: glm
---

## 目标

创建进程级 supervisor，监控所有 daemon 的 health endpoint，自动重启不健康的服务。用于非 Docker 部署（mac 本地开发、裸机节点）。

## 实现

创建 `oyster/infra/dispatch/supervisor.py`：

```python
"""
Dispatch Process Supervisor
- 管理所有 daemon 生命周期
- 轮询 /health endpoint
- 自动重启不健康或死亡的进程
- 自身由 launchd/systemd 管理（唯一需要 OS 级守护的进程）

用法:
    python3 supervisor.py                    # 启动所有 daemon
    python3 supervisor.py status             # 查看状态
    python3 supervisor.py restart guardian   # 重启指定服务
"""

SERVICES = {
    "guardian": {
        "cmd": ["python3", "guardian.py"],
        "health_port": 8091,
        "health_path": "/health",
    },
    "reaper": {
        "cmd": ["python3", "pipeline/reaper_daemon.py"],
        "health_port": 8092,
        "health_path": "/health",
    },
    "factory": {
        "cmd": ["python3", "pipeline/factory_daemon.py"],
        "health_port": 8093,
        "health_path": "/health",
    },
}

# 核心循环：
# 1. 检查进程是否存活（poll PID）
# 2. 检查 /health 是否 200
# 3. 连续 3 次 unhealthy → kill + restart
# 4. 指数退避重启（1s, 2s, 4s, 8s, max 60s）
# 5. 重启超过 10 次 → 告警但继续尝试
```

### 关键特性

1. **单一守护点**：只需要 launchd/systemd 管理 supervisor.py 一个进程
2. **Health-based 重启**：不只看进程是否存活，还看 `/health` 是否返回 200
3. **指数退避**：防止无限快速重启（crash loop）
4. **优雅关闭**：收到 SIGTERM 时先 SIGTERM 所有子进程，等 10s，再 SIGKILL
5. **日志隔离**：每个 daemon 的 stdout/stderr 重定向到独立日志文件
6. **状态查询**：`supervisor.py status` 输出类似 `docker-compose ps` 的表格

### 输出格式

```
$ python3 supervisor.py status
SERVICE     PID    STATUS    UPTIME    HEALTH    RESTARTS
guardian    1234   running   2h 15m    healthy   0
reaper     1235   running   2h 15m    healthy   0
factory    1236   running   1h 03m    healthy   1
```

## 约束

- 纯标准库（subprocess, urllib, signal, json）
- 不用 supervisord / PM2 / 第三方进程管理器
- 代码量 < 300 行
- supervisor 自身必须极简（不连 DB、不做 SSH），只做进程管理 + HTTP health check

## 验收标准

- [ ] `python3 supervisor.py` 启动 3 个 daemon
- [ ] `kill -9 <guardian_pid>` 后 10s 内自动重启
- [ ] daemon 卡死（/health 503）后自动重启
- [ ] `python3 supervisor.py status` 显示所有服务状态
- [ ] `python3 supervisor.py restart reaper` 重启指定服务
- [ ] 优雅关闭（Ctrl+C）停止所有子进程

## 不要做

- 不用第三方库
- 不做远程节点管理（只管本机进程）
- 不连接数据库
