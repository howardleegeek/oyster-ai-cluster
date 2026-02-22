"""
JSON Protocol 输出标准化
所有任务输出必须是单行 JSON，不是 JSON 则标记为 parse_error
"""

import json
import logging
from typing import Any
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

PROTOCOL_VERSION = "1.0"


@dataclass
class TaskResult:
    """标准化的任务结果"""

    ok: bool
    task_id: str
    status: str  # COMPLETED, FAILED, TIMEOUT, PARSE_ERROR

    # 输出数据
    artifacts: list[dict] = field(default_factory=list)
    stdout: str = ""
    stderr: str = ""

    # 元数据
    metrics: dict = field(default_factory=dict)
    error: str | None = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    # 版本
    protocol_version: str = PROTOCOL_VERSION

    def to_json(self) -> str:
        """序列化为单行 JSON"""
        return json.dumps(self.__dict__, ensure_ascii=False)

    @classmethod
    def from_json(cls, data: str) -> "TaskResult":
        """从 JSON 解析"""
        try:
            obj = json.loads(data)
            return cls(**obj)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

    @classmethod
    def success(
        cls,
        task_id: str,
        artifacts: list[dict] = None,
        stdout: str = "",
        metrics: dict = None,
    ) -> "TaskResult":
        """创建成功结果"""
        return cls(
            ok=True,
            task_id=task_id,
            status="COMPLETED",
            artifacts=artifacts or [],
            stdout=stdout,
            metrics=metrics or {},
        )

    @classmethod
    def failure(
        cls, task_id: str, error: str, stderr: str = "", metrics: dict = None
    ) -> "TaskResult":
        """创建失败结果"""
        return cls(
            ok=False,
            task_id=task_id,
            status="FAILED",
            error=error,
            stderr=stderr,
            metrics=metrics or {},
        )

    @classmethod
    def timeout(cls, task_id: str, metrics: dict = None) -> "TaskResult":
        """创建超时结果"""
        return cls(
            ok=False,
            task_id=task_id,
            status="TIMEOUT",
            error="Task execution exceeded timeout",
            metrics=metrics or {},
        )

    @classmethod
    def parse_error(
        cls, task_id: str, raw_output: str, error: str = "Output is not valid JSON"
    ) -> "TaskResult":
        """创建解析错误结果"""
        return cls(
            ok=False,
            task_id=task_id,
            status="PARSE_ERROR",
            error=error,
            stdout=raw_output[:1000],  # 截断避免太大
            metrics={"parse_error": True},
        )


def validate_output(output: str) -> tuple[bool, dict | None]:
    """
    验证输出是否是有效的 JSON Protocol
    返回: (is_valid, parsed_data or None)
    """
    if not output or not output.strip():
        return False, None

    try:
        data = json.loads(output.strip())
        # 检查必需字段
        if "ok" in data and "task_id" in data and "status" in data:
            return True, data
        return False, None
    except json.JSONDecodeError:
        return False, None


def parse_task_output(stdout: str, stderr: str, task_id: str,
                      exit_code: int = None) -> TaskResult:
    """
    解析任务输出
    优先尝试解析 JSON Protocol，否则尝试解析任意 JSON，
    最后用 exit_code 判断成功/失败（兼容 task-wrapper.sh 非 JSON 输出）
    """
    # 尝试找最后一个有效的 JSON 对象（可能有多行日志）
    lines = stdout.strip().split("\n")

    # 从后往前找有效 JSON
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            if isinstance(data, dict) and "ok" in data:
                return TaskResult(**data)
        except json.JSONDecodeError:
            continue

    # 尝试解析整个 stdout
    try:
        data = json.loads(stdout.strip())
        if isinstance(data, dict) and "ok" in data:
            return TaskResult(**data)
    except json.JSONDecodeError:
        pass

    # No JSON protocol output found — fall back to exit code
    # This handles task-wrapper.sh which outputs human-readable text
    if exit_code is not None and exit_code == 0:
        return TaskResult.success(
            task_id,
            stdout=stdout[-2000:] if len(stdout) > 2000 else stdout,
            metrics={"exit_code": exit_code, "inferred_from_exit_code": True},
        )
    elif exit_code is not None:
        error_msg = stderr.strip()[-500:] if stderr.strip() else f"exit code {exit_code}"
        return TaskResult.failure(
            task_id,
            error=error_msg,
            stderr=stderr[-1000:] if len(stderr) > 1000 else stderr,
            metrics={"exit_code": exit_code, "inferred_from_exit_code": True},
        )

    # No exit code info either — parse_error
    error_msg = stderr.strip() if stderr.strip() else "Output is not valid JSON"
    return TaskResult.parse_error(task_id, stdout + "\n" + stderr)
