"""
Worker Daemon 配置
"""

import os
import socket

# 节点配置
# Use hostname, but strip GCP-style suffixes (e.g. "glm-node-2.us-west1-b.c.xxx.internal" → "glm-node-2")
_raw_hostname = os.environ.get("NODE_ID", socket.gethostname())
NODE_ID = _raw_hostname.split(".")[0] if "." in _raw_hostname else _raw_hostname
NODE_TAGS = os.environ.get("NODE_TAGS", "glm,codex").split(",")

# 控制平面地址（通过 Tailscale 内网访问）
CONTROLLER_URL = os.environ.get("CONTROLLER_URL", "http://100.95.165.3:8080")

# 并发控制
MAX_SLOTS = int(os.environ.get("MAX_SLOTS", "8"))
HEARTBEAT_INTERVAL = int(os.environ.get("HEARTBEAT_INTERVAL", "15"))

# 任务执行
TASK_TIMEOUT = int(os.environ.get("TASK_TIMEOUT", "600"))  # 默认 10 分钟
CLEANUP_TIMEOUT = int(os.environ.get("CLEANUP_TIMEOUT", "30"))  # 清理超时

# Worker HTTP 服务
WORKER_HOST = os.environ.get("WORKER_HOST", "0.0.0.0")
WORKER_PORT = int(os.environ.get("WORKER_PORT", "8081"))

# 日志
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
