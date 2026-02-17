# Oyster Labs Infrastructure Guide

> 集群运维手册 — 节点管理、健康监控、自动化运维

---

## 架构总览

```
┌─────────────────────────────────────────────────────────────────┐
│                     Howard's Mac (Controller)                    │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  dispatch   │  │  guardian   │  │   monitor   │             │
│  │  (调度)     │  │  (守护)     │  │  (监控)     │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                 │                 │                    │
│         └────────────────┼─────────────────┘                    │
│                          │                                      │
│         ┌────────────────┼─────────────────┐                    │
│         │                │                │                     │
│         ▼                ▼                ▼                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                │
│  │  nodes   │    │  alerts   │    │  logs    │                │
│  │.json cfg │    │ 告警文件   │    │  日志文件  │                │
│  └──────────┘    └──────────┘    └──────────┘                │
└─────────────────────────────────────────────────────────────────┘
                          │ SSH / rsync
          ┌───────────────┼───────────────┐
          │               │               │
    ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
    │ codex-    │  │ glm-      │  │ oci-     │
    │ node-1    │  │ node-2    │  │ paid-3   │
    └───────────┘  └───────────┘  └───────────┘
```

---

## 核心组件

### 1. Guardian (守护进程)

**文件**: `infra/guardian.py`

24/7 自动检测并修复基础设施问题的守护进程。

```bash
# 前台运行 (测试用)
python3 ~/Downloads/dispatch/guardian.py

# 后台运行
nohup python3 ~/Downloads/dispatch/guardian.py &

# 查看日志
tail -f ~/Downloads/dispatch/infra-guardian.log
```

**功能**:

| 检查项 | 说明 |
|--------|------|
| `db_schema` | 自动迁移 DB schema |
| `wrapper_version` | 确保 task-wrapper.sh 最新 |
| `ssh_connection` | SSH 连接健康检查 |
| `node_availability` | 节点可达性检测 |
| `param_alignment` | 参数对齐检查 |

**配置**: `infra/guardian_config.json`

```json
{
  "interval_seconds": 300,
  "max_fix_attempts": 2,
  "backup_retention_days": 7,
  "checks": {
    "db_schema": true,
    "wrapper_version": true,
    "ssh_connection": true,
    "node_availability": true,
    "param_alignment": true
  }
}
```

**告警**: 自动在 `~/Downloads/dispatch/guardian_alerts/` 生成 JSON 告警文件。

---

### 2. Monitor (API 监控)

**文件**: `infra/monitor.py`

监控各 AI API 提供商的配额和使用情况。

```bash
# 查看当前配额
python3 ~/Downloads/dispatch/monitor.py check

# 持续监控 (每 300s)
python3 ~/Downloads/dispatch/monitor.py watch

# 查看历史 (24h)
python3 ~/Downloads/dispatch/monitor.py history
```

**支持的 API**:

- GLM (Z.ai)
- MiniMax
- Anthropic (Claude)
- OpenAI (Codex)

---

### 3. Sync Infrastructure (批量同步)

**文件**: `infra/sync-infra.sh`

一键同步 dispatch 核心文件到所有节点。

```bash
# 编辑节点列表
vi ~/Downloads/dispatch/sync-infra.sh
# 修改: NODES="codex-node-1 glm-node-2 glm-node-3 glm-node-4"

# 执行同步
bash ~/Downloads/dispatch/sync-infra.sh
```

**同步内容**:
- `dispatch.py`
- `task-wrapper.sh`
- `task-watcher.py`
- `nodes.json`
- `projects.json`

---

### 4. Install Agent Daemon

**文件**: `infra/install-agent-daemon.sh`

在节点上安装 agent-daemon systemd 服务。

```bash
# 在目标节点上运行
ssh <node>
bash -c "$(curl -sL https://raw.githubusercontent.com/howardleegeek/oyster-ai-cluster/main/infra/install-agent-daemon.sh)"

# 或本地运行 (会自动 SSH 到各节点)
bash ~/Downloads/dispatch/install-agent-daemon.sh
```

---

### 5. OCI ARM Grabber

**文件**: `infra/oci-arm-grab.sh` + `oci-arm-retry.sh`

抢占 Oracle Cloud ARM 实例的脚本。

