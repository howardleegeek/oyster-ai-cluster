#!/usr/bin/env python3
"""执行器基类"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class ExecResult:
    success: bool
    stdout: str = ""
    stderr: str = ""
    returncode: int = 0

class Executor(ABC):
    @abstractmethod
    def run(self, command: str, cwd: Optional[str] = None, timeout: int = 300) -> ExecResult:
        pass
