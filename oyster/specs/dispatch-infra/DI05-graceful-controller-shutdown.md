---
task_id: DI05-graceful-controller-shutdown
project: dispatch-infra
priority: 1
estimated_minutes: 35
depends_on: []
modifies: ["dispatch-controller.py"]
executor: glm
---
## 目标
给 dispatch-controller.py 添加优雅关闭机制，停止时不丢失正在运行的任务状态

## 技术方案
1. **注册信号处理器**:
```python
import signal

shutdown_event = asyncio.Event()

def handle_shutdown(signum, frame):
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_event.set()

signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)
```

2. **优雅关闭流程**:
```python
async def graceful_shutdown():
    """Stop dispatching new tasks, wait for running tasks to finish heartbeat cycle"""
    logger.info("Graceful shutdown: stopping new dispatches...")
    # Stop accepting new tasks
    self.accepting_tasks = False
    # Wait up to 30s for current dispatch cycle to complete
    await asyncio.sleep(30)
    # Close DB connections cleanly
    self.db_pool.close()
    logger.info("Graceful shutdown complete")
```

3. **在主循环中检查 shutdown_event**:
```python
while not shutdown_event.is_set():
    await dispatch_cycle()
    await asyncio.sleep(10)
await graceful_shutdown()
```

## 约束
- 修改现有 dispatch-controller.py
- SIGTERM 和 SIGINT 触发优雅关闭
- 最多等 30 秒完成当前操作
- 不改任务调度逻辑
- 不改 DB schema

## 验收标准
- [ ] kill <pid> 触发优雅关闭（不是立即死亡）
- [ ] 关闭日志记录 "initiating graceful shutdown"
- [ ] 运行中的任务状态不丢失
- [ ] DB 连接正确关闭（无锁残留）

## 不要做
- 不改调度算法
- 不改 worker 通信协议
- 不改 task-wrapper.sh
