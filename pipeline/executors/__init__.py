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
