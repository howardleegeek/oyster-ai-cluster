#!/usr/bin/env python3
"""
Task Watcher - Hybrid Mode 节点执行器
监听任务目录，检测到新 spec 就自动执行
"""

import os
import sys
import json
import time
import subprocess
import signal
from pathlib import Path
from datetime import datetime
from threading import Thread

# 配置
DISPATCH_DIR = Path(os.environ.get("DISPATCH_DIR", str(Path.home() / "dispatch")))


# 支持多个任务目录 - 扫描所有项目目录
def get_all_task_dirs():
    """动态扫描 ~/dispatch/ 下所有项目的 tasks 目录"""
    dirs = []
    dispatch_dir = Path(os.environ.get("DISPATCH_DIR", str(Path.home() / "dispatch")))

    # 扫描 dispatch 目录下的所有子目录
    if dispatch_dir.exists():
        for subdir in dispatch_dir.iterdir():
            if subdir.is_dir() and not subdir.name.startswith("."):
                tasks_dir = subdir / "tasks"
                if tasks_dir.exists():
                    dirs.append(tasks_dir)
                    print(f"[TaskWatcher] Found tasks dir: {tasks_dir}", flush=True)

    # 也添加传统的两个目录（向后兼容）
    legacy_dirs = [
        dispatch_dir / "tasks",
        dispatch_dir / "dispatch" / "tasks",
    ]
    for d in legacy_dirs:
        if d.exists() and d not in dirs:
            dirs.append(d)

    return dirs


TASK_DIRS = get_all_task_dirs()

NODE_NAME = os.environ.get("NODE_NAME", "unknown")
SLOTS = int(os.environ.get("NODE_SLOTS", 4))
CHECK_INTERVAL = 5


def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{NODE_NAME}] {msg}", flush=True)


class TaskRunner:
    def __init__(self, max_concurrent=4):
        self.running_tasks = {}
        self.max_concurrent = max_concurrent

    def can_run(self):
        return len(self.running_tasks) < self.max_concurrent

    def run_task(self, project: str, task_id: str, spec_file: str):
        log(f"Starting task {task_id}")

        spec_path = Path(spec_file)
        task_dir = spec_path.parent
        status_file = task_dir / "status.json"

        # Update status to running (already claimed)
        with open(status_file, "w") as f:
            json.dump(
                {"status": "running", "started_at": datetime.now().isoformat()}, f
            )

        # 获取 API 模式
        api_mode = "zai"
        nodes_json = DISPATCH_DIR / "nodes.json"
        if nodes_json.exists():
            try:
                with open(nodes_json) as f:
                    for n in json.load(f):
                        if n.get("name") == NODE_NAME:
                            api_mode = n.get("api_mode", "zai")
                            break
            except:
                pass

        wrapper = DISPATCH_DIR / "task-wrapper.sh"
        cmd = ["bash", str(wrapper), project, task_id, spec_file]

        env = os.environ.copy()
        env["API_MODE"] = api_mode

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=7200, env=env
            )

            with open(task_dir / "result.json", "w") as f:
                json.dump(
                    {
                        "exit_code": result.returncode,
                        "stdout": result.stdout[:5000],
                        "stderr": result.stderr[:5000],
                    },
                    f,
                )

            status = "completed" if result.returncode == 0 else "failed"
            with open(status_file, "w") as f:
                json.dump({"status": status}, f)

            log(f"Task {task_id} {status}")

        except Exception as e:
            with open(status_file, "w") as f:
                json.dump({"status": "failed", "error": str(e)}, f)
            log(f"Task {task_id} error: {e}")


class TaskWatcher:
    def __init__(self, runner):
        self.runner = runner
        self.processed = set()
        self.running = True

    def scan_tasks(self):
        for TASK_DIR in TASK_DIRS:
            if not TASK_DIR.exists():
                continue

            # TASK_DIR is like ~/dispatch/dispatch-test/tasks/
            # The parent of TASK_DIR is the project name (dispatch-test)
            project = TASK_DIR.parent.name

            for task_dir in TASK_DIR.iterdir():
                if not task_dir.is_dir():
                    continue

                task_id = task_dir.name
                task_key = f"{project}/{task_id}"

                if task_key in self.processed:
                    continue

                spec_file = task_dir / "spec.md"
                status_file = task_dir / "status.json"

                if not spec_file.exists():
                    continue

                status_data = {}
                if status_file.exists():
                    try:
                        with open(status_file) as f:
                            status_data = json.load(f)
                    except:
                        pass

                status = status_data.get("status", "pending")

                # Skip if completed or failed
                if status in ("completed", "failed"):
                    self.processed.add(task_key)
                    continue

                # Skip if assigned to different node
                if status == "running" and status_data.get("node") != NODE_NAME:
                    self.processed.add(task_key)
                    continue

                # Try to atomically claim the task (including running tasks for this node)
                claim_status = {
                    "status": "claimed",
                    "claimed_by": NODE_NAME,
                    "claimed_at": datetime.now().isoformat(),
                }
                try:
                    with open(status_file, "w") as f:
                        json.dump(claim_status, f)

                    with open(status_file) as f:
                        verify = json.load(f)
                    if verify.get("status") != "claimed":
                        self.processed.add(task_key)
                        continue
                except Exception as e:
                    log(f"Failed to claim {task_id}: {e}")
                    continue

                if not self.runner.can_run():
                    with open(status_file, "w") as f:
                        json.dump({"status": "pending", "error": "no slots"}, f)
                    break

                self.processed.add(task_key)
                log(f"Detected task: {task_id}")

                Thread(
                    target=self.runner.run_task,
                    args=(project, task_id, str(spec_file)),
                    daemon=True,
                ).start()

    def run(self):
        log(f"Task watcher started (slots={SLOTS})")
        while self.running:
            try:
                self.scan_tasks()
            except Exception as e:
                log(f"Error: {e}")
            time.sleep(CHECK_INTERVAL)


def main():
    global NODE_NAME, SLOTS

    if len(sys.argv) >= 2:
        NODE_NAME = sys.argv[1]
    if len(sys.argv) >= 3:
        SLOTS = int(sys.argv[2])

    # 自动检测节点名
    if NODE_NAME == "unknown":
        try:
            hostname = subprocess.run(
                ["hostname"], capture_output=True, text=True
            ).stdout.strip()
            nodes_json = DISPATCH_DIR / "nodes.json"
            if nodes_json.exists():
                with open(nodes_json) as f:
                    for n in json.load(f):
                        if n.get("ssh_host") == hostname:
                            NODE_NAME = n.get("name", hostname)
                            SLOTS = n.get("slots", 4)
                            break
        except:
            pass

    # 简单的信号处理
    def handle_signal(sig, frame):
        log("Received signal, stopping...")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # 自动重启循环
    while True:
        try:
            runner = TaskRunner(SLOTS)
            watcher = TaskWatcher(runner)
            watcher.run()
        except Exception as e:
            log(f"Watcher crashed: {e}, restarting in 5s...")
            time.sleep(5)


if __name__ == "__main__":
    main()
