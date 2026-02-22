---
task_id: S10-infra-guardian
project: dispatch
priority: 1
depends_on: []
modifies:
  - dispatch/guardian.py
  - dispatch/guardian_config.json
executor: glm
---

# Infra Guardian: 24/7 自治基础设施守护进程

## 目标
构建独立守护进程，每 5 分钟自动检测基础设施问题、自己规划修复、自己执行、自己验证。全程不需要人工。

## 背景
2026-02-12 整个 session 烧在手动修 DB schema 不同步、wrapper 版本不一致、SSH 断开等问题上。这些问题完全可以自动化解决。

## 架构

```
Scheduler (5min) → Inspector (检测) → MiniMax Analyzer (分析+方案) → Executor (备份+修复) → Verifier (验证)
                                                                          ↓ 失败≥2次
                                                                     Notifier (告警文件)
```

**运行方式**: launchd 管理，独立 Python 进程
**AI 引擎**: MiniMax M2.5 (通过 `mm` CLI)，fallback 到 claude-glm

## 检查项 (5 项)

### C1: DB Schema 同步
- **检测**: `PRAGMA table_info()` 对比期望列定义 (硬编码在 guardian 中)
- **修复**: `ALTER TABLE ... ADD COLUMN ...`
- **回滚**: 不回滚 (只加列不删列)

### C2: 远端 Wrapper 版本
- **检测**: 本地 `md5 task-wrapper.sh` vs `ssh <node> "md5sum ~/task-wrapper.sh"`
- **修复**: `scp task-wrapper.sh <node>:~/task-wrapper.sh` (修前先 `cp .bak`)
- **回滚**: `ssh <node> "cp ~/task-wrapper.sh.bak ~/task-wrapper.sh"`

### C3: SSH ControlMaster 连通性
- **检测**: `ssh -O check <node>` 检查 socket
- **修复**: 删死 socket → `ssh -N -f <node>` 重建
- **回滚**: 无需

### C4: 节点基础可用性
- **检测**: `ssh <node> "which claude && which claude-glm && which mm && echo OK"`
- **修复**: 调 MiniMax 分析缺了什么 → 生成安装命令 → SSH 执行
- **回滚**: 记录已安装的包，失败时卸载

### C5: dispatch.py 与 wrapper 参数对齐
- **检测**: 解析 dispatch.py 中 `ssh ... task-wrapper.sh` 的调用行，提取参数列表；解析 wrapper 的 `$1 $2 ...` 接收顺序
- **修复**: 这个太复杂不自动修 → 只记录告警，MiniMax 生成修复建议写到告警文件
- **回滚**: N/A

## MiniMax 集成

何时调用 MiniMax:
1. **问题分析**: Inspector 发现异常后，发给 MiniMax 判断严重性 (1-5) 和根因
2. **修复规划**: 非标准问题 (C4 节点缺工具等) 需要 MiniMax 生成修复命令
3. **重复问题学习**: 同一 issue_key 第 3 次出现 → MiniMax 做根因分析，建议预防措施

调用方式:
```python
import subprocess
result = subprocess.run(["mm", prompt], capture_output=True, text=True)
```

MiniMax 不可用时 → fallback 到硬编码规则引擎 (每个检查项都有 if/else 修复逻辑)

## 数据存储

guardian_events 表 (在 dispatch.db 中):
```sql
CREATE TABLE IF NOT EXISTS guardian_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT DEFAULT (datetime('now')),
    check_type TEXT NOT NULL,        -- C1/C2/C3/C4/C5
    issue_key TEXT,                   -- 去重用
    severity INTEGER,                -- 1-5
    status TEXT CHECK(status IN ('detected','fixing','fixed','failed','rolled_back')),
    fix_attempts INTEGER DEFAULT 0,
    details TEXT,                     -- JSON
    node TEXT                        -- 涉及的节点
);
```

## 文件清单

| 文件 | 操作 | 描述 |
|------|------|------|
| `dispatch/guardian.py` | 新建 | 主守护进程 (~500行) |
| `dispatch/guardian_config.json` | 新建 | 配置 (检查间隔、重试次数、MiniMax 超时等) |
| `~/Library/LaunchAgents/com.oyster.infra-guardian.plist` | 新建 | launchd 服务 |
| `dispatch/dispatch.db` | 修改 | 新增 guardian_events 表 |

## guardian_config.json 结构

```json
{
  "interval_seconds": 300,
  "max_fix_attempts": 2,
  "backup_retention_days": 7,
  "log_file": "~/Downloads/dispatch/infra-guardian.log",
  "alert_dir": "~/Downloads/dispatch/guardian_alerts/",
  "minimax_timeout": 30,
  "minimax_fallback": "rules",
  "checks": {
    "db_schema": true,
    "wrapper_version": true,
    "ssh_connection": true,
    "node_availability": true,
    "param_alignment": true
  },
  "expected_schema": {
    "tasks": ["id", "project", "task_id", "spec_file", "node", "status", "priority", "depends_on", "created_at", "started_at", "completed_at"],
    "nodes": ["id", "name", "ssh_host", "slots", "priority", "status"]
  }
}
```

## 修复流程

```
发现问题 → 备份当前状态 → 执行修复 → 验证
  ↓ 验证失败
回滚 → 重试 (最多 2 次)
  ↓ 仍然失败
写告警文件到 guardian_alerts/ → 停止该检查项修复 → 继续其他检查
```

## 验收标准

- [ ] 每 5 分钟执行一轮完整检查 (5 项)
- [ ] 能检测并修复 DB 缺列 (手动 DROP 一列后自动恢复)
- [ ] 能检测并推送 wrapper 到不一致的节点
- [ ] 能检测并重建断开的 SSH ControlMaster
- [ ] 修复前自动备份，失败自动回滚
- [ ] 失败 2 次后写告警文件，不再重试
- [ ] MiniMax 不可用时 fallback 到规则引擎
- [ ] guardian_events 表正确记录所有事件

## 不要做

- 不修改 dispatch.py 业务逻辑
- 不修改 ~/.ssh/config
- 不执行 sudo 命令
- 不删除 DB 列 (只加不删)
- 不碰 nodes.json 和 projects.json
