#!/usr/bin/env python3
"""Layer 基类与结果模型"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class LayerResult:
    layer: str
    status: str  # PASS / FAIL
    report: dict = field(default_factory=dict)
    error: Optional[str] = None
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    finished_at: Optional[str] = None

    def finish(self, status: str, report: dict = None, error: str = None):
        self.status = status
        self.finished_at = datetime.utcnow().isoformat()
        if report:
            self.report = report
        if error:
            self.error = error


class Layer(ABC):
    name: str = ""
    max_retries: int = 3
    required_prev: list[str] = []  # 前置层名，如 ["L1"]

    @abstractmethod
    def execute(self, project_config, prev_results: dict) -> LayerResult:
        """执行层逻辑。prev_results: {layer_name: LayerResult}"""
        pass

    def check_preconditions(self, prev_results: dict) -> tuple[bool, str]:
        """检查前置条件。返回 (ok, reason)"""
        for req in self.required_prev:
            r = prev_results.get(req)
            # L5 特殊：L4 FAIL 也允许进入（用于修复）
            if self.name == "L5" and req == "L4":
                if not r:
                    return False, f"前置层 {req} 结果缺失"
                # L4 有结果就可以进 L5，不管 PASS 还是 FAIL
                continue
            if not r or r.status != "PASS":
                return False, f"前置层 {req} 未通过"
        return True, ""

    def validate(self, result: LayerResult) -> bool:
        return result.status == "PASS"