```bash
# 抢占 ARM 实例
bash ~/Downloads/dispatch/oci-arm-grab.sh

# 重试脚本
bash ~/Downloads/dispatch/oci-arm-retry.sh
```

---

### 6. Snapshot DB

**文件**: `infra/snapshot_dispatch_db.py`

定期备份 dispatch.db。

```bash
# 手动备份
python3 ~/Downloads/dispatch/snapshot_dispatch_db.py

# 查看备份
ls -la ~/Downloads/dispatch/*.db* ~/Downloads/dispatch/snapshots/
```

---

## systemd 服务 (节点守护)

**文件**: `infra/glm-node-3-watcher.service`, `glm-node-4-watcher.service`

```bash
# 安装到节点
scp glm-node-3-watcher.service user@node:/tmp/
ssh user@node "sudo cp /tmp/glm-node-3-watcher.service /etc/systemd/system/"
ssh user@node "sudo systemctl daemon-reload"
ssh user@node "sudo systemctl enable glm-node-3-watcher"
ssh user@node "sudo systemctl start glm-node-3-watcher"

# 查看状态
ssh user@node "sudo systemctl status glm-node-3-watcher"
```

---

## 日常运维命令

### 查看集群状态

```bash
# dispatch 状态
python3 ~/Downloads/dispatch/dispatch.py status

# 节点 SSH 连通性
for n in codex-node-1 glm-node-2 glm-node-3 glm-node-4; do
  echo -n "$n: "; ssh -o ConnectTimeout=5 $n "uptime" 2>&1 | head -1
done

# guardian 告警
ls -lt ~/Downloads/dispatch/guardian_alerts/ | head -10

# guardian 日志
tail -50 ~/Downloads/dispatch/infra-guardian.log
```

### 重启服务

```bash
# 重启 dispatch 调度器
python3 ~/Downloads/dispatch/dispatch.py stop <project>
python3 ~/Downloads/dispatch/dispatch.py start <project>

# 重启 guardian
pkill -f guardian.py
nohup python3 ~/Downloads/dispatch/guardian.py &

# 重启节点 daemon (SSH 到节点)
ssh <node> "sudo systemctl restart agent-daemon"
```

### 故障排查

```bash
# 1. 检查 dispatch 日志
tail -100 ~/Downloads/dispatch/dispatch.log

# 2. 检查任务日志
cat ~/Downloads/dispatch/<project>/tasks/<task-id>/task.log

# 3. 检查节点状态
ssh <node> "ps aux | grep -E 'dispatch|agent' | grep -v grep"

# 4. 检查 DB 锁
python3 -c "
import sqlite3
conn = sqlite3.connect('~/Downloads/dispatch/dispatch.db')
print(conn.execute('PRAGMA busy_timeout').fetchall())
print(conn.execute('SELECT * FROM tasks WHERE status=\"running\"').fetchall())
"

# 5. 手动触发 guardian 检查
python3 ~/Downloads/dispatch/guardian.py --check-all
```

---

## 文件结构

```
~/Downloads/dispatch/
├── dispatch.py              # 主调度器
├── task-wrapper.sh          # 任务执行包装
├── nodes.json              # 节点配置
├── projects.json           # 项目配置
├── dispatch.db             # 任务数据库
│
├── infra/
│   ├── guardian.py         # 24/7 守护进程
│   ├── guardian_config.json
│   ├── monitor.py          # API 配额监控
│   ├── sync-infra.sh       # 批量同步脚本
│   ├── install-agent-daemon.sh
│   ├── oci-arm-grab.sh
│   ├── oci-arm-retry.sh
│   ├── snapshot_dispatch_db.py
│   └── *.service           # systemd 服务
│
├── guardian_alerts/        # 告警文件 (自动生成)
├── infra-guardian.log      # 守护日志
└── snapshots/              # DB 备份
```

---

## 自动化建议 (Cron)

```bash
# 每天凌晨 3 点备份 DB
0 3 * * * python3 ~/Downloads/dispatch/snapshot_dispatch_db.py >> /var/log/dispatch-backup.log 2>&1

# 每小时同步一次基础设施
0 * * * * bash ~/Downloads/dispatch/sync-infra.sh >> /var/log/sync-infra.log 2>&1

# 每天早上 9 点发集群报告
0 9 * * * python3 ~/Downloads/dispatch/dispatch.py status | mail -s "Dispatch Report" team@oysterlabs.com
```
