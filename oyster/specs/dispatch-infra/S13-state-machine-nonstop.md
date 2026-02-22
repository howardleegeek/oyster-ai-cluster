---
task_id: S13-state-machine-nonstop
project: dispatch-infra
priority: 2
estimated_minutes: 45
depends_on: []
modifies: ["nonstop-loop.sh"]
executor: glm
---

## 目标
新建 `nonstop-machine.py`，替代 `nonstop-loop.sh` 的 while+sleep 循环，使用 Python 状态机实现。

## 输出文件
只产出 1 个新文件: `nonstop-machine.py`

## 核心要求 — 每个状态必须调用实际命令

每个状态执行 `subprocess.run()` 调用真实的 dispatch.py 命令:

```python
import subprocess, signal, json, time, argparse
from enum import Enum
from pathlib import Path

DISPATCH = str(Path(__file__).parent / "dispatch.py")

class State(Enum):
    IDLE = "idle"
    CHECK_STATUS = "check"
    ENSURE_CONTROLLER = "ctrl"
    SCAN_SPECS = "scan"
    AUTO_COLLECT = "collect"
    REPORT = "report"
    COOLDOWN = "cooldown"
    STOPPED = "stopped"

class NonstopMachine:
    STATE_FILE = Path.home() / "dispatch/nonstop-state.json"

    def __init__(self):
        self.state = State.IDLE
        self.loop_count = 0
        self.last_collect_ts = 0
        self.last_report_ts = 0
        self.paused = False
        self._load_state()
        self._setup_signals()  # 必须实现

    def _setup_signals(self):
        """必须注册这三个信号处理器"""
        signal.signal(signal.SIGUSR1, self._handle_pause)    # 暂停
        signal.signal(signal.SIGUSR2, self._handle_skip)     # 跳到下一步
        signal.signal(signal.SIGTERM, self._handle_stop)     # 优雅停止
        signal.signal(signal.SIGINT, self._handle_stop)      # Ctrl+C

    def _handle_pause(self, signum, frame):
        self.paused = True
        self._save_state()
        print(f"[PAUSED] state={self.state.value}")

    def _handle_skip(self, signum, frame):
        print(f"[SKIP] jumping from {self.state.value}")
        self.state = self._next_state()

    def _handle_stop(self, signum, frame):
        self.state = State.STOPPED
        self._save_state()
        print("[STOPPED] graceful shutdown")
        raise SystemExit(0)

    def step(self):
        """执行当前状态的动作，返回下一状态"""
        if self.state == State.CHECK_STATUS:
            # 必须调用: python3 dispatch.py status <project>
            subprocess.run(["python3", DISPATCH, "status"], capture_output=True)

        elif self.state == State.ENSURE_CONTROLLER:
            # 检查 dispatch-controller.py 是否在运行，不在就启动
            # 用 pgrep 或 ps 检查，用 subprocess.Popen 启动
            pass  # 实现这个逻辑

        elif self.state == State.SCAN_SPECS:
            # 必须调用: python3 dispatch.py start <project> 对所有活跃项目
            subprocess.run(["python3", DISPATCH, "start"], capture_output=True)

        elif self.state == State.AUTO_COLLECT:
            if time.time() - self.last_collect_ts > int(os.environ.get("COLLECT_INTERVAL", "600")):
                subprocess.run(["python3", DISPATCH, "auto-collect"], capture_output=True)
                self.last_collect_ts = time.time()

        elif self.state == State.REPORT:
            if time.time() - self.last_report_ts > int(os.environ.get("REPORT_INTERVAL", "1800")):
                subprocess.run(["python3", DISPATCH, "report"], capture_output=True)
                self.last_report_ts = time.time()

        elif self.state == State.COOLDOWN:
            time.sleep(int(os.environ.get("LOOP_INTERVAL", "60")))
            self.loop_count += 1

        self.state = self._next_state()
        self._save_state()
        return self.state
```

## 状态转移（必须只有一个 _next_state 方法，不要重复逻辑）
```
IDLE → CHECK_STATUS → ENSURE_CONTROLLER → SCAN_SPECS → AUTO_COLLECT → REPORT → COOLDOWN → IDLE
STOPPED = 终态
```

## CLI 参数（用 argparse）
```bash
python3 nonstop-machine.py                  # 主循环
python3 nonstop-machine.py --status         # 打印当前状态 JSON
python3 nonstop-machine.py --pause          # 写 paused=true 到 state file
python3 nonstop-machine.py --resume         # 写 paused=false
python3 nonstop-machine.py --step           # 执行一步就退出
python3 nonstop-machine.py --reset          # 删除 state file
```

## 绝对禁止
- ❌ 不碰 dispatch-controller.py（任何修改都判 FAIL）
- ❌ 不碰 dispatch.py（任何修改都判 FAIL）
- ❌ 不碰 task-wrapper.sh / bootstrap.sh
- ❌ 不引入任何外部依赖（只用标准库: subprocess, signal, json, time, argparse, pathlib, enum, os）
- ❌ step() 和 _next_state() 不能有重复的状态转移逻辑（只在 _next_state 一个地方定义转移）
- ❌ 不要写 placeholder/stub — 每个状态必须有真正的 subprocess.run 调用

## 验收标准
- [ ] nonstop-machine.py 是唯一新文件
- [ ] dispatch-controller.py 和 dispatch.py 零改动
- [ ] 每个状态调用真实 dispatch.py 命令（不是空 pass）
- [ ] signal.signal() 注册了 SIGUSR1, SIGUSR2, SIGINT, SIGTERM
- [ ] _save_state() 和 _load_state() 操作 ~/dispatch/nonstop-state.json
- [ ] --status/--pause/--resume/--step/--reset 五个 CLI 参数可用
- [ ] python3 -c "import nonstop_machine" 不报错
- [ ] 状态转移逻辑只在 _next_state() 一个地方定义
