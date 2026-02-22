#!/usr/bin/env python3
"""
Task Poller - Pull mode agent for nodes
每个节点运行这个，主动抢任务直到打满 slots
"""

import os
import sys
import json
import time
import subprocess
import signal
from pathlib import Path
from datetime import datetime

# 配置
DISPATCH_DIR = Path.home() / "Downloads" / "dispatch"
DISPATCH_PY = DISPATCH_DIR / "dispatch.py"
DB_PATH = DISPATCH_DIR / "dispatch.db"
POLL_INTERVAL = 10  # 每 10 秒检查一次

# 获取节点配置
NODE_NAME = os.environ.get("NODE_NAME", "unknown")
SLOTS = int(os.environ.get("NODE_SLOTS", 4))


def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{NODE_NAME}] {msg}", flush=True)


def run_cmd(cmd: list, timeout: int = 30) -> tuple:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"
    except Exception as e:
        return -1, "", str(e)


def dispatch_poll(project: str) -> list:
    """获取 pending 任务"""
    code, out, err = run_cmd(["python3", str(DISPATCH_PY), "poll", project])
    if code != 0:
        log(f"Poll failed: {err}")
        return []

    try:
        return json.loads(out)
    except:
        return []


def dispatch_claim(task_id: str) -> bool:
    """抢占任务"""
    code, out, err = run_cmd(["python3", str(DISPATCH_PY), "claim", task_id])
    if code != 0:
        log(f"Claim {task_id} failed: {err}")
        return False

    try:
        result = json.loads(out)
        return result.get("status") == "claimed"
    except:
        return False


def dispatch_heartbeat(task_id: str):
    """发送心跳"""
    run_cmd(["python3", str(DISPATCH_PY), "heartbeat", task_id])


def dispatch_finish(task_id: str, status: str, error: str = None):
    """标记任务完成"""
    cmd = ["python3", str(DISPATCH_PY), "finish", task_id, "--status", status]
    if error:
        cmd.extend(["--error", error])
    run_cmd(cmd)


def execute_task(task: dict) -> bool:
    """执行任务"""
    task_id = task["id"]
    spec_file = task["spec_file"]
    project = task["project"]

    log(f"Executing {task_id}...")

    # 发送心跳保持
    dispatch_heartbeat(task_id)

    # 获取当前节点配置
    nodes_json = DISPATCH_DIR / "nodes.json"
    node_config = {"api_mode": "zai", "executor": "glm"}

    if nodes_json.exists():
        try:
            with open(nodes_json) as f:
                nodes = json.load(f)
                for n in nodes:
                    if n.get("name") == NODE_NAME:
                        node_config = n
                        break
        except:
            pass

    api_mode = node_config.get("api_mode", "zai")

    # 构建 wrapper 命令
    if spec_file.startswith("/"):
        remote_spec = spec_file
    else:
        remote_spec = f"~/Downloads/specs/{spec_file}"

    # 先 claim 成功后才真正开始执行
    if not dispatch_claim(task_id):
        log(f"Failed to claim {task_id}")
        return False

    # 执行 wrapper
    cmd = ["bash", str(DISPATCH_DIR / "task-wrapper.sh"), project, task_id, remote_spec]

    env = os.environ.copy()
    env["API_MODE"] = api_mode

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=7200,  # 2 小时超时
            env=env,
        )

        if result.returncode == 0:
            dispatch_finish(task_id, "completed")
            log(f"Task {task_id} completed")
            return True
        else:
            dispatch_finish(task_id, "failed", result.stderr[:500])
            log(f"Task {task_id} failed: {result.stderr[:200]}")
            return False

    except subprocess.TimeoutExpired:
        dispatch_finish(task_id, "failed", "Timeout after 2 hours")
        log(f"Task {task_id} timeout")
        return False
    except Exception as e:
        dispatch_finish(task_id, "failed", str(e)[:500])
        log(f"Task {task_id} error: {e}")
        return False


def check_running_tasks() -> int:
    """检查当前运行的任务数"""
    # 从 DB 查询该节点正在运行的任务
    # 这里简化处理，返回当前进程认为正在运行的数量
    return len(RUNNING_TASKS)


# 全局状态
RUNNING_TASKS = {}
RUNNING = True


def signal_handler(signum, frame):
    global RUNNING
    log("Received signal, stopping...")
    RUNNING = False


def main():
    global RUNNING_TASKS, RUNNING

    if len(sys.argv) < 2:
        print("Usage: task-poller.py <project> [node_name] [slots]")
        sys.exit(1)

    project = sys.argv[1]

    global NODE_NAME, SLOTS
    if len(sys.argv) > 2:
        NODE_NAME = sys.argv[2]
    if len(sys.argv) > 3:
        SLOTS = int(sys.argv[3])

    # 如果没传 node_name，尝试从 nodes.json 获取
    if NODE_NAME == "unknown":
        nodes_json = DISPATCH_DIR / "nodes.json"
        if nodes_json.exists():
            try:
                with open(nodes_json) as f:
                    nodes = json.load(f)
                    # 尝试获取当前 hostname 对应的节点
                    hostname = subprocess.run(
                        ["hostname"], capture_output=True, text=True
                    ).stdout.strip()
                    for n in nodes:
                        if n.get("ssh_host") == hostname or n.get("name") == hostname:
                            NODE_NAME = n.get("name", hostname)
                            SLOTS = n.get("slots", 4)
                            break
            except:
                pass

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    log(f"Starting poller for {project} on {NODE_NAME} ({SLOTS} slots)")

    while RUNNING:
        # 检查空闲 slots
        current_running = len(RUNNING_TASKS)
        available_slots = SLOTS - current_running

        if available_slots <= 0:
            log(f"All slots full ({current_running}/{SLOTS}), waiting...")
            time.sleep(POLL_INTERVAL)
            continue

        # 拉取任务
        tasks = dispatch_poll(project)

        if not tasks:
            time.sleep(POLL_INTERVAL)
            continue

        # 抢任务直到打满
        for task in tasks:
            if len(RUNNING_TASKS) >= SLOTS:
                break

            if not RUNNING:
                break

            task_id = task["id"]

            # 检查依赖是否满足
            depends_on = task.get("depends_on", [])
            if depends_on:
                # 简单检查：依赖的任务是否都已完成
                # 实际应该查 DB，这里简化处理
                pass

            # 尝试 claim
            if dispatch_claim(task_id):
                log(f"Claimed {task_id}")

                # 后台执行
                import threading

                def run_and_track():
                    success = execute_task(task)
                    if task_id in RUNNING_TASKS:
                        del RUNNING_TASKS[task_id]

                t = threading.Thread(target=run_and_track)
                t.start()
                RUNNING_TASKS[task_id] = t

        time.sleep(POLL_INTERVAL)

    # 等待所有任务完成
    log("Waiting for running tasks to finish...")
    for task_id, t in RUNNING_TASKS.items():
        t.join(timeout=60)

    log("Poller stopped")


if __name__ == "__main__":
    main()
