#!/usr/bin/env python3
"""
Distributed Task Scheduler Controller
Usage:
  python3 dispatch.py start <project>
  python3 dispatch.py status [<project>]
  python3 dispatch.py report <project>
  python3 dispatch.py collect <project>
  python3 dispatch.py stop <project>
  python3 dispatch.py cleanup <project>
"""

import sqlite3
import subprocess
import json
import re
import hashlib
import argparse
import time
import os
import signal
import sys
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from typing import Optional, Dict, List, Any

# Global flag for graceful shutdown
RUNNING = True


def log(msg):
    """Print timestamped log message"""
    print(f"[{datetime.now().isoformat()}] {msg}", flush=True)


def signal_handler(signum, frame):
    """Handle SIGINT/SIGTERM for graceful shutdown"""
    global RUNNING
    log(f"Received signal {signum}, stopping gracefully...")
    RUNNING = False


@contextmanager
def get_db(db_path):
    """Context manager for database connection"""
    conn = sqlite3.connect(db_path, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_database(db_path):
    """Initialize database schema"""
    with get_db(db_path) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                project TEXT NOT NULL,
                spec_file TEXT NOT NULL,
                spec_hash TEXT,
                status TEXT DEFAULT 'pending' CHECK(status IN ('pending','claimed','running','completed','failed')),
                node TEXT,
                pid INTEGER,
                attempt INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 2,
                started_at TEXT,
                completed_at TEXT,
                collected_at TEXT,
                heartbeat_at TEXT,
                error TEXT,
                log_file TEXT,
                duration_seconds REAL,
                depends_on TEXT DEFAULT '[]',
                modifies TEXT DEFAULT '[]',
                exclusive INTEGER DEFAULT 0,
                priority INTEGER DEFAULT 2
            );

            CREATE TABLE IF NOT EXISTS file_locks (
                file_path TEXT NOT NULL,
                task_id TEXT NOT NULL,
                locked_at TEXT NOT NULL,
                PRIMARY KEY (file_path, task_id)
            );

            CREATE TABLE IF NOT EXISTS nodes (
                name TEXT PRIMARY KEY,
                ssh_host TEXT,
                slots INTEGER DEFAULT 8,
                api_mode TEXT DEFAULT 'direct',
                work_dir TEXT DEFAULT '~/dispatch',
                running_count INTEGER DEFAULT 0,
                last_seen TEXT,
                enabled INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                task_id TEXT,
                event_type TEXT,
                node TEXT,
                details TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
            CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project);
            CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
        """)
        # Migration: add collected_at column to existing databases
        try:
            conn.execute("ALTER TABLE tasks ADD COLUMN collected_at TEXT")
        except sqlite3.OperationalError:
            pass  # column already exists
        conn.commit()


def load_nodes_config(nodes_file):
    """Load nodes configuration from JSON file"""
    with open(nodes_file, "r") as f:
        config = json.load(f)
    return config["nodes"]


def compute_file_hash(file_path):
    """Compute SHA256 hash of file"""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def load_project_config(project):
    """Load project config from projects.json"""
    projects_file = Path(__file__).parent / "projects.json"
    if projects_file.exists():
        with open(projects_file) as f:
            projects = json.load(f)
        return projects.get(project, {})
    return {}


def parse_spec_metadata(spec_path):
    """Extract YAML front-matter from spec file.
    Returns (metadata_dict, content_string).
    If no front-matter, returns empty dict and full content."""
    text = Path(spec_path).read_text()
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            try:
                meta = yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError:
                meta = {}
            content = parts[2].strip()
            return meta, content
    return {}, text


def scan_specs(project, specs_dir):
    """Scan spec files and return list of tasks"""
    # specs_dir already includes the project path, don't add project again
    specs_path = Path(specs_dir)
    if not specs_path.exists():
        log(f"ERROR: Specs directory not found: {specs_path}")
        return []

    # Only treat numeric-prefixed S*/P* files as runnable tasks.
    # This prevents non-task docs like SHARED_CONTEXT.md from being scheduled.
    task_name_re = re.compile(r"^[SP]\d+")
    spec_files = sorted(
        [p for p in specs_path.glob("S*.md") if task_name_re.match(p.stem)]
    ) + sorted([p for p in specs_path.glob("P*.md") if task_name_re.match(p.stem)])
    tasks = []

    for spec_file in spec_files:
        task_id = spec_file.stem
        spec_hash = compute_file_hash(spec_file)
        meta, _ = parse_spec_metadata(spec_file)

        # 校验 modifies 必填（Best Practice: 文件锁机制基础）
        modifies = meta.get("modifies", [])
        if not modifies:
            log(
                f"ERROR: Spec {spec_file} has empty modifies - must list files to modify"
            )
            continue

        tasks.append(
            {
                "id": meta.get("task_id", task_id),
                "project": project,
                "spec_file": str(spec_file),
                "spec_hash": spec_hash,
                "depends_on": json.dumps(meta.get("depends_on", [])),
                "modifies": json.dumps(modifies),
                "exclusive": 1 if meta.get("exclusive", False) else 0,
                "priority": meta.get("priority", 2),
                "executor": meta.get("executor", "glm"),
            }
        )

    log(f"Found {len(tasks)} spec files in {specs_path}")
    return tasks


def init_tasks(db_path, tasks):
    """Initialize tasks in database"""
    with get_db(db_path) as conn:
        for task in tasks:
            conn.execute(
                """
                INSERT OR IGNORE INTO tasks (id, project, spec_file, spec_hash, status, depends_on, modifies, exclusive, priority)
                VALUES (?, ?, ?, ?, 'pending', ?, ?, ?, ?)
            """,
                (
                    task["id"],
                    task["project"],
                    task["spec_file"],
                    task["spec_hash"],
                    task.get("depends_on", "[]"),
                    task.get("modifies", "[]"),
                    task.get("exclusive", 0),
                    task.get("priority", 2),
                ),
            )
        conn.commit()


def acquire_file_locks(db_path, task_id, modifies):
    """Acquire file locks for a task"""
    with get_db(db_path) as conn:
        for f in modifies:
            conn.execute(
                "INSERT INTO file_locks (file_path, task_id, locked_at) VALUES (?, ?, ?)",
                (f, task_id, datetime.now().isoformat()),
            )
        conn.commit()


def release_file_locks(db_path, task_id, conn=None):
    """Release all file locks held by a task"""
    if conn is not None:
        # Use external connection (within existing transaction)
        conn.execute("DELETE FROM file_locks WHERE task_id=?", (task_id,))
    else:
        # Create own connection
        with get_db(db_path) as conn:
            conn.execute("DELETE FROM file_locks WHERE task_id=?", (task_id,))
            conn.commit()


def check_file_conflicts(db_path, modifies):
    """
    Check if any files are currently locked OR being modified by running tasks.
    Best Practice: 所有任务分发前必须检查 modifies 冲突
    """
    if not modifies:
        return []

    # Check file_locks table
    with get_db(db_path) as conn:
        placeholders = ",".join("?" * len(modifies))
        locked = conn.execute(
            f"SELECT file_path, task_id FROM file_locks WHERE file_path IN ({placeholders})",
            modifies,
        ).fetchall()

        # Also check running tasks for modifies overlap
        running_conflicts = conn.execute("""
            SELECT id, modifies FROM tasks 
            WHERE status = 'running' AND modifies != '[]'
        """).fetchall()

        conflicts = [(r["file_path"], r["task_id"]) for r in locked]

        # Check if any running task modifies overlapping files
        for running_task in running_conflicts:
            running_modifies = json.loads(running_task["modifies"] or "[]")
            overlap = set(modifies) & set(running_modifies)
            if overlap:
                conflicts.append((f"{overlap}", running_task["id"]))

        return conflicts


def init_nodes(db_path, nodes):
    """Initialize nodes in database"""
    with get_db(db_path) as conn:
        # Add executor and priority columns if they don't exist
        for col, col_type, default in [
            ("executor", "TEXT", '"glm"'),
            ("priority", "INTEGER", "2"),
        ]:
            try:
                conn.execute(
                    f"ALTER TABLE nodes ADD COLUMN {col} {col_type} DEFAULT {default}"
                )
            except:
                pass  # Column already exists

        for node in nodes:
            conn.execute(
                """
                INSERT OR REPLACE INTO nodes (name, ssh_host, slots, api_mode, executor, priority)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    node["name"],
                    node.get("ssh_host"),
                    node["slots"],
                    node["api_mode"],
                    node.get("executor", "glm"),
                    node.get("priority", 2),
                ),
            )
        conn.commit()


def log_event(db_path, task_id, event_type, node, details):
    """Log an event to database"""
    with get_db(db_path) as conn:
        conn.execute(
            """
            INSERT INTO events (timestamp, task_id, event_type, node, details)
            VALUES (?, ?, ?, ?, ?)
        """,
            (datetime.now().isoformat(), task_id, event_type, node, details),
        )
        conn.commit()


