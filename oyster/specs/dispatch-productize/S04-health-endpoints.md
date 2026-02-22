---
task_id: S04-health-endpoints
project: dispatch-productize
priority: 1
estimated_minutes: 30
depends_on: ["S01-db-abstraction"]
modifies: ["oyster/infra/dispatch/health.py"]
executor: glm
---

## 目标

创建可嵌入任何 daemon 的 HTTP health endpoint 模块，暴露 `/health` 和 `/metrics`。

## 实现

创建 `oyster/infra/dispatch/health.py`：

```python
"""
轻量级 Health HTTP Server，嵌入任何 daemon。
用法：
    from health import HealthServer
    hs = HealthServer(port=8090, name="guardian")
    hs.start()  # 后台线程
    # ... daemon 主循环 ...
    hs.heartbeat()  # 每个 cycle 调用
"""
import threading
import time
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            # 心跳超过 2x interval = unhealthy
            age = time.time() - self.server.last_heartbeat
            healthy = age < self.server.unhealthy_after
            status = 200 if healthy else 503
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "healthy" if healthy else "unhealthy",
                "service": self.server.service_name,
                "uptime": int(time.time() - self.server.start_time),
                "last_heartbeat_age": int(age),
                "cycle_count": self.server.cycle_count,
                "pid": os.getpid()
            }).encode())
        elif self.path == "/metrics":
            # Prometheus 格式
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            lines = [
                f'dispatch_daemon_up{{service="{self.server.service_name}"}} {1 if healthy else 0}',
                f'dispatch_daemon_uptime{{service="{self.server.service_name}"}} {int(time.time() - self.server.start_time)}',
                f'dispatch_daemon_cycles{{service="{self.server.service_name}"}} {self.server.cycle_count}',
                f'dispatch_daemon_heartbeat_age{{service="{self.server.service_name}"}} {int(age)}',
            ]
            self.wfile.write("\n".join(lines).encode())

    def log_message(self, format, *args):
        pass  # 静默 HTTP 日志

class HealthServer:
    def __init__(self, port, name, unhealthy_after=600):
        self.port = port
        self.name = name
        self.server = HTTPServer(("0.0.0.0", port), HealthHandler)
        self.server.service_name = name
        self.server.last_heartbeat = time.time()
        self.server.start_time = time.time()
        self.server.cycle_count = 0
        self.server.unhealthy_after = unhealthy_after

    def start(self):
        t = threading.Thread(target=self.server.serve_forever, daemon=True)
        t.start()

    def heartbeat(self):
        self.server.last_heartbeat = time.time()
        self.server.cycle_count += 1
```

### 端口分配

| Service | Port |
|---------|------|
| dispatch (controller) | 8090 |
| guardian | 8091 |
| reaper | 8092 |
| factory | 8093 |

## 约束

- 纯标准库（http.server + threading），无额外依赖
- 后台 daemon 线程，不阻塞主循环
- `/health` 返回 200（健康）或 503（不健康）
- 不健康定义：heartbeat 超过 `unhealthy_after` 秒（默认 600s = 10min）

## 验收标准

- [ ] `curl localhost:8091/health` 返回 JSON 状态
- [ ] daemon 卡住时 `/health` 返回 503
- [ ] `/metrics` 输出 Prometheus 格式
- [ ] 不影响 daemon 主循环性能

## 不要做

- 不嵌入到现有 daemon（后续 spec 做）
- 不加认证
- 不用 Flask/FastAPI
