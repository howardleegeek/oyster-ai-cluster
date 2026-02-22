#!/usr/bin/env python3
"""本地命令执行器"""
import subprocess
from typing import Optional
from executors.base import Executor, ExecResult

class LocalExecutor(Executor):
    def run(self, command: str, cwd: Optional[str] = None, timeout: int = 300) -> ExecResult:
        try:
            r = subprocess.run(
                command, shell=True, cwd=cwd,
                capture_output=True, text=True, timeout=timeout
            )
            return ExecResult(
                success=r.returncode == 0,
                stdout=r.stdout,
                stderr=r.stderr,
                returncode=r.returncode,
            )
        except subprocess.TimeoutExpired:
            return ExecResult(success=False, stderr=f"Timeout after {timeout}s", returncode=-1)
        except Exception as e:
            return ExecResult(success=False, stderr=str(e), returncode=-1)