def collect_git(db_path, project):
    """Fetch and merge completed task branches via git"""
    project_config = load_project_config(project)
    if project_config.get("sync_mode") != "git":
        log(f"Project {project} not in git mode, skipping")
        return []

    local_repo = Path(project_config["repo_local"]).expanduser()
    main_branch = project_config.get("main_branch", "main")

    if not local_repo.exists():
        log(f"ERROR: Local repo not found: {local_repo}")
        return []

    subprocess.run(
        ["git", "checkout", main_branch],
        cwd=str(local_repo),
        capture_output=True,
        timeout=30,
    )
    subprocess.run(
        ["git", "fetch", "--all", "--prune"],
        cwd=str(local_repo),
        capture_output=True,
        timeout=60,
    )

    with get_db(db_path) as conn:
        tasks = conn.execute(
            "SELECT id, node FROM tasks WHERE project=? AND status='completed' ORDER BY id",
            (project,),
        ).fetchall()

    merge_report = []
    for task in tasks:
        task_id = task["id"] if isinstance(task, dict) else task[0]
        task_node = task["node"] if isinstance(task, dict) else task[1]
        branch = f"task/{project}-{task_id}-{task_node}"

        result = subprocess.run(
            ["git", "branch", "-r", "--list", f"origin/{branch}"],
            cwd=str(local_repo),
            capture_output=True,
            text=True,
        )
        if not result.stdout.strip():
            merge_report.append({"task": task_id, "status": "no_branch"})
            continue

        result = subprocess.run(
            ["git", "merge", f"origin/{branch}", "--no-ff", "-m", f"Merge {branch}"],
            cwd=str(local_repo),
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            merge_report.append(
                {"task": task_id, "status": "merged", "node": task_node}
            )
            log(f"Merged {branch} successfully")
            subprocess.run(
                ["git", "push", "origin", "--delete", branch],
                cwd=str(local_repo),
                capture_output=True,
                timeout=30,
            )
            with get_db(db_path) as conn:
                conn.execute(
                    "UPDATE tasks SET collected_at=? WHERE id=?",
                    (datetime.now().isoformat(), task_id),
                )
        else:
            subprocess.run(
                ["git", "merge", "--abort"], cwd=str(local_repo), capture_output=True
            )
            conflicts = [l for l in result.stdout.split("\n") if "CONFLICT" in l]
            merge_report.append(
                {"task": task_id, "status": "conflict", "conflicts": conflicts}
            )
            log(f"CONFLICT merging {branch}: {conflicts}")
            log_event(
                db_path,
                task_id,
                "merge_conflict",
                task_node,
                json.dumps({"conflicts": conflicts}),
            )

    report_path = Path(__file__).parent / f"{project}_merge_report.json"
    with open(report_path, "w") as f:
        json.dump(merge_report, f, indent=2)
    log(f"Merge report: {report_path}")
    return merge_report


def collect_scp_outputs(db_path, project):
    """Collect output files from completed tasks on remote nodes via SCP

    Collects:
    - Task logs (task.log, status.json) from task directory
    - Code files from project directory (rsync)
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    nodes_file = Path(__file__).parent / "nodes.json"

    # Get completed tasks
    with get_db(db_path) as conn:
        tasks = conn.execute(
            "SELECT id, node FROM tasks WHERE project=? AND status='completed' AND collected_at IS NULL",
            (project,),
        ).fetchall()

    if not tasks:
        log("No completed tasks to collect")
        return []

    # Get nodes
    nodes = load_nodes_config(nodes_file)
    node_map = {n["name"]: n for n in nodes}

    collected = []

    def collect_from_node(task_id, node_name):
        if node_name not in node_map:
            return None

        node = node_map[node_name]
        ssh_host = node["ssh_host"]

        # Remote task directory
        remote_task_dir = f"~/dispatch/{project}/tasks/{task_id}"

        # Remote project directory (where code files are)
        remote_project_dir = f"~/dispatch/{project}"

        # Local directory
        local_dir = Path(__file__).parent / "output" / project / task_id
        local_dir.mkdir(parents=True, exist_ok=True)

        # 1. Collect task log files
        files_to_collect = ["task.log", "result.json", "status.json"]

        for filename in files_to_collect:
            remote_path = f"{remote_task_dir}/{filename}"
            local_path = local_dir / filename

            # Try to SCP each file
            scp_cmd = f"scp -o ConnectTimeout=10 {ssh_host}:{remote_path} {local_path} 2>/dev/null"
            result = subprocess.run(scp_cmd, shell=True, capture_output=True)

            if result.returncode == 0:
                log(f"Collected {filename} for {task_id} from {node_name}")

        # 2. Sync code files from project directory using rsync
        # This catches all code created by the agent in the project root
        local_project_dir = Path(__file__).parent / "output" / project / task_id
        rsync_cmd = (
            f"rsync -az --exclude='__pycache__' --exclude='.git' --exclude='*.pyc' "
            f"--exclude='node_modules' --exclude='.venv' --exclude='.pytest_cache' "
            f"-e 'ssh -o ConnectTimeout=10' {ssh_host}:{remote_project_dir}/ {local_project_dir}/"
        )
        rsync_result = subprocess.run(rsync_cmd, shell=True, capture_output=True)

        if rsync_result.returncode == 0:
            log(f"Synced code files for {task_id} from {node_name}")
        else:
            # Fallback: try scp for common file types if rsync fails
            log(f"Rsync failed for {task_id}, trying scp fallback")
            common_exts = [
                "*.py",
                "*.js",
                "*.ts",
                "*.tsx",
                "*.json",
                "*.yaml",
                "*.yml",
                "*.md",
                "*.sh",
            ]
            for ext in common_exts:
                scp_cmd = (
                    f"scp -o ConnectTimeout=10 -r {ssh_host}:'{remote_project_dir}/{ext}' "
                    f"{local_project_dir}/ 2>/dev/null"
                )
                subprocess.run(scp_cmd, shell=True, capture_output=True)

        return task_id

    # Collect in parallel
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(collect_from_node, t["id"], t["node"]): t for t in tasks
        }
        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    collected.append(result)
                    # Mark as collected in DB
                    with get_db(db_path) as conn:
                        conn.execute(
                            "UPDATE tasks SET collected_at=? WHERE id=?",
                            (datetime.now().isoformat(), result),
                        )
            except Exception as e:
                log(f"Error collecting task: {e}")

    log(f"Collected {len(collected)} task outputs")
    return collected


def detect_project_type(project_dir: Path) -> str:
    """检测项目类型"""
    if (project_dir / "package.json").exists():
        return "node"
    elif (project_dir / "requirements.txt").exists() or (
        project_dir / "pyproject.toml"
    ).exists():
        return "python"
    elif (project_dir / "go.mod").exists():
        return "go"
    elif (project_dir / "Cargo.toml").exists():
        return "rust"
    return "unknown"


def validate_collected_output(project: str, task_id: str) -> Dict:
    """验证收集的任务产出 - 自动构建测试"""
    dispatch_dir = Path(__file__).parent
    project_dir = dispatch_dir / project

    result = {
        "task_id": task_id,
        "project_type": "unknown",
        "build": {"success": False, "output": ""},
        "test": {"success": False, "output": ""},
        "overall": False,
    }

    # 检测项目类型
    proj_type = detect_project_type(project_dir)
    result["project_type"] = proj_type

    if proj_type == "unknown":
        result["build"]["output"] = "Unknown project type, skipping validation"
        result["overall"] = True  # 跳过验证
        return result

    # 运行构建
    if proj_type == "node":
        build_cmd = (
            ["npm", "run", "build"] if (project_dir / "package.json").exists() else None
        )
        test_cmd = ["npm", "test"] if (project_dir / "package.json").exists() else None
    elif proj_type == "python":
        build_cmd = (
            ["pip", "install", "-r", "requirements.txt"]
            if (project_dir / "requirements.txt").exists()
            else None
        )
        test_cmd = (
            ["pytest"]
            if (project_dir / "pytest.ini").exists() or (project_dir / "tests").exists()
            else None
        )
    elif proj_type == "go":
        build_cmd = ["go", "build", "./..."]
        test_cmd = ["go", "test", "./..."]
    else:
        build_cmd = None
        test_cmd = None

    # 执行构建
    if build_cmd:
        try:
            proc = subprocess.run(
                build_cmd,
                cwd=str(project_dir),
                capture_output=True,
                text=True,
                timeout=300,
            )
            result["build"]["success"] = proc.returncode == 0
            result["build"]["output"] = proc.stdout + proc.stderr
        except subprocess.TimeoutExpired:
            result["build"]["output"] = "Build timeout"
        except Exception as e:
            result["build"]["output"] = str(e)
    else:
        result["build"]["success"] = True
        result["build"]["output"] = "No build required"

    # 执行测试
    if test_cmd:
        try:
            proc = subprocess.run(
                test_cmd,
                cwd=str(project_dir),
                capture_output=True,
                text=True,
                timeout=300,
            )
            result["test"]["success"] = proc.returncode == 0
            result["test"]["output"] = proc.stdout + proc.stderr
        except subprocess.TimeoutExpired:
            result["test"]["output"] = "Test timeout"
        except Exception as e:
            result["test"]["output"] = str(e)
    else:
        result["test"]["success"] = True
        result["test"]["output"] = "No tests required"

    # 总体结果
    result["overall"] = result["build"]["success"] and result["test"]["success"]

    log(
        f"Validation for {task_id}: build={result['build']['success']}, test={result['test']['success']}"
    )
    return result


def collect_and_validate(db_path, project):
    """收集 + 构建 + 测试"""
    # 先收集
    collected = collect_scp_outputs(db_path, project)

    if not collected:
        return {"collected": 0, "validated": 0, "results": []}

    results = []
    dispatch_dir = Path(__file__).parent

    for task_id in collected:
        # 验证每个任务
        validation = validate_collected_output(project, task_id)

        # 保存验证结果
        validation_file = dispatch_dir / project / "tasks" / task_id / "validation.json"
        validation_file.parent.mkdir(parents=True, exist_ok=True)
        validation_file.write_text(json.dumps(validation, indent=2))

        results.append(validation)

    passed = sum(1 for r in results if r["overall"])

    log(f"Validation: {passed}/{len(results)} passed")

    return {
        "collected": len(collected),
        "validated": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "results": results,
    }


def get_task_type(task_id):
    """Determine task type from ID"""
    if task_id.startswith("V"):
        return "verification"
    if task_id.startswith("F"):
        return "fix"
    if task_id == "S99":
        return "integration"
    return "implementation"


def get_executor(task_type):
    """Determine executor from task type"""
    if task_type in ("verification", "fix", "integration"):
        return "codex"
    return "glm"


def build_enriched_spec(project, task_id, spec_content, node_name, db_path):
    """Build enriched spec with 5 layers of context"""
    parts = []

    # Layer 1: Project CLAUDE.md
    for p in [
        Path.home() / "Downloads" / project / "CLAUDE.md",
        Path.home() / "Downloads" / "specs" / project / "CLAUDE.md",
    ]:
        if p.exists():
            parts.append("## Project Instructions\n" + p.read_text()[:3000])
            break

    # Layer 2: claude-mem memory (graceful if DB missing)
    mem_db = Path.home() / ".claude-mem" / "claude-mem.db"
    if mem_db.exists():
        try:
            conn = sqlite3.connect(str(mem_db), timeout=5)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT type, narrative, created_at_epoch FROM observations
                WHERE project LIKE ? AND type IN ('decision','discovery','bugfix')
                ORDER BY created_at_epoch DESC LIMIT 10
            """,
                (f"%{project}%",),
            ).fetchall()
            conn.close()
            if rows:
                lines = [
                    f"- [{r['type']}] {datetime.fromtimestamp(r['created_at_epoch']).strftime('%m/%d')}: {r['narrative'][:200]}"
                    for r in rows
                ]
                parts.append("## Project Memory\n" + "\n".join(lines))
        except Exception:
            pass

    # Layer 3: Intelligent SHARED_CONTEXT (extract relevant sections by keywords)
    shared_path = Path.home() / "Downloads" / "specs" / project / "SHARED_CONTEXT.md"
    if shared_path.exists():
        text = shared_path.read_text()
        # Split by ## headings
        sections = []
        current = []
        for line in text.split("\n"):
            if line.startswith("## ") and current:
                sections.append("\n".join(current))
                current = []
            current.append(line)
        if current:
            sections.append("\n".join(current))

        # Extract keywords from spec
        spec_lower = spec_content.lower()
        keywords = [
            "model",
            "router",
            "auth",
            "database",
            "schema",
            "frontend",
            "react",
            "api",
            "test",
            "persona",
            "agent",
            "twitter",
            "discord",
            "analytics",
            "celery",
            "queue",
        ]
        relevant = [
            s
            for s in sections
            if any(kw in s.lower() for kw in keywords if kw in spec_lower)
        ]
        if relevant:
            parts.append(
                "## Shared Context (Relevant Sections)\n" + "\n\n".join(relevant[:5])
            )

    # Layer 4: Sibling tasks status
    if db_path and Path(db_path).exists():
        try:
            conn2 = sqlite3.connect(str(db_path), timeout=5)
            conn2.row_factory = sqlite3.Row
            siblings = conn2.execute(
                "SELECT id, status, node, spec_file FROM tasks WHERE project=? AND id!=? ORDER BY id",
                (project, task_id),
            ).fetchall()
            conn2.close()
            if siblings:
                slines = [
                    f"- {r['id']} ({Path(r['spec_file']).stem}): {r['status']} on {r['node'] or 'unassigned'}"
                    for r in siblings
                ]
                slines.append("")
                slines.append(
                    "IMPORTANT: Do not modify files owned by other tasks. If you need a stub, create minimal placeholder."
                )
                parts.append("## Other Tasks in This Project\n" + "\n".join(slines))
        except Exception:
            pass

    # Layer 5: Environment
    env_map = {
        "mac1": "macOS M3, Python 3.11, Node 22. Local.",
        "mac2": "macOS Intel, Python 3.11, Node 22. Z.AI API.",
        "codex-node-1": "Ubuntu 24.04, Python 3.12, Node 22. Direct API.",
        "glm-node-2": "Ubuntu 24.04, Python 3.12, Node 22. Direct API.",
        "codex-local": "macOS M3, Python 3.11, Node 22. Codex API.",
    }
    parts.append(f"## Environment\n{env_map.get(node_name, 'Unknown node')}")

    # Join all parts
    context = "\n\n---\n\n".join(parts)
    return f"{context}\n\n---\n\n## Task Spec\n\n{spec_content}"


