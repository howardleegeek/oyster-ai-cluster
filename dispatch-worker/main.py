"""
AI Factory v3 - Worker Daemon
最小稳定实现：HTTP + slots + runner timeout killpg + heartbeat
"""

import asyncio
from worker import main

if __name__ == "__main__":
    asyncio.run(main())
