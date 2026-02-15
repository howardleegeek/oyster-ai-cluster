#!/usr/bin/env python3
"""OpenCode / MiniMax 执行器"""

import subprocess
import os
from typing import Optional
from executors.base import Executor, ExecResult


class OpenCodeExecutor(Executor):
    def run(
        self, prompt: str, cwd: Optional[str] = None, timeout: int = 600
    ) -> ExecResult:
        """调用 opencode run 执行 AI 任务"""
        # 使用完整路径
        cmd = f'/home/ubuntu/.opencode/bin/opencode run "{prompt}"'
        try:
            r = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return ExecResult(
                success=r.returncode == 0,
                stdout=r.stdout,
                stderr=r.stderr,
                returncode=r.returncode,
            )
        except subprocess.TimeoutExpired:
            return ExecResult(
                success=False, stderr=f"OpenCode timeout {timeout}s", returncode=-1
            )
        except Exception as e:
            return ExecResult(success=False, stderr=str(e), returncode=-1)

    def generate_specs(self, gap_report: dict, project_name: str) -> str:
        """根据 gap report 生成修复 spec"""
        prompt = f"""你是代码工程师。根据以下 gap report 生成修复 spec:

项目: {project_name}
Gap Report:
{gap_report}

输出格式: YAML front-matter spec，包含 task_id, modifies, 目标, 约束, 验收标准。
每个 placeholder/mock 一个 spec。"""
        result = self.run(prompt)
        return result.stdout