def run_ssh(ssh_host, cmd, timeout=30):
    """Execute SSH command with timeout"""
    if not ssh_host:
        return None, "No SSH host configured"

    try:
        result = subprocess.run(
            ["ssh", ssh_host, cmd], capture_output=True, text=True, timeout=timeout
        )

        if result.returncode == 0:
            return result.stdout.strip(), None
        else:
            return None, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return None, "SSH command timed out"
    except Exception as e:
        return None, str(e)


def scp_to_remote(ssh_host, local_path, remote_path, timeout=60):
    """Copy file to remote host via SCP"""
    if not ssh_host:
        return False, "No SSH host configured"

    try:
        result = subprocess.run(
            ["scp", str(local_path), f"{ssh_host}:{remote_path}"],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.returncode == 0:
            return True, None
        else:
            return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "SCP command timed out"
    except Exception as e:
        return False, str(e)


def check_remote_task_status(node, project, task_id):
    """Check task status on remote node"""
    # Read status.json
    status_cmd = f"cat ~/dispatch/{project}/tasks/{task_id}/status.json 2>/dev/null"
    status_out, status_err = run_ssh(node["ssh_host"], status_cmd)

    if status_out:
        try:
            status_data = json.loads(status_out)
            return status_data, None
        except json.JSONDecodeError:
            return None, "Invalid status JSON"

    # Read heartbeat
    heartbeat_cmd = f"cat ~/dispatch/{project}/tasks/{task_id}/heartbeat 2>/dev/null"
    heartbeat_out, heartbeat_err = run_ssh(node["ssh_host"], heartbeat_cmd)

    if heartbeat_out:
        try:
            heartbeat_time = datetime.fromisoformat(heartbeat_out.strip())
            now = datetime.now()
            if (now - heartbeat_time).total_seconds() > 120:
                # Check if process still exists
                pid_cmd = f"cat ~/dispatch/{project}/tasks/{task_id}/pid 2>/dev/null"
                pid_out, _ = run_ssh(node["ssh_host"], pid_cmd)
                if pid_out:
                    check_pid_cmd = f"ps -p {pid_out.strip()} > /dev/null && echo alive || echo dead"
                    alive_out, _ = run_ssh(node["ssh_host"], check_pid_cmd)
                    if alive_out and "dead" in alive_out:
                        return {
                            "status": "failed",
                            "error": "Process died (heartbeat timeout)",
                        }, None
        except Exception:
            pass

    return None, status_err or heartbeat_err


def validate_completed_task(node, project, task_id, db_path):
    """Validate completed task by checking syntax of Python files"""
    # Find all .py files in output directory
    find_cmd = f"find ~/dispatch/{project}/tasks/{task_id}/output/ -name '*.py' 2>/dev/null | head -20"

    # For local execution
    if node["name"] == "mac1" or node["name"] == "codex-local":
        task_dir = Path.home() / "dispatch" / project / "tasks" / task_id / "output"
        if task_dir.exists():
            py_files = list(task_dir.rglob("*.py"))[:20]
        else:
            return False  # No validation needed if no output
    else:
        files_out, files_err = run_ssh(node["ssh_host"], find_cmd)
        if not files_out:
            return False  # No Python files or no output dir
        py_files = files_out.strip().split("\n")

    failed_files = []
    for py_file in py_files:
        if not py_file.strip():
            continue

        # Validate syntax
        if node["name"] == "mac1" or node["name"] == "codex-local":
            # Local validation
            try:
                import ast

                ast.parse(open(py_file).read())
            except Exception as e:
                failed_files.append(py_file)
        else:
            # Remote validation
            validate_cmd = f'python3 -c \'import ast; ast.parse(open("{py_file}").read()); print("OK")\' 2>&1'
            validate_out, validate_err = run_ssh(node["ssh_host"], validate_cmd)
            if not validate_out or "OK" not in validate_out:
                failed_files.append(py_file)

    if failed_files:
        # Generate fix spec
        fix_spec = f"Fix syntax errors in these files: {', '.join(failed_files)}. Read each file, fix the errors, verify with ast.parse()."

        # Create fix task
        fix_task_id = f"F-{task_id}"
        with get_db(db_path) as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO tasks (id, project, spec_file, status)
                VALUES (?, ?, ?, 'pending')
            """,
                (fix_task_id, project, fix_spec),
            )
            conn.commit()

        log(f"Validation failed for {task_id}, created fix task {fix_task_id}")
        return True  # validation_failed=True

    return False  # validation_failed=False


def check_node_tasks(db_path, node, project):
    """Check all running tasks on a node"""
    with get_db(db_path) as conn:
        tasks = conn.execute(
            """
            SELECT * FROM tasks
            WHERE node = ? AND status = 'running' AND project = ?
        """,
            (node["name"], project),
        ).fetchall()

    updates = []
    for task in tasks:
        status_data, error = check_remote_task_status(node, project, task["id"])

        if status_data:
            if status_data["status"] == "completed":
                completed_at = status_data.get(
                    "completed_at", datetime.now().isoformat()
                )
                # Calculate duration, handling timezone-aware vs naive datetimes
                try:
                    end_dt = datetime.fromisoformat(
                        completed_at.replace("+00:00", "+00:00")
                    )
                    start_dt = datetime.fromisoformat(task["started_at"])
                    # Strip tzinfo from both to avoid naive/aware mismatch
                    duration = (
                        end_dt.replace(tzinfo=None) - start_dt.replace(tzinfo=None)
                    ).total_seconds()
                except (ValueError, TypeError):
                    duration = 0
                updates.append(
                    {
                        "id": task["id"],
                        "status": "completed",
                        "completed_at": completed_at,
                        "duration": duration,
                        "node": node,
                    }
                )
            elif status_data["status"] == "failed":
                updates.append(
                    {
                        "id": task["id"],
                        "status": "failed",
                        "completed_at": datetime.now().isoformat(),
                        "error": status_data.get("error", "Unknown error"),
                    }
                )
        elif error:
            log(
                f"Warning: Could not check task {task['id']} on {node['name']}: {error}"
            )

    return updates


def apply_task_updates(db_path, updates, project):
    """Apply task status updates to database"""
    if not updates:
        return

    # Run validations before opening DB connection to avoid nested locks
    validation_results = {}
    for update in updates:
        if update["status"] == "completed" and "node" in update:
            validation_failed = validate_completed_task(
                update["node"], project, update["id"], db_path
            )
            if validation_failed:
                log(f"Task {update['id']} validation failed, created fix task")
                validation_results[update["id"]] = True

    with get_db(db_path) as conn:
        for update in updates:
            if update["status"] == "completed":
                conn.execute(
                    """
                    UPDATE tasks
                    SET status = ?, completed_at = ?, duration_seconds = ?
                    WHERE id = ?
                """,
                    (
                        update["status"],
                        update["completed_at"],
                        update["duration"],
                        update["id"],
                    ),
                )
                release_file_locks(db_path, update["id"], conn=conn)
            elif update["status"] == "failed":
                conn.execute(
                    """
                    UPDATE tasks
                    SET status = ?, completed_at = ?, error = ?
                    WHERE id = ?
                """,
                    (
                        update["status"],
                        update["completed_at"],
                        update["error"],
                        update["id"],
                    ),
                )
                release_file_locks(db_path, update["id"], conn=conn)

            # Log event in same connection to avoid DB lock
            conn.execute(
                """
                INSERT INTO events (timestamp, task_id, event_type, node, details)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    datetime.now().isoformat(),
                    update["id"],
                    f"task_{update['status']}",
                    None,
                    json.dumps({k: v for k, v in update.items() if k != "node"}),
                ),
            )

        conn.commit()


