#!/usr/bin/env python3
"""Self-Healing Monitor - 自动修复系统

核心原则：不能停
- 每分钟检查健康状态
- 自动修复常见问题
- 失败自动重启 dispatch
"""

import subprocess
import time
import sys
import os
from datetime import datetime
from pathlib import Path

PROJECTS = ["clawmarketing", "gem-platform", "oyster-infra", "dispatch"]
CHECK_INTERVAL = 60  # 1 分钟检查一次


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def check_dispatch_running(project: str) -> bool:
    """检查 dispatch 进程是否在运行"""
    result = subprocess.run(
        ["pgrep", "-f", f"dispatch.py start {project}"], capture_output=True
    )
    return result.returncode == 0


def restart_dispatch(project: str):
    """重启 dispatch"""
    log(f"⚠️ Restarting {project}...")
    subprocess.run(["pkill", "-f", f"dispatch.py start {project}"], capture_output=True)
    time.sleep(2)
    subprocess.Popen(
        f"cd ~/Downloads/dispatch && python3 dispatch.py start {project}",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    log(f"✅ {project} restarted")


def check_health():
    """检查所有项目健康状态"""
    issues = []

    for project in PROJECTS:
        if not check_dispatch_running(project):
            issues.append(f"{project} not running")
            restart_dispatch(project)

    return issues


def monitor_loop():
    """主监控循环"""
    log("🚀 Self-Healer started - 24/7 monitoring")
    log(f"Watching: {PROJECTS}")

    while True:
        try:
            issues = check_health()
            if issues:
                for issue in issues:
                    log(f"❌ {issue}")
            else:
                log("✅ All systems healthy")
        except Exception as e:
            log(f"❌ Health check error: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    monitor_loop()
