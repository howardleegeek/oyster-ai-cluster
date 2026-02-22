---
task_id: S09-integrate-health
project: dispatch-productize
priority: 1
estimated_minutes: 30
depends_on: ["S04-health-endpoints"]
modifies: ["oyster/infra/dispatch/guardian.py", "oyster/infra/dispatch/pipeline/reaper_daemon.py", "oyster/infra/dispatch/pipeline/factory_daemon.py", "oyster/infra/dispatch/dispatch-controller.py"]
executor: glm
---

## 目标

将 health.py 的 HealthServer 嵌入所有 daemon，暴露 /health 和 /metrics 端点。

## 实现

每个 daemon 的 main() 函数开头加：

```python
from health import HealthServer

# Guardian
hs = HealthServer(port=8091, name="guardian")
hs.start()

# 在主循环每个 cycle 末尾：
hs.heartbeat()
hs.set_metric("cycle_count", cycle_count)
```

### 端口分配
- dispatch-controller: 8090（controller 本身已有 aiohttp，加 /health route）
- guardian: 8091
- reaper: 8092
- factory: 8093

### controller 特殊处理
controller 已有 aiohttp web server，直接加 route：
```python
async def handle_health(request):
    return web.json_response({"status": "healthy", "uptime": ...})
app.router.add_get("/health", handle_health)
```

## 约束

- 不改 daemon 主逻辑
- 端口冲突时 log warning 不 crash

## 验收标准

- [ ] `curl localhost:8091/health` 返回 guardian 状态
- [ ] `curl localhost:8092/health` 返回 reaper 状态
- [ ] `curl localhost:8093/health` 返回 factory 状态
- [ ] daemon 正常运行不受影响

## 不要做

- 不改 daemon 业务逻辑
- 不加认证