def update_node_running_counts(db_path):
    """Update running_count for all nodes"""
    with get_db(db_path) as conn:
        # Reset all counts
        conn.execute("UPDATE nodes SET running_count = 0")

        # Count running tasks per node
        counts = conn.execute("""
            SELECT node, COUNT(*) as count
            FROM tasks
            WHERE status = 'running'
            GROUP BY node
        """).fetchall()

        for row in counts:
            conn.execute(
                """
                UPDATE nodes SET running_count = ? WHERE name = ?
            """,
                (row["count"], row["node"]),
            )

        conn.commit()


def deploy_task_to_node(db_path, node, project, task):
    """Deploy a task to a node"""
    task_id = task["id"]
    spec_file = task["spec_file"]

    # Read original spec content
    with open(spec_file, "r") as f:
        spec_content = f.read()

    # Build enriched spec
    enriched_spec = build_enriched_spec(
        project, task_id, spec_content, node["name"], db_path
    )

    # Handle local execution for mac1 and codex-local
    if node["name"] == "mac1" or node["name"] == "codex-local":
        # Create local directory
        task_dir = Path.home() / "dispatch" / project / "tasks" / task_id
        task_dir.mkdir(parents=True, exist_ok=True)

        # Write enriched spec
        spec_path = task_dir / "spec.md"
        with open(spec_path, "w") as f:
            f.write(enriched_spec)

        # Determine executor based on task type
        task_type = get_task_type(task_id)
        executor = get_executor(task_type)

        # Build command based on executor
        if executor == "codex":
            cmd = [
                "codex",
                "exec",
                "--skip-git-repo-check",
                "--full-auto",
                enriched_spec,
                "--json",
            ]
        else:
            # Use OpenCode with MiniMax (free)
            cmd = [
                "~/.opencode/bin/opencode",
                "run",
                "--model",
                "opencode/minimax-m2.5-free",
                "--",
                enriched_spec,
            ]

        # Start process
        log_path = task_dir / "output.log"
        pid_path = task_dir / "pid"
        status_path = task_dir / "status.json"

        with open(log_path, "w") as log_file:
            proc = subprocess.Popen(
                cmd,
                cwd=str(task_dir),
                stdout=log_file,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )

        # Write PID
        with open(pid_path, "w") as f:
            f.write(str(proc.pid))

        # Write initial status
        with open(status_path, "w") as f:
            f.write(
                json.dumps(
                    {"status": "running", "started_at": datetime.now().isoformat()}
                )
            )

        # Update database
        with get_db(db_path) as conn:
            conn.execute(
                """
                UPDATE tasks
                SET status = 'running', node = ?, started_at = ?, pid = ?
                WHERE id = ?
            """,
                (node["name"], datetime.now().isoformat(), proc.pid, task_id),
            )
            conn.commit()

        log_event(
            db_path,
            task_id,
            "task_started",
            node["name"],
            json.dumps({"pid": proc.pid, "executor": executor}),
        )
        log(f"Started task {task_id} on {node['name']} (local, executor={executor})")

        return True

    # Remote execution

    # ====== P0 FIX: RSYNC CODE WITH RETRY ======
    # Check if project code exists on remote, if not, rsync
    project_local_path = Path.home() / "Downloads" / project
    project_remote_path = f"~/dispatch/{project}"

    # Check if remote project exists
    check_remote_cmd = f"test -d {project_remote_path} && echo exists || echo missing"
    remote_status, _ = run_ssh(node["ssh_host"], check_remote_cmd)

    if "missing" in str(remote_status) or remote_status == "":
        log(f"Syncing {project} code to {node['name']}...")

        # Retry rsync up to 3 times
        max_retries = 3
        rsync_success = False

        for attempt in range(1, max_retries + 1):
            log(f"Rsync attempt {attempt}/{max_retries}...")

            # First delete remote dir if exists (to avoid partial sync)
            run_ssh(node["ssh_host"], f"rm -rf {project_remote_path}")

            # Rsync project to node
            rsync_cmd = [
                "rsync",
                "-az",
                "--delete",
                "--exclude",
                ".git",
                "--exclude",
                "node_modules",
                "--exclude",
                "__pycache__",
                "--exclude",
                ".venv",
                "--exclude",
                "*.pyc",
                f"{project_local_path}/",
                f"{node['ssh_host']}:{project_remote_path}",
            ]
            rsync_result = subprocess.run(
                rsync_cmd, capture_output=True, text=True, timeout=600
            )

            if rsync_result.returncode == 0:
                log(f"Code synced to {node['name']}")
                rsync_success = True
                break
            else:
                log(f"Rsync attempt {attempt} failed: {rsync_result.stderr[:100]}")
                if attempt < max_retries:
                    time.sleep(5)  # Wait before retry

        if not rsync_success:
            log(f"ERROR: Rsync failed after {max_retries} attempts - task may fail")
    # ====== END RSYNC FIX ======

    # Create remote directory
    mkdir_cmd = f"mkdir -p ~/dispatch/{project}/tasks/{task_id}"
    _, err = run_ssh(node["ssh_host"], mkdir_cmd)
    if err:
        log(f"ERROR: Failed to create remote directory: {err}")
        return False

    # Check sync mode for git support
    project_config = load_project_config(project)
    sync_mode = project_config.get("sync_mode", "scp")

    repo_url = ""
    git_branch = ""

    if sync_mode == "git":
        repo_url = project_config["repo_url"]
        main_branch = project_config.get("main_branch", "main")
        git_branch = f"task/{project}-{task_id}-{node['name']}"

        # Create remote branch from main
        local_repo = Path(project_config["repo_local"]).expanduser()
        if local_repo.exists():
            subprocess.run(
                ["git", "fetch", "origin"],
                cwd=str(local_repo),
                capture_output=True,
                timeout=30,
            )
            subprocess.run(
                ["git", "push", "origin", f"{main_branch}:refs/heads/{git_branch}"],
                cwd=str(local_repo),
                capture_output=True,
                timeout=30,
            )
            log(f"Created branch {git_branch} on origin")

        # Clone on remote node
        clone_cmd = f"git clone --depth=1 --branch {git_branch} --single-branch {repo_url} ~/dispatch/{project}/tasks/{task_id}/repo 2>&1 | tail -3"
        clone_out, clone_err = run_ssh(node["ssh_host"], clone_cmd)
        if clone_err:
            log(f"Warning: git clone issue: {clone_err}")

    # Write enriched spec to temporary file
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tmp:
        tmp.write(enriched_spec)
        tmp_path = tmp.name

    try:
        # SCP enriched spec file
        remote_spec = f"~/dispatch/{project}/tasks/{task_id}/spec.md"
        ok, err = scp_to_remote(node["ssh_host"], tmp_path, remote_spec)
        if not ok:
            log(f"ERROR: SCP failed for {task_id}: {err}")
            return False
    finally:
        # Clean up temp file
        Path(tmp_path).unlink()

    # Deploy task-wrapper.sh if not exists
    wrapper_local = Path(__file__).parent / "task-wrapper.sh"
    if not wrapper_local.exists():
        create_task_wrapper(wrapper_local)

    # Check if wrapper exists remotely
    check_wrapper_cmd = (
        f"test -f ~/dispatch/task-wrapper.sh && echo exists || echo missing"
    )
    wrapper_status, _ = run_ssh(node["ssh_host"], check_wrapper_cmd)

    if not wrapper_status or "missing" in wrapper_status:
        remote_wrapper = f"~/dispatch/task-wrapper.sh"
        ok, err = scp_to_remote(node["ssh_host"], str(wrapper_local), remote_wrapper)
        if not ok:
            log(f"Warning: Could not deploy wrapper: {err}")

    # Start task remotely
    remote_spec_path = f"~/dispatch/{project}/tasks/{task_id}/spec.md"
    remote_status_path = f"~/dispatch/{project}/tasks/{task_id}/status.json"
    api_mode = node.get("api_mode", "direct")

    # Write initial status.json (for hybrid mode / task-watcher)
    status_json = json.dumps(
        {
            "status": "pending",
            "task_id": task_id,
            "project": project,
            "node": node["name"],
            "created_at": datetime.now().isoformat(),
        }
    )

    # Create temp status file
    import tempfile

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as tmp_status:
        tmp_status.write(status_json)
        tmp_status_path = tmp_status.name

    try:
        # SCP status.json first
        ok, err = scp_to_remote(node["ssh_host"], tmp_status_path, remote_status_path)
        if not ok:
            log(f"Warning: SCP status failed for {task_id}: {err}")
    finally:
        Path(tmp_status_path).unlink()

    # Check if task-watcher is running on node (hybrid mode)
    check_watcher_cmd = "pgrep -f '[t]ask-watcher.py' || echo not_running"
    watcher_status, _ = run_ssh(node["ssh_host"], check_watcher_cmd)

    if watcher_status and "not_running" not in watcher_status:
        # Hybrid mode: task-watcher will pick up the task
        log(f"Hybrid mode: task-watcher will execute {task_id} on {node['name']}")
        # Just update DB as pending, watcher will update later
        with get_db(db_path) as conn:
            conn.execute(
                "UPDATE tasks SET status = 'running', node = ?, started_at = ? WHERE id = ?",
                (node["name"], datetime.now().isoformat(), task_id),
            )
            conn.commit()
        return True

    # Original mode: SSH start wrapper directly
    if sync_mode == "git":
        start_cmd = f"API_MODE={api_mode} nohup bash ~/dispatch/task-wrapper.sh {project} {task_id} {remote_spec_path} {repo_url} {git_branch} > ~/dispatch/{project}/tasks/{task_id}/wrapper.log 2>&1 & echo $!"
    else:
        start_cmd = f"API_MODE={api_mode} nohup bash ~/dispatch/task-wrapper.sh {project} {task_id} {remote_spec_path} > ~/dispatch/{project}/tasks/{task_id}/wrapper.log 2>&1 & echo $!"
    pid_out, err = run_ssh(node["ssh_host"], start_cmd)

    if err:
        log(f"ERROR: Failed to start task {task_id}: {err}")
        return False

    # Update database
    with get_db(db_path) as conn:
        conn.execute(
            """
            UPDATE tasks
            SET status = 'running', node = ?, started_at = ?, pid = ?
            WHERE id = ?
        """,
            (
                node["name"],
                datetime.now().isoformat(),
                pid_out.strip() if pid_out else None,
                task_id,
            ),
        )
        conn.commit()

    log_event(
        db_path,
        task_id,
        "task_started",
        node["name"],
        json.dumps({"pid": pid_out.strip() if pid_out else None}),
    )
    log(f"Started task {task_id} on {node['name']}")

    return True


