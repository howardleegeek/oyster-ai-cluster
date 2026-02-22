---
task_id: S12-task-wrapper-hard-timeout-v2
project: dispatch
priority: 1
depends_on: []
modifies: ["dispatch/task-wrapper.sh"]
executor: glm
---

## 目标
给 `dispatch/task-wrapper.sh` 增加“全局硬超时兜底”，保证每个任务的 LLM 执行与 wrapper 自己跑的验证测试都**可退出、可控、有上限**，避免 watch / 卡死吞掉关键路径。

## 背景
近期出现过 `npm test`/`vitest` 进入 watch 导致单任务挂住 40+ 分钟的情况。即使 spec 里写了 targeted tests，也需要 wrapper 级别的兜底保护。

## 约束
- 不引入新依赖（只能用 bash + 系统已有工具；如无 `timeout`，允许用 `python3` 做 fallback）
- 不破坏现有 rate-limit fallback 逻辑
- 不改变 task-wrapper.sh 的入参签名
- 超时后必须能让 dispatch 正确把任务标记为 **failed**（不能用新 status 值导致 scheduler 不认识）

## 具体改动

### 1) 增加可移植的 timeout helper
在 `task-wrapper.sh` 里增加一个 `run_with_timeout`（或同等）函数：
- 优先使用 `timeout`（Linux）
- 其次使用 `gtimeout`（macOS coreutils）
- 两者都没有时，用 `python3` 启动子进程并在超时后 kill 整个进程组（exit code 固定为 124）

默认超时（可被 env 覆盖）：
- `TASK_TIMEOUT_SECS=3600`（LLM 执行上限，1h）
- `VERIFY_TIMEOUT_SECS=1200`（wrapper 验证测试上限，20m）
- `*_KILL_SECS=30`（SIGTERM→SIGKILL 的宽限）

### 2) 给 LLM 执行加硬超时
将 `claude -p ...` 与 `codex exec ...` 都包一层 `run_with_timeout`。
- 如果 LLM 执行 exit code = 124：
  - 不再尝试 fallback
  - 不再跑后续 git commit / TODO check / verification tests（避免额外吞时间）
  - 最终 `status.json` 写 `status=failed` 且 `error` 字段写明超时原因

### 3) 给 wrapper 自己跑的验证测试加硬超时
对 `pytest` / `npm test` / `make test` / `./run.sh test` 都加 `run_with_timeout`。
- 任一验证命令超时：exit code 保留为 124，并写 `error="verification timeout ..."`
- 任一验证命令失败：写 `error="verification tests failed"`

### 4) status.json 增强
当前 wrapper 写 `status=failed` 时没有 `error` 字段，会导致 dispatch 侧显示 `Unknown error`。
本次改动要求：
- 失败时一定写 `error` 字段
- 超时与验证失败的 error 信息可直接用于 report

## 验收标准
- [ ] `bash -n ~/Downloads/dispatch/task-wrapper.sh` 通过
- [ ] `task-wrapper.sh` 中 `claude -p` 与 `codex exec` 都被硬超时保护
- [ ] LLM 超时（exit 124）时，任务能被 dispatch 标记为 failed，且 error 包含 timeout 文案
- [ ] wrapper 跑 `npm test` / `pytest` 等验证命令时，均有硬超时兜底

## 不要做
- 不修改 dispatch.py 的调度逻辑
- 不改变 fallback provider 策略（只是在超时时直接终止）
- 不把 status 改成新的枚举值（比如 timeout），避免 scheduler 不认识而卡在 running
