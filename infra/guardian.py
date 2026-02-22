#!/usr/bin/env python3
"""
infra-guardian: 24/7 自治基础设施守护进程
每 5 分钟自动检测并修复基础设施问题
"""

import os
import sys
import json
import time
import subprocess
import sqlite3
import hashlib
import shutil
from datetime import datetime
from pathlib import Path

# 配置路径
DISPATCH_DIR = Path.home() / "Downloads" / "dispatch"
DB_PATH = DISPATCH_DIR / "dispatch.db"
CONFIG_PATH = DISPATCH_DIR / "guardian_config.json"
LOG_FILE = DISPATCH_DIR / "infra-guardian.log"
ALERT_DIR = DISPATCH_DIR / "guardian_alerts"

# 节点列表
NODES = ["codex-node-1", "glm-node-2", "glm-node-3", "glm-node-4", "howard-mac2"]


def load_nodes():
    """Load node configuration from nodes.json"""
    nodes_file = DISPATCH_DIR / "nodes.json"
    if nodes_file.exists():
        with open(nodes_file) as f:
            data = json.load(f)
            # Handle both formats: {"nodes": [...]} or [...]
            if isinstance(data, dict) and "nodes" in data:
                return data["nodes"]
            return data
    # Fallback to basic config
    return [
        {"name": "codex-node-1", "ssh_host": "codex-node-1", "slots": 8},
        {"name": "glm-node-2", "ssh_host": "glm-node-2", "slots": 8},
        {"name": "glm-node-3", "ssh_host": "glm-node-3", "slots": 8},
        {"name": "glm-node-4", "ssh_host": "glm-node-4", "slots": 8},
    ]


# 默认配置
DEFAULT_CONFIG = {
    "interval_seconds": 300,
    "max_fix_attempts": 2,
    "backup_retention_days": 7,
    "log_file": str(LOG_FILE),
    "alert_dir": str(ALERT_DIR),
    "minimax_timeout": 30,
    "minimax_fallback": "rules",
    "checks": {
        "db_schema": True,
        "wrapper_version": True,
        "ssh_connection": True,
        "node_availability": True,
        "param_alignment": True,
    },
}


def log(msg: str, level: str = "INFO"):
    """写日志"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def send_alert(alert_type: str, message: str, severity: int):
    """发送告警到告警目录"""
    ALERT_DIR.mkdir(parents=True, exist_ok=True)

    alert_file = (
        ALERT_DIR / f"{alert_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

    alert_data = {
        "type": alert_type,
        "message": message,
        "severity": severity,
        "timestamp": datetime.now().isoformat(),
    }

    with open(alert_file, "w") as f:
        json.dump(alert_data, f, indent=2)

    log(f"ALERT [{severity}]: {alert_type} - {message}", "WARN")

    # Also print to stderr for visibility
    print(f"🚨 ALERT: {message}", file=sys.stderr)


def ensure_config():
    """确保配置文件存在"""
    if not CONFIG_PATH.exists():
        with open(CONFIG_PATH, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        log("Created default config")


def ensure_alert_dir():
    """确保告警目录存在"""
    ALERT_DIR.mkdir(parents=True, exist_ok=True)


def init_db():
    """初始化 guardian_events 表"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS guardian_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT (datetime('now')),
            check_type TEXT NOT NULL,
            issue_key TEXT,
            severity INTEGER,
            status TEXT CHECK(status IN ('detected','fixing','fixed','failed','rolled_back')),
            fix_attempts INTEGER DEFAULT 0,
            details TEXT,
            node TEXT
        )
    """)
    conn.commit()
    conn.close()


def record_event(
    check_type: str,
    issue_key: str,
    severity: int,
    status: str,
    details: dict,
    node: str = None,
):
    """记录事件到数据库"""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=5.0)
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO guardian_events (check_type, issue_key, severity, status, details, node)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (check_type, issue_key, severity, status, json.dumps(details), node),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Warning: Failed to record event: {e}")


def run_cmd(cmd: list, timeout: int = 30) -> tuple:
    """运行命令，返回 (returncode, stdout, stderr)"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"
    except Exception as e:
        return -1, "", str(e)