def create_task_wrapper(wrapper_path):
    """Create task-wrapper.sh script"""
    wrapper_content = """#!/bin/bash
# Task wrapper script
TASK_ID=$1
PROJECT=$2
API_MODE=$3

TASK_DIR=~/dispatch/$PROJECT/tasks/$TASK_ID
cd $TASK_DIR

echo $$ > pid
echo "$(date -Iseconds)" > heartbeat

# Write initial status
cat > status.json <<EOF
{"status": "running", "started_at": "$(date -Iseconds)"}
EOF

# Determine claude command
if [ "$API_MODE" = "zai" ]; then
    CLAUDE_CMD="claude-glm"
else
    CLAUDE_CMD="claude"
fi

# Run task
$CLAUDE_CMD -p "$(cat spec.md)" --dangerously-skip-permissions > output.log 2>&1
EXIT_CODE=$?

# Update heartbeat periodically in background (disabled for now - task should be quick)
# while kill -0 $$ 2>/dev/null; do
#     echo "$(date -Iseconds)" > heartbeat
#     sleep 30
# done &

# Write completion status
if [ $EXIT_CODE -eq 0 ]; then
    cat > status.json <<EOF
{"status": "completed", "completed_at": "$(date -Iseconds)", "exit_code": $EXIT_CODE}
EOF
else
    cat > status.json <<EOF
{"status": "failed", "completed_at": "$(date -Iseconds)", "exit_code": $EXIT_CODE, "error": "Task exited with code $EXIT_CODE"}
EOF
fi
"""

    with open(wrapper_path, "w") as f:
        f.write(wrapper_content)
    os.chmod(wrapper_path, 0o755)


def detect_circular_dependencies(db_path, project):
    """Detect circular dependencies in task DAG"""
    with get_db(db_path) as conn:
        tasks = conn.execute(
            "SELECT id, depends_on FROM tasks WHERE project=?", (project,)
        ).fetchall()

    # Build adjacency list
    graph = {}
    for task in tasks:
        task_id = task["id"]
        deps = json.loads(task["depends_on"] or "[]")
        graph[task_id] = deps

    # DFS cycle detection
    visited = set()
    in_stack = set()
    cycles = []

    def dfs(node, path):
        if node in in_stack:
            cycle_start = path.index(node)
            cycles.append(path[cycle_start:])
            return
        if node in visited:
            return
        visited.add(node)
        in_stack.add(node)
        path.append(node)
        for dep in graph.get(node, []):
            dfs(dep, path[:])
        in_stack.discard(node)

    for task_id in graph:
        if task_id not in visited:
            dfs(task_id, [])

    if cycles:
        log(f"WARNING: Circular dependencies detected: {cycles}")
    return cycles


