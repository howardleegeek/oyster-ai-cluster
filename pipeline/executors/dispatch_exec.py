#!/usr/bin/env python3
"""Dispatch.py 执行器 — 黑盒调用"""
import subprocess
import time
import json
from pathlib import Path
from typing import Optional
from executors.base import Executor, ExecResult

DISPATCH_PY = Path(__file__).parent.parent.parent / "dispatch.py"

class DispatchExecutor(Executor):
    def run(self, command: str, cwd: Optional[str] = None, timeout: int = 600) -> ExecResult:
        """command 格式: 'start <project>' / 'status <project>' / 'collect <project>'"""
        cmd = f"python3 {DISPATCH_PY} {command}"
        try:
            r = subprocess.run(
                cmd, shell=True, cwd=cwd,
                capture_output=True, text=True, timeout=timeout
            )
            return ExecResult(
                success=r.returncode == 0,
                stdout=r.stdout, stderr=r.stderr, returncode=r.returncode,
            )
        except subprocess.TimeoutExpired:
            return ExecResult(success=False, stderr=f"Dispatch timeout {timeout}s", returncode=-1)

    def start_and_wait(self, project: str, poll_interval: int = 30, max_wait: int = 3600) -> ExecResult:
        """启动 dispatch 并轮询等待完成"""
        start = self.run(f"start {project}")
        if not start.success:
            return start
        elapsed = 0
        while elapsed < max_wait:
            time.sleep(poll_interval)
            elapsed += poll_interval
            status = self.run(f"status {project}")
            # 检查是否全部完成
            if "DONE" in status.stdout or "all tasks completed" in status.stdout.lower():
                return self.run(f"collect {project}")
            if "FAILED" in status.stdout:
                return ExecResult(success=False, stdout=status.stdout, stderr="Tasks failed", returncode=1)
        return ExecResult(success=False, stderr=f"Timeout waiting {max_wait}s", returncode=-1)
