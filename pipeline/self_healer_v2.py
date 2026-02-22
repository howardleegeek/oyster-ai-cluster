#!/usr/bin/env python3
"""Self-Healer - Process Supervisor with Backoff + Circuit Breaker

24/7 监控所有 dispatch 进程，挂了自动重启
"""

import os
import sys
import time
import subprocess
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

PROJECTS = ["clawmarketing", "gem-platform", "oyster-infra", "dispatch"]
DISPATCH_PATH = Path.home() / "Downloads" / "dispatch"

# Config
MAX_RESTARTS = 5  # 10分钟内最大重启次数
BACKOFF_WINDOW = 600  # 10分钟窗口
MAX_BACKOFF = 60  # 最大退避60秒
CHECK_INTERVAL = 30  # 30秒检查一次

# State file
STATE_FILE = Path.home() / "dispatch_healer_state.json"


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def load_state():
    """加载状态"""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except:
            pass
    return {"restarts": defaultdict(list), "circuit_broken": []}


def save_state(state):
    """保存状态"""
    STATE_FILE.write_text(json.dumps(state, default=str))


def get_running_dispatch():
    """获取运行中的 dispatch 进程"""
    result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
    running = {}
    for line in result.stdout.split("\n"):
        if "dispatch.py start" in line and "grep" not in line:
            for proj in PROJECTS:
                if f"dispatch.py start {proj}" in line:
                    pid = line.split()[1]
                    running[proj] = pid
    return running


def restart_project(project, state):
    """重启项目"""
    log(f"⚠️ Restarting {project}...")

    # 计算重启次数
    now = datetime.now()
    state["restarts"][project] = [
        t
        for t in state["restarts"][project]
        if now - datetime.fromisoformat(str(t)) < timedelta(seconds=BACKOFF_WINDOW)
    ]

    restart_count = len(state["restarts"][project])

    # 检查是否触发熔断
    if restart_count >= MAX_RESTARTS:
        if project not in state["circuit_broken"]:
            state["circuit_broken"].append(project)
            log(f"🔴 CIRCUIT BREAKER TRIGGERED for {project}")
            save_state(state)
            return False, f"Circuit broken (too many restarts)"

    # 计算退避时间
    backoff = min(2**restart_count, MAX_BACKOFF)
    log(f"  Backoff: {backoff}s")
    time.sleep(backoff)

    # 重启
    subprocess.Popen(
        f"cd {DISPATCH_PATH} && nohup python3 dispatch.py start {project} > ~/dispatch_{project}.log 2>&1 &",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    state["restarts"][project].append(now.isoformat())
    save_state(state)

    return True, f"Restarted (attempt {restart_count + 1}, backoff {backoff}s)"


def check_health():
    """检查所有项目健康状态"""
    state = load_state()
    running = get_running_dispatch()

    issues = []

    for project in PROJECTS:
        # 检查是否被熔断
        if project in state["circuit_broken"]:
            issues.append(f"{project}: 🔴 CIRCUIT BROKEN - manual intervention needed")
            continue

        # 检查是否在运行
        if project not in running:
            success, msg = restart_project(project, state)
            if success:
                issues.append(f"{project}: ✅ Restarted - {msg}")
            else:
                issues.append(f"{project}: ❌ {msg}")
        else:
            # 运行中
            if project in state["circuit_broken"]:
                issues.append(f"{project}: 🔴 Broken")
            else:
                issues.append(f"{project}: ✅ Running (PID: {running[project]})")

    return issues, state


def main():
    """主循环"""
    log("🚀 Self-Healer started - 24/7 monitoring")
    log(f"Projects: {PROJECTS}")
    log(f"Max restarts: {MAX_RESTARTS} per {BACKOFF_WINDOW}s")

    while True:
        try:
            issues, state = check_health()

            # 打印状态
            for issue in issues:
                log(issue)

            # 检查是否有熔断
            broken = state.get("circuit_broken", [])
            if broken:
                log(f"⚠️ Circuit broken: {broken}")

        except Exception as e:
            log(f"❌ Error: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
