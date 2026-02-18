"""
Worker Daemon - 主服务
提供 HTTP 接口给 Controller 调用
"""

import os
import sys
import json
import time
import asyncio
import logging
import subprocess
import traceback
from pathlib import Path
from datetime import datetime
from aiohttp import web

# Monkey-patch aiohttp tcp_keepalive to avoid OSError on some macOS + Python combos
# where setsockopt(SO_KEEPALIVE) fails with EINVAL on certain socket types.
try:
    import aiohttp.tcp_helpers as _tcp_helpers
    import aiohttp.web_protocol as _web_protocol

    _noop_keepalive = lambda transport: None
    _tcp_helpers.tcp_keepalive = _noop_keepalive
    _web_protocol.tcp_keepalive = _noop_keepalive
except Exception:
    pass
import psutil

import config
import protocol
from runner import TaskRunner

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class WorkerDaemon:
    """Worker Daemon 主类"""

    def __init__(self):
        self.node_id = config.NODE_ID
        self.node_tags = config.NODE_TAGS
        self.controller_url = config.CONTROLLER_URL

        # 组件
        self.runner = TaskRunner(
            task_timeout=config.TASK_TIMEOUT, cleanup_timeout=config.CLEANUP_TIMEOUT
        )

        # 状态
        self.slots_free = config.MAX_SLOTS
        self.max_slots = config.MAX_SLOTS
        self.heartbeat_task: asyncio.Task | None = None
        self.current_tasks: dict[str, dict] = {}

        logger.info(
            f"WorkerDaemon initialized: node_id={self.node_id}, slots={self.max_slots}"
        )

    # ========== HTTP 路由 ==========

    async def handle_poll(self, request: web.Request) -> web.Response:
        """
        POST /v1/poll
        Worker 从 Controller 拉取任务
        """
        try:
            data = await request.json()
        except:
            data = {}

        node_id = data.get("node_id", self.node_id)
        slots_free = data.get("slots_free", self.slots_free)
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent

        # 更新状态
        self.slots_free = min(slots_free, self.max_slots)

        # 检查是否有运行中的任务
        running = self.runner.get_running_tasks()

        response = {
            "node_id": self.node_id,
            "status": "OK",
            "slots_free": self._true_slots_free(),
            "max_slots": self.max_slots,
            "cpu": cpu,
            "mem": mem,
            "running_tasks": len(running),
            "node_tags": self.node_tags,
        }

        return web.json_response(response)

    async def handle_execute(self, request: web.Request) -> web.Response:
        """
        POST /v1/execute
        Controller 派发任务给 Worker

        Supports spec_content and setup_commands from Controller:
        - spec_content: enriched spec markdown, written to cwd/spec.md
        - setup_commands: list of shell commands to run before main command (e.g. mkdir)
        """
        try:
            task_data = await request.json()
        except:
            return web.json_response({"error": "Invalid JSON"}, status=400)

        task_id = task_data.get("task_id")
        command = task_data.get("command")
        timeout = task_data.get("timeout", config.TASK_TIMEOUT)
        cwd = task_data.get("cwd", "/home/user")
        env = task_data.get("env", {})
        lease_owner = task_data.get("lease_owner", "")
        spec_content = task_data.get("spec_content")
        setup_commands = task_data.get("setup_commands", [])

        if not task_id or not command:
            return web.json_response(
                {"error": "task_id and command are required"}, status=400
            )

        # 检查 slot (ground truth: actual process count)
        if self._true_slots_free() <= 0:
            return web.json_response(
                {"error": "No slots available", "slots_free": 0}, status=429
            )

        # Expand ~ in cwd
        cwd = os.path.expanduser(cwd)

        # Run setup commands (mkdir, etc.)
        for setup_cmd in setup_commands:
            try:
                expanded = os.path.expanduser(setup_cmd)
                subprocess.run(expanded, shell=True, check=True, timeout=10)
            except Exception as e:
                logger.warning(f"[{task_id}] Setup command failed: {setup_cmd} -> {e}")

        # Write spec_content to cwd/spec.md
        if spec_content:
            try:
                os.makedirs(cwd, exist_ok=True)
                spec_path = os.path.join(cwd, "spec.md")
                with open(spec_path, "w") as f:
                    f.write(spec_content)
                logger.info(
                    f"[{task_id}] Wrote spec ({len(spec_content)} bytes) to {spec_path}"
                )
            except Exception as e:
                logger.error(f"[{task_id}] Failed to write spec: {e}")
                return web.json_response(
                    {"error": f"Failed to write spec: {e}"}, status=500
                )

        # 扣减 slot
        self.slots_free -= 1
        self.current_tasks[task_id] = {
            "command": command,
            "start_time": datetime.utcnow().isoformat(),
            "lease_owner": lease_owner,
        }

        logger.info(f"[{task_id}] Executing: {command[:80]}")

        # 异步执行
        asyncio.create_task(
            self._execute_and_report(task_id, command, cwd, env, timeout, lease_owner)
        )

        return web.json_response(
            {"status": "ACCEPTED", "task_id": task_id, "slots_free": self.slots_free}
        )

    async def _execute_and_report(
        self,
        task_id: str,
        command: str,
        cwd: str,
        env: dict,
        timeout: int,
        lease_owner: str,
    ):
        """执行任务并上报结果"""
        try:
            # 执行任务
            result = await self.runner.execute(
                task_id, command, cwd, env, timeout, lease_owner
            )

            # 上报结果到 Controller
            await self._report_to_controller(task_id, result)

        except Exception as e:
            logger.error(f"[{task_id}] Execute error: {e}")
            result = protocol.TaskResult.failure(task_id, str(e))
            await self._report_to_controller(task_id, result)

        finally:
            # 释放 slot
            self.slots_free += 1
            self.current_tasks.pop(task_id, None)

    async def _report_to_controller(self, task_id: str, result: protocol.TaskResult):
        """上报任务结果到 Controller"""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                url = f"{config.CONTROLLER_URL}/v1/task_report"
                payload = {
                    "node_id": self.node_id,
                    "task_id": task_id,
                    "status": result.status,
                    "ok": result.ok,
                    "result": result.to_json(),
                    "timestamp": result.timestamp,
                }
                async with session.post(
                    url, json=payload, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        logger.info(
                            f"[{task_id}] Reported to controller: {result.status}"
                        )
                    else:
                        logger.warning(f"[{task_id}] Failed to report: {resp.status}")
        except Exception as e:
            logger.error(f"[{task_id}] Report error: {e}")

    async def handle_heartbeat(self, request: web.Request) -> web.Response:
        """
        POST /v1/heartbeat
        Worker 主动心跳
        """
        try:
            data = await request.json()
        except:
            data = {}

        task_id = data.get("task_id")
        status = data.get("status", "RUNNING")
        progress = data.get("progress", 0.0)

        # 更新任务状态
        if task_id and task_id in self.current_tasks:
            self.current_tasks[task_id]["status"] = status
            self.current_tasks[task_id]["progress"] = progress

        running = self.runner.get_running_tasks()

        response = {
            "node_id": self.node_id,
            "status": "OK",
            "slots_free": self._true_slots_free(),
            "max_slots": self.max_slots,
            "running_tasks": running,
            "timestamp": datetime.utcnow().isoformat(),
        }

        return web.json_response(response)

    async def handle_kill(self, request: web.Request) -> web.Response:
        """
        POST /v1/kill
        Controller 请求杀死任务
        """
        try:
            data = await request.json()
        except:
            return web.json_response({"error": "Invalid JSON"}, status=400)

        task_id = data.get("task_id")
        if not task_id:
            return web.json_response({"error": "task_id required"}, status=400)

        killed = self.runner.kill_task(task_id)

        if killed:
            self.slots_free += 1
            self.current_tasks.pop(task_id, None)

        return web.json_response({"task_id": task_id, "killed": killed})

    def _actual_running_count(self) -> int:
        """Ground truth: count actual live processes in runner, not the in-memory counter.
        This prevents slot leaks when processes exit without hitting the finally block."""
        # runner.running_tasks only contains tasks with live Popen handles
        # Also prune any entries whose process has already exited
        dead = [
            tid for tid, rt in self.runner.running_tasks.items()
            if rt.process.poll() is not None
        ]
        for tid in dead:
            self.runner.running_tasks.pop(tid, None)
            self.current_tasks.pop(tid, None)
            logger.warning(f"[slot_sync] Pruned dead process for task {tid}")
        return len(self.runner.running_tasks)

    def _true_slots_free(self) -> int:
        """Slots free based on actual process count, not the counter."""
        return max(self.max_slots - self._actual_running_count(), 0)

    async def handle_status(self, request: web.Request) -> web.Response:
        """GET /v1/status - 获取 Worker 状态 (ground-truth based)"""
        # Sync the in-memory counter to match reality
        actual = self._actual_running_count()
        if self.slots_free != self.max_slots - actual:
            logger.warning(
                f"[slot_sync] Counter drift detected: counter says {self.slots_free} free, "
                f"actual processes={actual}, correcting to {self.max_slots - actual}"
            )
            self.slots_free = self.max_slots - actual

        running = self.runner.get_running_tasks()

        # Serialize current_tasks safely (convert any datetime objects to strings)
        safe_tasks = {}
        for tid, info in self.current_tasks.items():
            safe_info = {}
            for k, v in info.items():
                if isinstance(v, datetime):
                    safe_info[k] = v.isoformat()
                else:
                    safe_info[k] = v
            safe_tasks[tid] = safe_info

        return web.json_response(
            {
                "node_id": self.node_id,
                "node_tags": self.node_tags,
                "slots_free": self._true_slots_free(),
                "max_slots": self.max_slots,
                "cpu": psutil.cpu_percent(),
                "mem": psutil.virtual_memory().percent,
                "running_tasks": running,
                "current_tasks": safe_tasks,
            }
        )

    async def handle_metrics(self, request: web.Request) -> web.Response:
        """GET /v1/metrics - Prometheus 格式指标"""
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        metrics = f"""# HELP worker_slots_free Free task slots
# TYPE worker_slots_free gauge
worker_slots_free {self.slots_free}

# HELP worker_slots_max Maximum task slots
# TYPE worker_slots_max gauge
worker_slots_max {self.max_slots}

# HELP worker_cpu_usage CPU usage percentage
# TYPE worker_cpu_usage gauge
worker_cpu_usage {cpu}

# HELP worker_memory_usage Memory usage percentage
# TYPE worker_memory_usage gauge
worker_memory_usage {mem.percent}

# HELP worker_disk_usage Disk usage percentage
# TYPE worker_disk_usage gauge
worker_disk_usage {disk.percent}

# HELP worker_running_tasks Number of running tasks
# TYPE worker_running_tasks gauge
worker_running_tasks {len(self.runner.running_tasks)}
"""

        return web.Response(text=metrics, content_type="text/plain")

    # ========== Heartbeat ==========

    async def start_heartbeat(self):
        """启动心跳"""

        async def heartbeat_loop():
            while True:
                try:
                    await self._send_heartbeat()
                except Exception as e:
                    logger.error(f"Heartbeat error: {e}")
                await asyncio.sleep(config.HEARTBEAT_INTERVAL)

        self.heartbeat_task = asyncio.create_task(heartbeat_loop())
        logger.info(f"Heartbeat started: interval={config.HEARTBEAT_INTERVAL}s")

    async def _send_heartbeat(self):
        """发送心跳到 Controller"""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                url = f"{config.CONTROLLER_URL}/v1/heartbeat"
                running = self.runner.get_running_tasks()

                payload = {
                    "node_id": self.node_id,
                    "slots_free": self._true_slots_free(),
                    "max_slots": self.max_slots,
                    "cpu": psutil.cpu_percent(),
                    "mem": psutil.virtual_memory().percent,
                    "running_tasks": running,
                    "timestamp": datetime.utcnow().isoformat(),
                }

                async with session.post(
                    url, json=payload, timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status != 200:
                        logger.warning(f"Heartbeat failed: {resp.status}")
        except Exception as e:
            logger.debug(f"Heartbeat to {self.controller_url}: {e}")

    async def handle_health(self, request: web.Request) -> web.Response:
        """GET /v1/health - Rich node health data for controller and monitoring.

        Returns comprehensive health info including:
        - Resource usage (CPU, memory, disk, load)
        - Process details (running tasks, zombie count)
        - Network health (Tailscale status)
        - Uptime and version info
        - Node guardian state (if available)
        """
        import platform

        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        load1, load5, load15 = os.getloadavg() if hasattr(os, "getloadavg") else (0, 0, 0)

        # Count zombie processes
        zombie_count = 0
        try:
            for proc in psutil.process_iter(["status"]):
                if proc.info["status"] == psutil.STATUS_ZOMBIE:
                    zombie_count += 1
        except Exception:
            pass

        # Get Tailscale status
        tailscale_status = "unknown"
        tailscale_ip = ""
        try:
            ts_result = subprocess.run(
                ["tailscale", "status", "--json"],
                capture_output=True, text=True, timeout=5,
            )
            if ts_result.returncode == 0:
                ts_data = json.loads(ts_result.stdout)
                tailscale_status = ts_data.get("BackendState", "unknown")
                # Get our Tailscale IP
                self_node = ts_data.get("Self", {})
                ts_addrs = self_node.get("TailscaleIPs", [])
                tailscale_ip = ts_addrs[0] if ts_addrs else ""
            else:
                tailscale_status = "error"
        except FileNotFoundError:
            tailscale_status = "not_installed"
        except Exception:
            tailscale_status = "check_failed"

        # Read node-guardian state if available
        guardian_state = {}
        for state_path in [
            Path("/home/ubuntu/dispatch/node_state.json"),
            Path("/home/howardli/dispatch/node_state.json"),
            Path.home() / "dispatch" / "node_state.json",
        ]:
            try:
                if state_path.exists():
                    guardian_state = json.loads(state_path.read_text())
                    break
            except Exception:
                continue

        # Worker version (md5 of worker.py)
        worker_version = "unknown"
        try:
            import hashlib
            worker_file = Path(__file__).resolve()
            worker_version = hashlib.md5(worker_file.read_bytes()).hexdigest()[:8]
        except Exception:
            pass

        # Uptime
        uptime_seconds = 0
        try:
            uptime_seconds = int(time.time() - psutil.boot_time())
        except Exception:
            pass

        # Network connections count
        net_connections = 0
        try:
            net_connections = len(psutil.net_connections(kind="tcp"))
        except Exception:
            pass

        # Actual running processes
        actual_running = self._actual_running_count()
        running_tasks = self.runner.get_running_tasks()

        health = {
            "node_id": self.node_id,
            "node_tags": self.node_tags,
            "healthy": True,  # Will be set to False if degraded
            "timestamp": datetime.utcnow().isoformat(),

            # Slots
            "slots_free": self._true_slots_free(),
            "max_slots": self.max_slots,
            "actual_running": actual_running,

            # Resources
            "cpu_percent": cpu,
            "cpu_count": psutil.cpu_count(),
            "memory": {
                "total_mb": round(mem.total / (1024 * 1024)),
                "available_mb": round(mem.available / (1024 * 1024)),
                "percent": mem.percent,
            },
            "disk": {
                "total_gb": round(disk.total / (1024 ** 3), 1),
                "free_gb": round(disk.free / (1024 ** 3), 1),
                "percent": disk.percent,
            },
            "load": {
                "load1": round(load1, 2),
                "load5": round(load5, 2),
                "load15": round(load15, 2),
            },

            # Processes
            "zombie_count": zombie_count,
            "running_tasks": running_tasks,
            "net_connections": net_connections,

            # Network
            "tailscale": {
                "status": tailscale_status,
                "ip": tailscale_ip,
            },

            # System
            "uptime_seconds": uptime_seconds,
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "worker_version": worker_version,

            # Guardian state (from node-guardian.py)
            "guardian": guardian_state,
        }

        # Determine overall health
        if mem.percent > 95 or disk.percent > 95 or zombie_count > 10:
            health["healthy"] = False
            health["degraded_reason"] = []
            if mem.percent > 95:
                health["degraded_reason"].append("memory_critical")
            if disk.percent > 95:
                health["degraded_reason"].append("disk_critical")
            if zombie_count > 10:
                health["degraded_reason"].append("too_many_zombies")

        if tailscale_status not in ("Running", "not_installed"):
            health["healthy"] = False
            health.setdefault("degraded_reason", []).append("tailscale_unhealthy")

        return web.json_response(health)

    # ========== 启动 ==========

    def create_app(self) -> web.Application:
        """创建 aiohttp 应用"""
        app = web.Application()

        app.router.add_post("/v1/poll", self.handle_poll)
        app.router.add_post("/v1/execute", self.handle_execute)
        app.router.add_post("/v1/heartbeat", self.handle_heartbeat)
        app.router.add_post("/v1/kill", self.handle_kill)
        app.router.add_get("/v1/status", self.handle_status)
        app.router.add_get("/v1/metrics", self.handle_metrics)
        app.router.add_get("/v1/health", self.handle_health)

        return app


async def main():
    """主入口"""
    logger.info(f"Starting WorkerDaemon: {config.NODE_ID}")

    daemon = WorkerDaemon()

    # 启动 heartbeat
    await daemon.start_heartbeat()

    # 启动 HTTP 服务
    app = daemon.create_app()
    runner = web.AppRunner(app, keepalive_timeout=30)
    await runner.setup()

    # tcp_keepalive=False avoids OSError on some macOS + Python combos
    site = web.TCPSite(
        runner, config.WORKER_HOST, config.WORKER_PORT, shutdown_timeout=5.0
    )
    await site.start()

    logger.info(f"WorkerDaemon listening on {config.WORKER_HOST}:{config.WORKER_PORT}")

    # 保持运行
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