def schedule_tasks(db_path, project):
    """Schedule pending tasks to available nodes"""
    # Get enabled nodes with available slots
    with get_db(db_path) as conn:
        nodes = [
            dict(r)
            for r in conn.execute("""
            SELECT * FROM nodes
            WHERE enabled = 1 AND (slots - running_count) > 0
            ORDER BY COALESCE(priority, 2) ASC, (slots - running_count) DESC
        """).fetchall()
        ]

        pending_tasks = [
            dict(r)
            for r in conn.execute(
                """
            SELECT * FROM tasks
            WHERE status = 'pending' AND project = ?
            ORDER BY priority ASC, id ASC
        """,
                (project,),
            ).fetchall()
        ]

    if not pending_tasks:
        return 0

    scheduled = 0
    for task in pending_tasks:
        if not nodes:
            break

        # DAG: Check dependencies are satisfied
        depends_on = json.loads(task.get("depends_on", "[]"))
        if depends_on:
            with get_db(db_path) as conn:
                dep_statuses = conn.execute(
                    f"SELECT id, status FROM tasks WHERE id IN ({','.join('?' * len(depends_on))})",
                    depends_on,
                ).fetchall()
                all_done = all(d["status"] == "completed" for d in dep_statuses)
                if not all_done:
                    # Don't auto-fail on ghost/timeout - allow retry
                    continue  # Skip - dependencies not met

        # DAG: Check file conflicts (Best Practice: 所有任务都检查 modifies 冲突)
        modifies = json.loads(task.get("modifies", "[]"))
        if modifies:
            conflicts = check_file_conflicts(db_path, modifies)
            if conflicts:
                # 有冲突，记录日志但继续检查其他任务
                log(
                    f"Task {task['id']} has file conflicts with: {conflicts}, checking if any are running..."
                )
                # 检查是否有正在运行的冲突任务
                running_conflicts = []
                conflict_task_ids = []
                for c in conflicts:
                    if isinstance(c, dict):
                        task_id = c.get("task_id")
                        if task_id:
                            conflict_task_ids.append(task_id)
                    elif isinstance(c, (tuple, list)) and len(c) >= 2:
                        conflict_task_ids.append(c[1])

                if conflict_task_ids:
                    with get_db(db_path) as conn3:
                        placeholders = ",".join("?" * len(conflict_task_ids))
                        rows = conn3.execute(
                            f"SELECT id, status FROM tasks WHERE id IN ({placeholders})",
                            conflict_task_ids,
                        ).fetchall()
                        running_ids = {
                            r["id"] for r in rows if r["status"] == "running"
                        }

                    for c in conflicts:
                        if isinstance(c, dict):
                            if c.get("task_id") in running_ids:
                                running_conflicts.append(c)
                        elif isinstance(c, (tuple, list)) and len(c) >= 2:
                            if c[1] in running_ids:
                                running_conflicts.append(c)

                if running_conflicts:
                    continue  # Skip - files are locked by a running task

        # Determine task type and required executor
        task_type = get_task_type(task["id"])
        required_executor = get_executor(task_type)

        # Filter nodes by executor type
        compatible_nodes = [
            n for n in nodes if n.get("executor", "glm") == required_executor
        ]

        # If no codex nodes available and task requires codex, fallback to GLM
        if not compatible_nodes and required_executor == "codex":
            log(
                f"Warning: Task {task['id']} requires codex but no codex nodes available, falling back to GLM"
            )
            compatible_nodes = [n for n in nodes if n.get("executor", "glm") == "glm"]

        if not compatible_nodes:
            continue

        # Find best node: lowest priority number first, then most available slots
        best_node = None
        best_priority = 999
        max_available = 0

        for node in compatible_nodes:
            available = node["slots"] - node["running_count"]
            node_priority = int(node.get("priority", 2))
            if node_priority < best_priority or (
                node_priority == best_priority and available > max_available
            ):
                best_priority = node_priority
                max_available = available
                best_node = node

        if best_node and max_available > 0:
            if deploy_task_to_node(db_path, dict(best_node), project, dict(task)):
                scheduled += 1
                # Acquire file locks if task has exclusive files
                modifies = json.loads(task.get("modifies", "[]"))
                if modifies and task.get("exclusive", 0):
                    acquire_file_locks(db_path, task["id"], modifies)
                # Update running count locally to prevent over-scheduling
                with get_db(db_path) as conn:
                    conn.execute(
                        """
                        UPDATE nodes SET running_count = running_count + 1
                        WHERE name = ?
                    """,
                        (best_node["name"],),
                    )
                    conn.commit()

                # Refresh nodes list
                with get_db(db_path) as conn:
                    nodes = [
                        dict(r)
                        for r in conn.execute("""
                        SELECT * FROM nodes
                        WHERE enabled = 1 AND (slots - running_count) > 0
                        ORDER BY COALESCE(priority, 2) ASC, (slots - running_count) DESC
                    """).fetchall()
                    ]

    return scheduled


def check_all_nodes(db_path, project):
    """Check status of all nodes in parallel"""
    with get_db(db_path) as conn:
        nodes = conn.execute("SELECT * FROM nodes WHERE enabled = 1").fetchall()

    all_updates = []

    with ThreadPoolExecutor(max_workers=len(nodes)) as executor:
        future_to_node = {
            executor.submit(check_node_tasks, db_path, dict(node), project): node
            for node in nodes
        }

        for future in as_completed(future_to_node):
            node = future_to_node[future]
            try:
                updates = future.result()
                all_updates.extend(updates)
            except Exception as e:
                log(f"Error checking node {node['name']}: {e}")

    if all_updates:
        apply_task_updates(db_path, all_updates, project)

    update_node_running_counts(db_path)


def refresh_stuck_tasks(db_path, project, timeout_minutes=15):
    """Auto-refresh tasks that are stuck (running too long without status update)"""
    with get_db(db_path) as conn:
        # Find tasks running longer than timeout
        stuck_tasks = conn.execute(
            """
            SELECT id, node, started_at FROM tasks
            WHERE project = ? AND status = 'running'
            AND started_at < datetime('now', '-' || ? || ' minutes')
        """,
            (project, timeout_minutes),
        ).fetchall()

        refreshed = 0
        for task in stuck_tasks:
            task_id = task["id"]
            node_name = task["node"]

            # Check if task process is still alive on remote
            if node_name:
                # Try to get status.json from remote
                status_cmd = (
                    f"cat ~/dispatch/{project}/tasks/{task_id}/status.json 2>/dev/null"
                )
                status_out, _ = run_ssh(
                    next(
                        (
                            n["ssh_host"]
                            for n in load_nodes_config(
                                Path.home() / "Downloads" / "dispatch" / "nodes.json"
                            )
                            if n["name"] == node_name
                        ),
                        None,
                    ),
                    status_cmd,
                )

                if status_out:
                    try:
                        status_data = json.loads(status_out)
                        # If status is still running but task is old, check heartbeat
                        if status_data.get("status") == "running":
                            heartbeat_cmd = f"cat ~/dispatch/{project}/tasks/{task_id}/heartbeat 2>/dev/null"
                            heartbeat_out, _ = run_ssh(
                                next(
                                    (
                                        n["ssh_host"]
                                        for n in load_nodes_config(
                                            Path.home()
                                            / "Downloads"
                                            / "dispatch"
                                            / "nodes.json"
                                        )
                                        if n["name"] == node_name
                                    ),
                                    None,
                                ),
                                heartbeat_cmd,
                            )
                            if heartbeat_out:
                                try:
                                    heartbeat_time = datetime.fromisoformat(
                                        heartbeat_out.strip()
                                    )
                                    if (
                                        datetime.now() - heartbeat_time
                                    ).total_seconds() > 300:  # 5 min no heartbeat
                                        # Force mark as failed to allow retry
                                        conn.execute(
                                            "UPDATE tasks SET status='pending', error='timeout_refreshed' WHERE id=?",
                                            (task_id,),
                                        )
                                        refreshed += 1
                                        log(
                                            f"Refreshed stuck task: {task_id} on {node_name}"
                                        )
                                except:
                                    pass
                    except:
                        pass

        if refreshed > 0:
            conn.commit()

        return refreshed


def check_completion(db_path, project):
    """Check if all tasks are completed"""
    with get_db(db_path) as conn:
        result = conn.execute(
            """
            SELECT COUNT(*) as count FROM tasks
            WHERE project = ? AND status IN ('pending', 'running')
        """,
            (project,),
        ).fetchone()

        return result["count"] == 0


