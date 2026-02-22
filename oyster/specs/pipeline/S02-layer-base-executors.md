---
task_id: S02-layer-base-executors
project: pipeline
priority: 1
depends_on: [S01]
modifies: ["dispatch/pipeline/layers/base.py", "dispatch/pipeline/layers/__init__.py", "dispatch/pipeline/executors/base.py", "dispatch/pipeline/executors/local.py", "dispatch/pipeline/executors/dispatch_exec.py", "dispatch/pipeline/executors/opencode.py", "dispatch/pipeline/executors/__init__.py"]
executor: glm
---

## 目标
实现 Layer 基类 + 3 个执行器（local, dispatch, opencode）

## 要创建的文件

### 1. dispatch/pipeline/layers/__init__.py
```python
from layers.base import Layer, LayerResult
__all__ = ["Layer", "LayerResult"]
```

### 2. dispatch/pipeline/layers/base.py
```python
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
            if not r or r.status != "PASS":
                return False, f"前置层 {req} 未通过"
        return True, ""

    def validate(self, result: LayerResult) -> bool:
        return result.status == "PASS"
```

### 3. dispatch/pipeline/executors/__init__.py
```python
from executors.base import Executor, ExecResult
from executors.local import LocalExecutor
from executors.dispatch_exec import DispatchExecutor
from executors.opencode import OpenCodeExecutor

EXECUTORS = {
    "local": LocalExecutor,
    "dispatch": DispatchExecutor,
    "opencode": OpenCodeExecutor,
}

def get_executor(name: str) -> Executor:
    cls = EXECUTORS.get(name)
    if not cls:
        raise ValueError(f"Unknown executor: {name}. Available: {list(EXECUTORS.keys())}")
    return cls()
```

### 4. dispatch/pipeline/executors/base.py
```python
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
```

### 5. dispatch/pipeline/executors/local.py
```python
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
```

### 6. dispatch/pipeline/executors/dispatch_exec.py
```python
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
```

### 7. dispatch/pipeline/executors/opencode.py
```python
#!/usr/bin/env python3
"""OpenCode / MiniMax 执行器"""
import subprocess
import os
from typing import Optional
from executors.base import Executor, ExecResult

class OpenCodeExecutor(Executor):
    def run(self, prompt: str, cwd: Optional[str] = None, timeout: int = 600) -> ExecResult:
        """调用 opencode run 执行 AI 任务"""
        # 优先用 opencode CLI
        cmd = f'opencode run "{prompt}"'
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
            return ExecResult(success=False, stderr=f"OpenCode timeout {timeout}s", returncode=-1)
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
```

## 验收标准
- [ ] `python3 -c "from executors import get_executor; e=get_executor('local'); print(e.run('echo ok'))"` 输出 success=True
- [ ] `python3 -c "from layers.base import Layer, LayerResult; print('OK')"` 无报错
- [ ] DispatchExecutor 能找到 dispatch.py 路径

## 不要做
- 不要修改 dispatch.py
- 不要实现具体的 L1-L6 层（S04-S06 做）
- 不要创建 pipeline.py CLI（S03 做）
