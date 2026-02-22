"""
任务执行器 - setsid + killpg + timeout
"""

import os
import sys
import json
import time
import signal
import asyncio
import logging
import subprocess
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

import protocol

logger = logging.getLogger(__name__)


@dataclass
class RunningTask:
    """运行中的任务"""

    task_id: str
    process: subprocess.Popen
    start_time: float
    timeout: int
    lease_owner: str


class TaskRunner:
    """任务执行器 - 负责 setsid + killpg + timeout"""

    def __init__(self, task_timeout: int = 600, cleanup_timeout: int = 30):
        self.task_timeout = task_timeout
        self.cleanup_timeout = cleanup_timeout
        self.running_tasks: dict[str, RunningTask] = {}

    async def execute(
        self,
        task_id: str,
        command: str,
        cwd: str = "/home/user",
        env: dict = None,
        timeout: int = None,
        lease_owner: str = "",
    ) -> protocol.TaskResult:
        """
        执行任务
        - 使用 setsid 创建新进程组
        - 超时后使用 killpg 杀死整个进程组
        - 返回标准化 JSON 结果
        """
        timeout = timeout or self.task_timeout
        start_time = time.time()

        logger.info(f"[{task_id}] Starting task: {command[:100]}")

        # 准备环境变量
        exec_env = os.environ.copy()
        if env:
            exec_env.update(env)

        try:
            # 使用 setsid 创建新进程组
            # - setsid: 创建新会话，成为新进程组的leader
            # - stdout/stderr: 重定向到 pipe
            process = subprocess.Popen(
                f"setsid {command}",
                shell=True,
                cwd=cwd,
                env=exec_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid,  # 关键：创建新进程组
            )

            # 注册到运行任务
            running = RunningTask(
                task_id=task_id,
                process=process,
                start_time=start_time,
                timeout=timeout,
                lease_owner=lease_owner,
            )
            self.running_tasks[task_id] = running

            # 等待完成或超时
            try:
                stdout, stderr = await self._wait_with_timeout(process, timeout)
            except asyncio.TimeoutError:
                # 超时，杀死进程组
                logger.warning(f"[{task_id}] Task timeout, killing process group")
                self._kill_process_group(process)
                stdout, stderr = process.communicate()  # 收集剩余输出

                elapsed = time.time() - start_time
                return protocol.TaskResult.timeout(task_id, {"elapsed": elapsed})

            # 任务完成
            elapsed = time.time() - start_time

            # 解析输出 (pass exit_code for fallback when no JSON protocol)
            result = protocol.parse_task_output(
                stdout, stderr, task_id, exit_code=process.returncode
            )
            result.metrics["elapsed"] = elapsed
            result.metrics["exit_code"] = process.returncode

            logger.info(
                f"[{task_id}] Task completed: {result.status}, elapsed={elapsed:.1f}s"
            )
            return result

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"[{task_id}] Task failed with exception: {e}")
            return protocol.TaskResult.failure(
                task_id, str(e), metrics={"elapsed": elapsed}
            )

        finally:
            # 清理
            self.running_tasks.pop(task_id, None)

    async def _wait_with_timeout(self, process: subprocess.Popen, timeout: int):
        """等待进程完成，支持超时"""
        loop = asyncio.get_event_loop()

        # 轮询检查进程状态
        start = time.time()
        while True:
            # 检查是否完成
            if process.poll() is not None:
                # 收集输出
                stdout, stderr = process.communicate()
                return stdout, stderr

            # 检查超时
            if time.time() - start > timeout:
                raise asyncio.TimeoutError()

            # 短暂休眠
            await asyncio.sleep(0.5)

    def _kill_process_group(self, process: subprocess.Popen):
        """
        杀死整个进程组（进程 + 子进程 + 孙进程）
        """
        try:
            # 获取进程组 ID
            pgid = os.getpgid(process.pid)
            logger.info(f"[{process.pid}] Killing process group {pgid}")

            # 发送 SIGTERM 到整个进程组
            os.killpg(pgid, signal.SIGTERM)

            # 等待一下让进程优雅退出
            time.sleep(1)

            # 如果还在运行，强制杀死
            if process.poll() is None:
                os.killpg(pgid, signal.SIGKILL)
                logger.warning(f"[{process.pid}] Force killed process group {pgid}")

        except ProcessLookupError:
            # 进程已经不存在
            pass
        except Exception as e:
            logger.error(f"[{process.pid}] Failed to kill process group: {e}")

    def kill_task(self, task_id: str) -> bool:
        """强制终止指定任务"""
        running = self.running_tasks.get(task_id)
        if not running:
            logger.warning(f"[{task_id}] Task not found or already finished")
            return False

        logger.info(f"[{task_id}] Killing task on request")
        self._kill_process_group(running.process)
        return True

    def get_running_tasks(self) -> list[dict]:
        """获取所有运行中的任务"""
        return [
            {
                "task_id": rt.task_id,
                "lease_owner": rt.lease_owner,
                "elapsed": time.time() - rt.start_time,
                "timeout": rt.timeout,
            }
            for rt in self.running_tasks.values()
        ]

    async def cleanup_orphans(self):
        """
        清理孤儿进程（启动时检查）
        扫描可能残留的进程组并清理
        """
        logger.info("Scanning for orphan processes...")
        # 注意：这里需要根据实际情况实现
        # 可能需要解析 ps 输出，找到可疑进程并 killpg
        pass