def cmd_start(args):
    """Start command: initialize and run scheduler"""
    project = args.project
    daemon_mode = getattr(args, "daemon", False)

    # If daemon mode, fork to background
    if daemon_mode:
        log("Starting dispatch in daemon mode...")

        # Fork process
        pid = os.fork()
        if pid > 0:
            # Parent exits
            print(f"Dispatch started in background (PID: {pid})")
            sys.exit(0)

        # Child continues
        # Close stdin/stdout/stderr
        sys.stdin.close()
        sys.stdout.close()
        sys.stderr.close()

        # Become session leader
        os.setsid()

        # Write PID file
        dispatch_dir = Path.home() / "Downloads" / "dispatch"
        pid_file = dispatch_dir / f"{project}.pid"
        with open(pid_file, "w") as f:
            f.write(str(os.getpid()))

    dispatch_dir = Path.home() / "Downloads" / "dispatch"
    project_config = load_project_config(project)
    specs_dir = Path(
        project_config.get("specs_dir", str(Path.home() / "Downloads" / "specs"))
    ).expanduser()
    db_path = dispatch_dir / "dispatch.db"
    pid_file = dispatch_dir / f"{project}.pid"
    stop_file = dispatch_dir / f"{project}.stop"
    nodes_file = dispatch_dir / "nodes.json"

    # Check if already running
    if pid_file.exists():
        with open(pid_file, "r") as f:
            old_pid = f.read().strip()
        log(f"Warning: PID file exists ({old_pid}). Check if already running.")

    # Remove stop file if exists
    if stop_file.exists():
        stop_file.unlink()

    # Initialize database
    log("Initializing database...")
    init_database(db_path)

    # Load nodes
    log("Loading nodes configuration...")
    nodes = load_nodes_config(nodes_file)
    init_nodes(db_path, nodes)

    # Scan specs
    log(f"Scanning specs for project: {project}")
    tasks = scan_specs(project, specs_dir)
    if not tasks:
        log("No tasks found. Exiting.")
        return

    init_tasks(db_path, tasks)

    # Check for circular dependencies
    cycles = detect_circular_dependencies(db_path, project)
    if cycles:
        log(f"ERROR: Circular dependencies found: {cycles}")
        log("Fix spec dependencies before running. Aborting.")
        return

    # Write PID file
    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))

    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    log(f"Starting scheduler for project: {project}")
    log(f"Press Ctrl+C to stop gracefully")

    cycle = 0
    try:
        while RUNNING:
            cycle += 1
            log(f"=== Cycle {cycle} ===")

            # Check for stop file
            if stop_file.exists():
                log("Stop file detected. Exiting...")
                break

            # Check all running tasks
            log("Checking node status...")
            check_all_nodes(db_path, project)

            # Auto-refresh stuck tasks (every 3 cycles)
            if cycle % 3 == 0:
                refreshed = refresh_stuck_tasks(db_path, project, timeout_minutes=15)
                if refreshed > 0:
                    log(f"Refreshed {refreshed} stuck tasks")

            # Schedule new tasks
            log("Scheduling pending tasks...")
            scheduled = schedule_tasks(db_path, project)
            if scheduled > 0:
                log(f"Scheduled {scheduled} new tasks")

            # Check if all done
            if check_completion(db_path, project):
                log("All tasks completed!")

                # Auto-collect git branches if in git mode
                project_config = load_project_config(project)
                if project_config.get("sync_mode") == "git":
                    log("Auto-collecting git branches...")
                    collect_git(db_path, project)

                log("Generating report...")
                args.project = project
                cmd_report(args)
                break

            # Sleep
            log("Sleeping 30 seconds...")
            for _ in range(30):
                if not RUNNING:
                    break
                time.sleep(1)

    finally:
        # Cleanup
        if pid_file.exists():
            pid_file.unlink()
        log("Scheduler stopped")


def cmd_status(args):
    """Status command: show current state"""
    dispatch_dir = Path.home() / "Downloads" / "dispatch"
    db_path = dispatch_dir / "dispatch.db"

    if not db_path.exists():
        log("Database not found. Run 'start' first.")
        return

    project = args.project

    with get_db(db_path) as conn:
        # Task counts by status
        if project:
            status_counts = conn.execute(
                """
                SELECT status, COUNT(*) as count
                FROM tasks
                WHERE project = ?
                GROUP BY status
            """,
                (project,),
            ).fetchall()
        else:
            status_counts = conn.execute("""
                SELECT status, COUNT(*) as count
                FROM tasks
                GROUP BY status
            """).fetchall()

        print("\n=== Task Status ===")
        for row in status_counts:
            print(f"  {row['status']}: {row['count']}")

        # Node status
        nodes = conn.execute("SELECT * FROM nodes").fetchall()
        print("\n=== Node Status ===")
        for node in nodes:
            enabled = "✓" if node["enabled"] else "✗"
            print(
                f"  {node['name']}: {node['running_count']}/{node['slots']} slots used [{enabled}]"
            )

        # Running tasks
        if project:
            running = conn.execute(
                """
                SELECT * FROM tasks
                WHERE status = 'running' AND project = ?
                ORDER BY started_at
            """,
                (project,),
            ).fetchall()
        else:
            running = conn.execute("""
                SELECT * FROM tasks
                WHERE status = 'running'
                ORDER BY started_at
            """).fetchall()

        if running:
            print("\n=== Running Tasks ===")
            for task in running:
                started = task["started_at"]
                if started:
                    started_dt = datetime.fromisoformat(started)
                    duration = (datetime.now() - started_dt).total_seconds()
                    print(f"  {task['id']} on {task['node']} (running {duration:.0f}s)")


def cmd_report(args):
    """Report command: generate completion report"""
    project = args.project
    dispatch_dir = Path.home() / "Downloads" / "dispatch"
    db_path = dispatch_dir / "dispatch.db"
    report_file = dispatch_dir / f"{project}-report.md"

    if not db_path.exists():
        log("Database not found.")
        return

    with get_db(db_path) as conn:
        tasks = conn.execute(
            """
            SELECT * FROM tasks
            WHERE project = ?
            ORDER BY id
        """,
            (project,),
        ).fetchall()

        completed = sum(1 for t in tasks if t["status"] == "completed")
        failed = sum(1 for t in tasks if t["status"] == "failed")
        total = len(tasks)

    # Generate report
    report = [
        f"# Dispatch Report: {project}",
        f"Generated: {datetime.now().isoformat()}",
        "",
        f"## Summary",
        f"- Total tasks: {total}",
        f"- Completed: {completed}",
        f"- Failed: {failed}",
        f"- Success rate: {completed / total * 100:.1f}%" if total > 0 else "N/A",
        "",
        f"## Task Details",
        "",
    ]

    for task in tasks:
        report.append(f"### {task['id']}")
        report.append(f"- Status: {task['status']}")
        report.append(f"- Node: {task['node'] or 'N/A'}")

        if task["duration_seconds"]:
            report.append(f"- Duration: {task['duration_seconds']:.1f}s")

        if task["error"]:
            report.append(f"- Error: {task['error']}")

        report.append("")

    # Failed tasks
    failed_tasks = [t for t in tasks if t["status"] == "failed"]
    if failed_tasks:
        report.append("## Failed Tasks")
        report.append("")
        for task in failed_tasks:
            report.append(f"### {task['id']}")
            report.append(f"- Node: {task['node']}")
            report.append(f"- Error: {task['error']}")
            report.append("")

    with open(report_file, "w") as f:
        f.write("\n".join(report))

    log(f"Report written to: {report_file}")


def cmd_stop(args):
    """Stop command: write stop flag"""
    project = args.project
    dispatch_dir = Path.home() / "Downloads" / "dispatch"
    stop_file = dispatch_dir / f"{project}.stop"

    with open(stop_file, "w") as f:
        f.write(datetime.now().isoformat())

    log(f"Stop flag written for project: {project}")


def cmd_cleanup(args):
    """Cleanup command: remove remote task directories for collected tasks older than threshold"""
    project = args.project
    older_than_hours = args.older_than
    force_all = args.all
    dispatch_dir = Path.home() / "Downloads" / "dispatch"
    db_path = str(dispatch_dir / "dispatch.db")
    nodes_file = dispatch_dir / "nodes.json"

    if not Path(db_path).exists():
        log("Database not found.")
        return

    nodes = load_nodes_config(nodes_file)
    node_map = {n["name"]: n for n in nodes if n["name"] != "mac1"}

    if force_all:
        # Legacy behavior: nuke entire project dir on all nodes
        for node in node_map.values():
            log(f"Cleaning up {node['name']} (all)...")
            cleanup_cmd = f"rm -rf ~/dispatch/{project}"
            _, err = run_ssh(node["ssh_host"], cleanup_cmd)
            log(f"  {'Warning: ' + err if err else 'Cleaned'}")
        return

    # Time-based cleanup: only collected tasks older than threshold
    cutoff = (datetime.now() - timedelta(hours=older_than_hours)).isoformat()
    with get_db(db_path) as conn:
        tasks = conn.execute(
            "SELECT id, node FROM tasks WHERE project=? AND collected_at IS NOT NULL AND collected_at < ?",
            (project, cutoff),
        ).fetchall()

    if not tasks:
        log(f"No collected tasks older than {older_than_hours}h to clean up.")
        return

    cleaned = 0
    for task in tasks:
        task_id = task["id"] if isinstance(task, dict) else task[0]
        task_node = task["node"] if isinstance(task, dict) else task[1]
        node = node_map.get(task_node)
        if not node:
            continue

        task_dir = f"~/dispatch/{project}/{task_id}"
        log(f"  Removing {task_node}:{task_dir}...")
        _, err = run_ssh(node["ssh_host"], f"rm -rf {task_dir}")
        if err:
            log(f"    Warning: {err}")
        else:
            cleaned += 1

    log(
        f"Cleaned {cleaned}/{len(tasks)} task directories (older than {older_than_hours}h)."
    )


def cmd_collect(args):
    """Collect and merge completed task branches"""
    project = args.project
    db_path = str(Path(__file__).parent / "dispatch.db")

    if not Path(db_path).exists():
        log("ERROR: No database found. Run 'start' first.")
        return

    # Check sync mode
    project_config = load_project_config(project)
    sync_mode = project_config.get("sync_mode", "scp")

    if sync_mode == "git":
        report = collect_git(db_path, project)
        if report:
            log(f"Merge report:")
            for entry in report:
                status_icon = (
                    "✓"
                    if entry["status"] == "merged"
                    else "✗"
                    if entry["status"] == "conflict"
                    else "?"
                )
                log(f"  {status_icon} {entry['task']}: {entry['status']}")
    else:
        # SCP mode: collect output files from nodes
        collected = collect_scp_outputs(db_path, project)
        if collected:
            log(f"Collected {len(collected)} tasks")