def ssh_cmd(node: str, cmd: str, timeout: int = 30) -> tuple:
    """SSH 到节点执行命令，带超时和重试"""
    # Add connection timeout and retry
    ssh_opts = [
        "-o",
        "ConnectTimeout=10",
        "-o",
        "ServerAliveInterval=5",
        "-o",
        "ServerAliveCountMax=3",
    ]

    # Retry up to 2 times
    for attempt in range(2):
        try:
            result = subprocess.run(
                ["ssh"] + ssh_opts + [node, cmd],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            if attempt == 1:
                return -1, "", "Timeout"
            time.sleep(1)
            continue
        except Exception as e:
            if attempt == 1:
                return -1, "", str(e)
            time.sleep(1)
            continue

    return -1, "", "Unknown error"


# ============ C1: DB Schema 同步 ============


def check_db_schema():
    """C1: 检测 DB Schema"""
    log("=== C1: Checking DB Schema ===")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 获取 tasks 表结构
    c.execute("PRAGMA table_info(tasks)")
    columns = {row[1] for row in c.fetchall()}
    conn.close()

    expected_columns = {
        "id",
        "project",
        "spec_file",
        "spec_hash",
        "status",
        "node",
        "pid",
        "attempt",
        "max_retries",
        "started_at",
        "completed_at",
        "collected_at",
        "heartbeat_at",
        "error",
        "log_file",
        "duration_seconds",
        "depends_on",
        "modifies",
        "exclusive",
        "priority",
    }

    missing = expected_columns - columns
    if missing:
        log(f"DB Schema: Missing columns {missing}", "WARN")
        return {"status": "missing_columns", "missing": list(missing), "severity": 3}

    log("DB Schema: OK")
    return {"status": "ok", "severity": 0}


def fix_db_schema(config: dict) -> bool:
    """修复 DB Schema"""
    log("Fixing DB Schema...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 尝试添加缺失的列
    # 注意：这里需要根据实际情况添加列
    # 这里只是示例，实际应该更智能

    # 检查 completed_at 是否存在
    c.execute("PRAGMA table_info(tasks)")
    columns = {row[1] for row in c.fetchall()}

    if "collected_at" not in columns:
        try:
            c.execute("ALTER TABLE tasks ADD COLUMN collected_at TEXT")
            log("Added collected_at column")
        except Exception as e:
            log(f"Failed to add collected_at: {e}", "ERROR")

    if "heartbeat_at" not in columns:
        try:
            c.execute("ALTER TABLE tasks ADD COLUMN heartbeat_at TEXT")
            log("Added heartbeat_at column")
        except Exception as e:
            log(f"Failed to add heartbeat_at: {e}", "ERROR")

    conn.commit()
    conn.close()
    return True


# ============ C2: Wrapper 版本 ============


def check_wrapper_version():
    """C2: 检测 wrapper 版本"""
    log("=== C2: Checking Wrapper Version ===")

    local_path = DISPATCH_DIR / "task-wrapper.sh"
    if not local_path.exists():
        return {"status": "local_missing", "severity": 5}

    # 本地 hash
    code, local_md5, _ = run_cmd(["md5sum", str(local_path)])
    local_hash = local_md5.split()[0] if code == 0 else None

    issues = []
    for node in NODES:
        code, remote_md5, _ = ssh_cmd(
            node,
            "md5sum ~/Downloads/dispatch/task-wrapper.sh 2>/dev/null || md5sum ~/task-wrapper.sh 2>/dev/null",
        )
        if code != 0:
            issues.append({"node": node, "status": "not_found", "severity": 4})
            continue

        remote_hash = remote_md5.split()[0] if remote_md5 else None
        if remote_hash != local_hash:
            issues.append(
                {
                    "node": node,
                    "status": "mismatch",
                    "local": local_hash,
                    "remote": remote_hash,
                    "severity": 3,
                }
            )

    if issues:
        log(f"Wrapper Version: {len(issues)} nodes out of sync", "WARN")
        return {"status": "out_of_sync", "issues": issues, "severity": 3}

    log("Wrapper Version: OK")
    return {"status": "ok", "severity": 0}


def fix_wrapper_version(config: dict) -> bool:
    """修复 wrapper 版本"""
    log("Fixing Wrapper Version...")

    local_path = DISPATCH_DIR / "task-wrapper.sh"
    if not local_path.exists():
        log("Local wrapper missing!", "ERROR")
        return False

    for node in NODES:
        # 备份
        ssh_cmd(node, "cp ~/task-wrapper.sh ~/task-wrapper.sh.bak 2>/dev/null || true")

        # 推送
        code, _, err = run_cmd(["scp", str(local_path), f"{node}:~/task-wrapper.sh"])
        if code != 0:
            log(f"Failed to push wrapper to {node}: {err}", "ERROR")
            continue

        log(f"Pushed wrapper to {node}")

    return True


# ============ C3: SSH ControlMaster ============


def check_ssh_connection():
    """C3: 检测 SSH ControlMaster"""
    log("=== C3: Checking SSH Connection ===")

    issues = []
    for node in NODES:
        code, out, err = run_cmd(["ssh", "-O", "check", node])
        if code != 0:
            issues.append({"node": node, "status": "dead", "error": err, "severity": 4})

    if issues:
        log(f"SSH Connection: {len(issues)} nodes unreachable", "WARN")
        return {"status": "unreachable", "issues": issues, "severity": 4}

    log("SSH Connection: OK")
    return {"status": "ok", "severity": 0}


def fix_ssh_connection(config: dict) -> bool:
    """修复 SSH ControlMaster"""
    log("Fixing SSH Connection...")

    for node in NODES:
        # 检查连接状态
        code, _, _ = run_cmd(["ssh", "-O", "check", node])
        if code != 0:
            # 杀掉可能存在的死连接
            run_cmd(["ssh", "-O", "exit", node])

            # 重建连接 (后台)
            code, _, err = run_cmd(["ssh", "-N", "-f", node])
            if code != 0:
                log(f"Failed to reconnect {node}: {err}", "ERROR")
                continue

            log(f"Reconnected {node}")

    return True


# ============ C4: 节点可用性 ============


def check_node_availability():
    """C4: 检测节点工具可用性"""
    log("=== C4: Checking Node Availability ===")

    issues = []
    for node in NODES:
        # 检查基本命令
        code, out, err = ssh_cmd(node, "which python3 && which git && echo OK")
        if code != 0 or "OK" not in out:
            issues.append(
                {"node": node, "status": "missing_tools", "error": err, "severity": 3}
            )
            continue

        # 检查 dispatch 目录
        code, _, _ = ssh_cmd(node, "ls ~/Downloads/dispatch 2>/dev/null | head -1")
        if code != 0:
            issues.append({"node": node, "status": "no_dispatch_dir", "severity": 4})

    if issues:
        log(f"Node Availability: {len(issues)} nodes have issues", "WARN")
        return {"status": "issues", "issues": issues, "severity": 3}

    log("Node Availability: OK")
    return {"status": "ok", "severity": 0}


# ============ C4b: Task Watcher 监控 ============


def check_task_watcher():
    """C4b: 检测 task-watcher 进程，死了自动重启"""
    log("=== C4b: Checking Task Watcher ===")

    # 要监控的节点列表
    watcher_nodes = [
        ("glm-node-3", "/home/howardli/dispatch"),
        ("glm-node-4", "/home/howardli/dispatch"),
    ]

    issues = []
    fixed = 0

    for node, dispatch_dir in watcher_nodes:
        # 检查 task-watcher 是否在运行
        code, out, _ = ssh_cmd(node, "pgrep -f '[t]ask-watcher.py' | head -1")

        if code != 0 or not out.strip():
            # 没运行，需要启动
            log(f"Task watcher not running on {node}, starting...")

            # 启动 watcher
            start_cmd = f"cd ~ && DISPATCH_DIR={dispatch_dir} nohup python3 {dispatch_dir}/task-watcher.py {node} 8 > /tmp/watcher.log 2>&1 &"
            ssh_cmd(node, start_cmd)

            issues.append({"node": node, "status": "restarted", "severity": 2})
            fixed += 1
            log(f"Restarted task-watcher on {node}")
        else:
            log(f"Task watcher running on {node} (PID: {out.strip()})")

    if issues:
        return {"status": "restarted", "issues": issues, "fixed": fixed, "severity": 2}

    log("Task Watcher: All OK")
    return {"status": "ok", "severity": 0}


def fix_node_availability(config: dict) -> bool:
    """修复节点可用性 - 记录告警，不自动安装"""
    log("Node Availability: Manual intervention required", "WARN")
    # 不自动执行 sudo 命令
    return False


# ============ C5: 参数对齐 ============


def check_param_alignment():
    """C5: 检测参数对齐"""
    log("=== C5: Checking Param Alignment ===")
    # 简化版本：只检查 dispatch.py 和 wrapper 是否都存在
    dispatch_py = DISPATCH_DIR / "dispatch.py"
    wrapper = DISPATCH_DIR / "task-wrapper.sh"

    if not dispatch_py.exists() or not wrapper.exists():
        return {"status": "files_missing", "severity": 2}

    log("Param Alignment: OK (manual check required)")
    return {"status": "ok", "severity": 0}


# ============ C6: 代码同步检查 ============


def check_code_sync():
    """C6: 检测节点代码同步状态"""
    log("=== C6: Checking Code Sync ===")

    # 要检查的项目
    projects = ["clawmarketing", "gem-platform"]
    nodes = ["glm-node-3", "glm-node-4"]

    issues = []

    for node in nodes:
        for project in projects:
            local_path = Path.home() / "Downloads" / project
            remote_path = f"~/dispatch/{project}"

            # 检查远程目录是否存在
            check_cmd = f"test -d {remote_path} && echo exists || echo missing"
            code, out, _ = ssh_cmd(node, check_cmd)

            if "missing" in out or code != 0:
                issues.append(
                    {
                        "node": node,
                        "project": project,
                        "status": "missing",
                        "severity": 4,
                    }
                )
                log(f"Code missing: {project} on {node}")

    if issues:
        log(f"Code Sync: {len(issues)} projects missing", "WARN")
        return {"status": "missing", "issues": issues, "severity": 4}

    log("Code Sync: All OK")
    return {"status": "ok", "severity": 0}


def fix_code_sync(config: dict) -> bool:
    """C6: 自动同步代码"""
    log("Syncing missing code to nodes...")

    projects = ["clawmarketing", "gem-platform"]
    nodes = ["glm-node-3", "glm-node-4"]

    fixed = 0
    for node in nodes:
        for project in projects:
            local_path = Path.home() / "Downloads" / project
            remote_path = f"~/dispatch/{project}"

            # 检查远程是否存在
            check_cmd = f"test -d {remote_path} && echo exists || echo missing"
            code, out, _ = ssh_cmd(node, check_cmd)

            if "missing" in out or code != 0:
                log(f"Rsyncing {project} to {node}...")

                # Rsync
                rsync_cmd = [
                    "rsync",
                    "-az",
                    "--exclude",
                    ".git",
                    "--exclude",
                    "node_modules",
                    "--exclude",
                    "__pycache__",
                    "--exclude",
                    ".venv",
                    f"{local_path}/",
                    f"{node}:{remote_path}",
                ]
                result = subprocess.run(rsync_cmd, capture_output=True, timeout=600)

                if result.returncode == 0:
                    log(f"Synced {project} to {node}")
                    fixed += 1
                else:
                    error_msg = (
                        result.stderr.decode()[:100] if result.stderr else "Unknown"
                    )
                    log(f"Failed to sync {project}: {error_msg}", "ERROR")
                    send_alert(
                        "CODE_SYNC_FAILED", f"{project} to {node}: {error_msg}", 4
                    )

    if fixed > 0:
        log(f"Synced {fixed} projects")
        return True
    return False


# ============ T1: 任务卡死检测 ============


def check_task_stuck():
    """T1: 任务卡死 - 激进自动修复"""
    log("=== T1: Checking Stuck Tasks ===")

    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    from datetime import timedelta

    four_hours_ago = datetime.now() - timedelta(hours=4)

    fixed = 0

    # 运行超过 4 小时的任务 → 自动标记失败
    long_running = c.execute(
        """
        SELECT id, project, node
        FROM tasks
        WHERE status = 'running' AND started_at < ?
    """,
        (four_hours_ago.isoformat(),),
    ).fetchall()

    for task in long_running:
        c.execute(
            "UPDATE tasks SET status = 'failed', error = 'Guardian: running >4h, auto-failed' WHERE id = ?",
            (task["id"],),
        )
        log(f"Auto-fixed: {task['id']} marked failed (>4h)")
        record_event(
            "T1",
            f"long_running_{task['id']}",
            2,
            "fixed",
            {"task_id": task["id"], "action": "marked_failed"},
            task["node"],
        )
        fixed += 1

    # 无心跳 + 无 PID 的可疑任务 → 自动标记失败
    suspicious = c.execute("""
        SELECT id, project, node
        FROM tasks
        WHERE status = 'running' 
        AND (heartbeat_at IS NULL OR pid IS NULL OR pid = 0)
    """).fetchall()

    for task in suspicious:
        c.execute(
            "UPDATE tasks SET status = 'failed', error = 'Guardian: no heartbeat/PID, auto-failed' WHERE id = ?",
            (task["id"],),
        )
        log(f"Auto-fixed: {task['id']} marked failed (no heartbeat)")
        record_event(
            "T1",
            f"no_heartbeat_{task['id']}",
            3,
            "fixed",
            {"task_id": task["id"], "action": "marked_failed"},
            task["node"],
        )
        fixed += 1

    conn.commit()
    conn.close()

    if fixed > 0:
        log(f"Auto-fixed {fixed} stuck tasks")
        return {"status": "fixed", "fixed": fixed, "severity": 2}

    log("No stuck tasks")
    return {"status": "ok", "severity": 0}


def sync_task_status_from_nodes():
    """Sync task completion status from remote nodes to central DB"""
    log("=== Sync: Checking node status files ===")

    import json
    from pathlib import Path

    # Get all running and failed tasks
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Also check failed tasks that might have actually completed on node
    all_tasks = c.execute("""
        SELECT id, project, node, status
        FROM tasks
        WHERE status IN ('running', 'failed')
    """).fetchall()

    if not all_tasks:
        log("No tasks to sync")
        conn.close()
        return {"status": "ok", "synced": 0}

    # Get node info
    nodes = load_nodes()
    node_map = {n["name"]: n["ssh_host"] for n in nodes}

    synced = 0

    for task in all_tasks:
        task_id = task["id"]
        project = task["project"]
        node = task["node"]

        if node not in node_map:
            continue

        ssh_host = node_map[node]
        remote_status_file = f"~/dispatch/{project}/tasks/{task_id}/status.json"

        # Try to read status from node
        cmd = f"cat {remote_status_file} 2>/dev/null"
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=5", ssh_host, cmd],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            continue

        try:
            remote_status = json.loads(result.stdout)
            status = remote_status.get("status", "")

            # Update DB if task completed or failed on node
            if status == "completed":
                c.execute(
                    """
                    UPDATE tasks 
                    SET status = 'completed', 
                        completed_at = ?,
                        error = NULL
                    WHERE id = ?
                """,
                    (
                        remote_status.get("completed_at", datetime.now().isoformat()),
                        task_id,
                    ),
                )
                log(f"Sync: {task_id} marked completed (from {node})")
                synced += 1
            elif status == "failed":
                c.execute(
                    """
                    UPDATE tasks 
                    SET status = 'failed', 
                        completed_at = ?,
                        error = ?
                    WHERE id = ?
                """,
                    (
                        remote_status.get("completed_at", datetime.now().isoformat()),
                        remote_status.get("error", "Task failed on node"),
                        task_id,
                    ),
                )
                log(f"Sync: {task_id} marked failed (from {node})")
                synced += 1
        except json.JSONDecodeError:
            continue

    conn.commit()
    conn.close()

    if synced > 0:
        log(f"Synced {synced} task statuses from nodes")
        return {"status": "synced", "synced": synced, "severity": 1}

    return {"status": "ok", "synced": 0}


def fix_task_stuck(config: dict) -> bool:
    """修复卡死任务 - 只记录告警，不自动处理（wrapper 不发心跳）"""
    log("Task stuck check is informational only - no auto-fix")
    return False


# ============ T2: 进程挂掉检测 ============


def check_process_dead():
    """T2: 检测进程挂掉 - 简化版"""
    log("=== T2: Checking Dead Processes ===")
    # Wrapper PID 逻辑复杂，暂时只记录状态
    log("Process dead check is informational only")
    return {"status": "ok", "severity": 0}


def fix_process_dead(config: dict) -> bool:
    """修复进程挂掉 - 暂不自动处理"""
    return False


# ============ T3: Wrapper 崩溃检测 ============


def check_wrapper_crash():
    """T3: 检测 Wrapper 崩溃（exit code 非 0）"""
    log("=== T3: Checking Wrapper Crashes ===")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 查找最近失败的任务
    failed_recent = c.execute("""
        SELECT id, project, node, error, completed_at
        FROM tasks
        WHERE status = 'failed'
        AND completed_at > datetime('now', '-1 hour')
    """).fetchall()

    conn.close()

    issues = []
    for task in failed_recent:
        issues.append(
            {
                "task_id": task["id"],
                "project": task["project"],
                "node": task["node"],
                "error": task["error"],
                "severity": 3,
            }
        )

    if issues:
        log(f"Found {len(issues)} wrapper crashes in last hour", "WARN")
        return {"status": "crashes", "tasks": issues, "severity": 3}

    log("No recent wrapper crashes")
    return {"status": "ok", "severity": 0}


# ============ T4: DAG 卡住检测 ============


def check_dag_stuck():
    """T4: 检测 DAG 卡住 - 自动修复依赖失败"""
    log("=== T4: Checking DAG Stuck ===")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    fixed_count = 0

    # 找 pending 且有依赖的任务
    pending_with_deps = c.execute("""
        SELECT id, project, depends_on
        FROM tasks
        WHERE status = 'pending' AND depends_on != '[]' AND depends_on != ''
    """).fetchall()

    for task in pending_with_deps:
        depends_on = json.loads(task["depends_on"] or "[]")
        if not depends_on:
            continue

        # 检查依赖状态
        deps = c.execute(
            f"""
            SELECT id, status FROM tasks WHERE id IN ({",".join("?" * len(depends_on))})
        """,
            depends_on,
        ).fetchall()

        dep_statuses = {d["id"]: d["status"] for d in deps}

        # 检查是否有失败的依赖
        failed_deps = [
            d_id for d_id, status in dep_statuses.items() if status == "failed"
        ]
        if failed_deps:
            # 依赖失败了，标记这个任务也失败
            c.execute(
                "UPDATE tasks SET status = 'failed', error = ? WHERE id = ?",
                (f"Guardian: dependency failed: {', '.join(failed_deps)}", task["id"]),
            )
            log(
                f"Auto-fixed: Marked {task['id']} as failed (dependency failed: {failed_deps})"
            )
            record_event(
                "T4",
                f"dep_failed_{task['id']}",
                3,
                "fixed",
                {"task_id": task["id"], "failed_deps": failed_deps},
            )
            fixed_count += 1
            continue

        # 检查依赖是否都完成
        all_done = all(status == "completed" for status in dep_statuses.values())
        if all_done:
            # 依赖都完成了但还是 pending，这是不应该的
            # 可能需要重新调度，但 Guardian 不做调度决策，只记录
            log(f"Task {task['id']} ready but not scheduled (informational)")
            record_event(
                "T4",
                f"ready_not_scheduled_{task['id']}",
                1,
                "detected",
                {"task_id": task["id"], "depends_on": depends_on},
            )

    conn.commit()
    conn.close()

    if fixed_count > 0:
        log(f"Auto-fixed {fixed_count} tasks with failed dependencies")
        return {"status": "fixed", "fixed": fixed_count, "severity": 2}

    log("No DAG stuck")
    return {"status": "ok", "severity": 0}


# ============ T5: 节点过载检测 ============


def check_node_overload():
    """T5: 检测节点过载（slots 满但有 pending）"""
    log("=== T5: Checking Node Overload ===")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 统计每个节点 running 任务数
    running_by_node = c.execute("""
        SELECT node, COUNT(*) as running_count
        FROM tasks
        WHERE status = 'running'
        GROUP BY node
    """).fetchall()

    # 获取节点 slots
    nodes_config = c.execute("SELECT name, slots FROM nodes").fetchall()
    node_slots = {n["name"]: n["slots"] for n in nodes_config}

    # 检查 pending 任务数
    pending_count = c.execute(
        "SELECT COUNT(*) FROM tasks WHERE status = 'pending'"
    ).fetchone()[0]

    conn.close()

    overloaded = []
    for node_data in running_by_node:
        node = node_data["node"]
        running = node_data["running_count"]
        slots = node_slots.get(node, 8)

        if running >= slots and pending_count > 0:
            overloaded.append(
                {
                    "node": node,
                    "running": running,
                    "slots": slots,
                    "pending": pending_count,
                    "severity": 2,
                }
            )

    if overloaded:
        log(f"Found {len(overloaded)} overloaded nodes", "WARN")
        return {"status": "overloaded", "nodes": overloaded, "severity": 2}

    log("No node overload")
    return {"status": "ok", "severity": 0}


# ============ T6: SSH 断联检测 ============


def check_ssh_disconnect():
    """T6: 检测 SSH 断联"""
    # 这个和 C3 SSH 合并了
    return check_ssh_connection()


# ============ C7: 任务执行监控 ============


def check_task_execution():
    """C7: 检测长期 pending 但未执行的任务"""
    log("=== C7: Checking Task Execution ===")

    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 查找 pending 超过 30 分钟的任务（可能没被 watcher 执行）
    from datetime import timedelta

    thirty_mins_ago = datetime.now() - timedelta(minutes=30)

    stuck_pending = c.execute(
        """
        SELECT id, project, created_at
        FROM tasks
        WHERE status = 'pending' AND created_at < ?
        ORDER BY created_at ASC
    """,
        (thirty_mins_ago.isoformat(),),
    ).fetchall()

    conn.close()

    issues = []
    for task in stuck_pending:
        issues.append(
            {
                "task_id": task["id"],
                "project": task["project"],
                "created_at": task["created_at"],
                "severity": 2,
            }
        )

    if issues:
        log(f"Found {len(issues)} pending tasks >30min", "WARN")
        return {"status": "stuck_pending", "tasks": issues, "severity": 2}

    log("Task Execution: OK")
    return {"status": "ok", "severity": 0}


# ============ 主循环 ============


def run_cycle(config: dict):
    """执行一轮检查"""
    checks = config.get("checks", {})

    results = []

    # C1: DB Schema
    if checks.get("db_schema"):
        result = check_db_schema()
        results.append(("C1", result))
        if result.get("severity", 0) > 0:
            fix_db_schema(config)
            record_event("C1", "db_schema", result["severity"], "fixed", result)

    # C2: Wrapper Version
    if checks.get("wrapper_version"):
        result = check_wrapper_version()
        results.append(("C2", result))
        if result.get("severity", 0) > 0:
            fix_wrapper_version(config)
            record_event("C2", "wrapper_version", result["severity"], "fixed", result)

    # C3: SSH Connection
    if checks.get("ssh_connection"):
        result = check_ssh_connection()
        results.append(("C3", result))
        if result.get("severity", 0) > 0:
            fix_ssh_connection(config)
            record_event("C3", "ssh_connection", result["severity"], "fixed", result)

    # C4: Node Availability
    if checks.get("node_availability"):
        result = check_node_availability()
        results.append(("C4", result))
        if result.get("severity", 0) > 0:
            record_event(
                "C4", "node_availability", result["severity"], "failed", result
            )

    # C4b: Task Watcher
    if checks.get("task_watcher"):
        result = check_task_watcher()
        results.append(("C4b", result))

    # C5: Param Alignment
    if checks.get("param_alignment"):
        result = check_param_alignment()
        results.append(("C5", result))

    # C6: Code Sync
    if checks.get("code_sync"):
        result = check_code_sync()
        results.append(("C6", result))
        if result.get("severity", 0) > 0:
            fix_code_sync(config)
            record_event("C6", "code_sync", result["severity"], "fixed", result)

    # C7: Task Execution
    if checks.get("task_execution"):
        result = check_task_execution()
        results.append(("C7", result))

    # T1: Stuck Tasks
    if checks.get("task_stuck"):
        result = check_task_stuck()
        results.append(("T1", result))
        if result.get("severity", 0) > 0:
            fix_task_stuck(config)
            record_event("T1", "task_stuck", result["severity"], "fixed", result)

    # Sync task status from nodes
    sync_result = sync_task_status_from_nodes()
    results.append(("SYNC", sync_result))

    # T2: Dead Processes
    if checks.get("process_dead"):
        result = check_process_dead()
        results.append(("T2", result))
        if result.get("severity", 0) > 0:
            fix_process_dead(config)
            record_event("T2", "process_dead", result["severity"], "fixed", result)

    # T3: Wrapper Crashes
    if checks.get("wrapper_crash"):
        result = check_wrapper_crash()
        results.append(("T3", result))

    # T4: DAG Stuck
    if checks.get("dag_stuck"):
        result = check_dag_stuck()
        results.append(("T4", result))

    # T5: Node Overload
    if checks.get("node_overload"):
        result = check_node_overload()
        results.append(("T5", result))

    return results


def main():
    """主入口"""
    log("=" * 50)
    log("infra-guardian starting...")
    log("=" * 50)

    ensure_config()
    ensure_alert_dir()
    init_db()

    # 加载配置
    with open(CONFIG_PATH) as f:
        config = json.load(f)

    interval = config.get("interval_seconds", 300)

    log(f"Interval: {interval}s")
    log(f"Checks: {config.get('checks', {})}")

    cycle_count = 0
    while True:
        cycle_count += 1
        log(f"=== Cycle {cycle_count} ===")

        try:
            run_cycle(config)
        except Exception as e:
            log(f"Cycle error: {e}", "ERROR")

        log(f"Sleeping {interval}s...")
        time.sleep(interval)


if __name__ == "__main__":
    main()