def cmd_validate(args):
    """Collect + Build + Test"""
    project = args.project
    db_path = str(Path(__file__).parent / "dispatch.db")

    if not Path(db_path).exists():
        log("ERROR: No database found. Run 'start' first.")
        return

    log("Starting collect + validate...")
    result = collect_and_validate(db_path, project)

    log(f"=== Validation Results ===")
    log(f"Collected: {result['collected']}")
    log(f"Validated: {result['validated']}")
    log(f"Passed: {result['passed']}")
    log(f"Failed: {result['failed']}")

    for r in result.get("results", []):
        status = "✓" if r["overall"] else "✗"
        log(
            f"  {status} {r['task_id']}: {r['project_type']} build={r['build']['success']} test={r['test']['success']}"
        )


# ============ Pull Mode Commands ============


def cmd_poll(args):
    """Get pending tasks (for pull mode)"""
    db_path = Path.home() / "Downloads" / "dispatch" / "dispatch.db"

    with get_db(db_path) as conn:
        tasks = conn.execute(
            """
            SELECT id, project, spec_file, priority, depends_on, modifies, exclusive
            FROM tasks
            WHERE status = 'pending' AND project = ?
            ORDER BY priority ASC, id ASC
            LIMIT ?
        """,
            (args.project, args.limit),
        ).fetchall()

        if not tasks:
            print("[]")
            return

        results = []
        for task in tasks:
            # Check dependencies
            depends_on = json.loads(task["depends_on"] or "[]")
            if depends_on:
                dep_statuses = conn.execute(
                    f"SELECT id, status FROM tasks WHERE id IN ({','.join('?' * len(depends_on))})",
                    depends_on,
                ).fetchall()
                if not all(d["status"] == "completed" for d in dep_statuses):
                    continue  # Skip - dependencies not met

            results.append(
                {
                    "id": task["id"],
                    "project": task["project"],
                    "spec_file": task["spec_file"],
                    "priority": task["priority"],
                    "depends_on": depends_on,
                    "modifies": json.loads(task["modifies"] or "[]"),
                    "exclusive": task["exclusive"],
                }
            )

        print(json.dumps(results, indent=2))


def cmd_claim(args):
    """Claim a task for execution"""
    db_path = Path.home() / "Downloads" / "dispatch" / "dispatch.db"
    task_id = args.task_id

    with get_db(db_path) as conn:
        # Check if task exists and is pending
        task = conn.execute(
            "SELECT id, status FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()

        if not task:
            print(json.dumps({"error": "Task not found"}))
            return

        if task["status"] != "pending":
            print(
                json.dumps({"error": f"Task status is {task['status']}, not pending"})
            )
            return

        # Try to claim (atomic update)
        conn.execute(
            "UPDATE tasks SET status = 'claimed' WHERE id = ? AND status = 'pending'",
            (task_id,),
        )
        conn.commit()

        # Check if claim succeeded
        updated = conn.execute(
            "SELECT status FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()

        if updated["status"] == "claimed":
            print(json.dumps({"status": "claimed", "task_id": task_id}))
        else:
            print(json.dumps({"error": "Failed to claim - another node got it"}))


def cmd_finish(args):
    """Mark task as completed or failed"""
    db_path = Path.home() / "Downloads" / "dispatch" / "dispatch.db"
    task_id = args.task_id
    status = args.status
    error = args.error

    with get_db(db_path) as conn:
        if status == "completed":
            conn.execute(
                "UPDATE tasks SET status = 'completed', completed_at = ? WHERE id = ?",
                (datetime.now().isoformat(), task_id),
            )
        else:
            conn.execute(
                "UPDATE tasks SET status = 'failed', completed_at = ?, error = ? WHERE id = ?",
                (datetime.now().isoformat(), error or "Unknown error", task_id),
            )
        conn.commit()

        print(json.dumps({"status": status, "task_id": task_id}))


def cmd_heartbeat(args):
    """Send heartbeat for a task"""
    db_path = Path.home() / "Downloads" / "dispatch" / "dispatch.db"
    task_id = args.task_id

    with get_db(db_path) as conn:
        conn.execute(
            "UPDATE tasks SET heartbeat_at = ? WHERE id = ?",
            (datetime.now().isoformat(), task_id),
        )
        conn.commit()

        print(json.dumps({"status": "ok", "task_id": task_id}))


def cmd_memory(args):
    """Memory store commands"""
    import sys

    sys.path.insert(0, str(Path(__file__).parent))
    from memory_store import MemoryStore

    store = MemoryStore()

    if args.memory_action == "search":
        query = args.query
        limit = args.limit
        mem_type = args.type

        results = store.search(query, memory_type=mem_type, limit=limit)
        print(
            json.dumps(
                {"query": query, "count": len(results), "results": results}, indent=2
            )
        )

    elif args.memory_action == "stats":
        stats = store.get_stats()
        print(json.dumps(stats, indent=2))

    elif args.memory_action == "add":
        store.add(args.content, args.type or "task")
        print(json.dumps({"status": "ok", "added": args.content[:50]}))

    elif args.memory_action == "clear":
        count = store.clear(args.type)
        print(json.dumps({"status": "ok", "cleared": count}))


def main():
    parser = argparse.ArgumentParser(description="Distributed Task Scheduler")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # start
    start_parser = subparsers.add_parser("start", help="Start scheduler")
    start_parser.add_argument("project", help="Project name")
    start_parser.add_argument(
        "--daemon", "-d", action="store_true", help="Run as daemon (background)"
    )

    # status
    status_parser = subparsers.add_parser("status", help="Show status")
    status_parser.add_argument("project", nargs="?", help="Project name (optional)")

    # report
    report_parser = subparsers.add_parser("report", help="Generate report")
    report_parser.add_argument("project", help="Project name")

    # stop
    stop_parser = subparsers.add_parser("stop", help="Stop scheduler")
    stop_parser.add_argument("project", help="Project name")

    # cleanup
    cleanup_parser = subparsers.add_parser(
        "cleanup", help="Cleanup remote task directories"
    )
    cleanup_parser.add_argument("project", help="Project name")
    cleanup_parser.add_argument(
        "--older-than",
        type=int,
        default=48,
        help="Only clean tasks collected more than N hours ago (default: 48)",
    )
    cleanup_parser.add_argument(
        "--all",
        action="store_true",
        help="Force remove entire project dir on all nodes (legacy behavior)",
    )

    # collect
    collect_parser = subparsers.add_parser(
        "collect", help="Collect and merge git branches"
    )
    collect_parser.add_argument("project", help="Project name")
    collect_parser.set_defaults(func=cmd_collect)

    # validate
    validate_parser = subparsers.add_parser("validate", help="Collect + Build + Test")
    validate_parser.add_argument("project", help="Project name")
    validate_parser.set_defaults(func=cmd_validate)

    # pull mode: poll
    poll_parser = subparsers.add_parser(
        "poll", help="Get pending tasks (for pull mode)"
    )
    poll_parser.add_argument("project", help="Project name")
    poll_parser.add_argument(
        "--limit", type=int, default=10, help="Max tasks to return"
    )

    # pull mode: claim
    claim_parser = subparsers.add_parser("claim", help="Claim a task for execution")
    claim_parser.add_argument("task_id", help="Task ID to claim")

    # pull mode: finish
    finish_parser = subparsers.add_parser("finish", help="Mark task as completed")
    finish_parser.add_argument("task_id", help="Task ID")
    finish_parser.add_argument(
        "--status", default="completed", help="Status: completed/failed"
    )
    finish_parser.add_argument("--error", help="Error message if failed")

    # pull mode: heartbeat
    heartbeat_parser = subparsers.add_parser(
        "heartbeat", help="Send heartbeat for a task"
    )
    heartbeat_parser.add_argument("task_id", help="Task ID")

    # memory: semantic search
    memory_parser = subparsers.add_parser("memory", help="Memory store commands")
    memory_parser.add_argument(
        "memory_action",
        choices=["search", "stats", "add", "clear"],
        help="Action to perform",
    )
    memory_parser.add_argument(
        "query", nargs="?", help="Search query (for search action)"
    )
    memory_parser.add_argument("--limit", type=int, default=5, help="Max results")
    memory_parser.add_argument(
        "--type", "-t", help="Memory type filter (event/task/error/spec/rule)"
    )
    memory_parser.add_argument(
        "--content", "-c", help="Content to add (for add action)"
    )
    memory_parser.set_defaults(func=cmd_memory)

    args = parser.parse_args()

    if args.command == "start":
        cmd_start(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "report":
        cmd_report(args)
    elif args.command == "stop":
        cmd_stop(args)
    elif args.command == "cleanup":
        cmd_cleanup(args)
    elif args.command == "collect":
        args.func(args)
    elif args.command == "poll":
        cmd_poll(args)
    elif args.command == "claim":
        cmd_claim(args)
    elif args.command == "finish":
        cmd_finish(args)
    elif args.command == "heartbeat":
        cmd_heartbeat(args)
    elif args.command == "memory":
        cmd_memory(args)


if __name__ == "__main__":
    main()
