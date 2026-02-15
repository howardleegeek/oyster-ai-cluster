#!/usr/bin/env python3
"""
Agent Memory System - 跨任务上下文记忆

功能:
- 长期记忆存储 (TTL 支持)
- 上下文搜索
- 任务链记忆继承
- 跨 Agent 记忆共享
"""

import os
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

# 配置
DISPATCH_DIR = Path.home() / "dispatch"
MEMORY_DIR = DISPATCH_DIR / "memory"
DEFAULT_TTL = 86400  # 24 小时


def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [AgentMemory] {msg}", flush=True)


class MemoryStore:
    """记忆存储"""

    def __init__(self, agent_id: str = "global"):
        self.agent_id = agent_id
        self.agent_dir = MEMORY_DIR / agent_id
        self.agent_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.agent_dir / "index.json"
        self.load_index()

    def load_index(self):
        """加载索引"""
        if self.index_file.exists():
            try:
                self.index = json.loads(self.index_file.read_text())
            except:
                self.index = {"memories": [], "tags": {}}
        else:
            self.index = {"memories": [], "tags": {}}

    def save_index(self):
        """保存索引"""
        self.index_file.write_text(json.dumps(self.index, indent=2))

    def store(
        self,
        key: str,
        value: Any,
        ttl: int = DEFAULT_TTL,
        tags: List[str] = None,
        metadata: Dict = None,
    ) -> str:
        """存储记忆"""
        memory_id = hashlib.md5(f"{key}_{time.time()}".encode()).hexdigest()[:12]

        memory = {
            "id": memory_id,
            "key": key,
            "value": value,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(seconds=ttl)).isoformat(),
            "tags": tags or [],
            "metadata": metadata or {},
            "agent_id": self.agent_id,
            "access_count": 0,
            "last_accessed": datetime.now().isoformat(),
        }

        # 保存记忆文件
        memory_file = self.agent_dir / f"{memory_id}.json"
        memory_file.write_text(json.dumps(memory, indent=2))

        # 更新索引
        self.index["memories"].append(
            {
                "id": memory_id,
                "key": key,
                "tags": memory["tags"],
                "created_at": memory["created_at"],
            }
        )

        for tag in memory["tags"]:
            if tag not in self.index["tags"]:
                self.index["tags"][tag] = []
            self.index["tags"][tag].append(memory_id)

        self.save_index()
        log(f"Stored memory: {key} ({memory_id})")
        return memory_id

    def recall(self, key: str) -> Optional[Any]:
        """召回记忆"""
        for mem_info in self.index["memories"]:
            if mem_info["key"] == key:
                memory_file = self.agent_dir / f"{mem_info['id']}.json"
                if memory_file.exists():
                    try:
                        memory = json.loads(memory_file.read_text())
                        # 检查过期
                        if (
                            datetime.fromisoformat(memory["expires_at"])
                            < datetime.now()
                        ):
                            self.forget(key)
                            return None
                        # 更新访问次数
                        memory["access_count"] += 1
                        memory["last_accessed"] = datetime.now().isoformat()
                        memory_file.write_text(json.dumps(memory, indent=2))
                        return memory["value"]
                    except:
                        return None
        return None

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """搜索记忆"""
        results = []
        query_lower = query.lower()

        for mem_info in self.index["memories"]:
            memory_file = self.agent_dir / f"{mem_info['id']}.json"
            if memory_file.exists():
                try:
                    memory = json.loads(memory_file.read_text())
                    # 检查过期
                    if datetime.fromisoformat(memory["expires_at"]) < datetime.now():
                        continue
                    # 搜索匹配
                    if (
                        query_lower in mem_info["key"].lower()
                        or query_lower in str(memory.get("value", "")).lower()
                        or any(
                            query_lower in tag.lower() for tag in memory.get("tags", [])
                        )
                    ):
                        results.append(
                            {
                                "key": mem_info["key"],
                                "value": memory["value"][:500],  # 限制长度
                                "tags": memory["tags"],
                                "created_at": memory["created_at"],
                                "id": mem_info["id"],
                            }
                        )
                        if len(results) >= limit:
                            break
                except:
                    continue
        return results

    def forget(self, key: str) -> bool:
        """删除记忆"""
        for mem_info in list(self.index["memories"]):
            if mem_info["key"] == key:
                memory_file = self.agent_dir / f"{mem_info['id']}.json"
                if memory_file.exists():
                    memory_file.unlink()

                self.index["memories"].remove(mem_info)

                # 从 tags 中移除
                for tag, ids in list(self.index["tags"].items()):
                    if mem_info["id"] in ids:
                        ids.remove(mem_info["id"])

                self.save_index()
                log(f"Forgot: {key}")
                return True
        return False

    def cleanup_expired(self):
        """清理过期记忆"""
        count = 0
        for mem_info in list(self.index["memories"]):
            memory_file = self.agent_dir / f"{mem_info['id']}.json"
            if memory_file.exists():
                try:
                    memory = json.loads(memory_file.read_text())
                    if datetime.fromisoformat(memory["expires_at"]) < datetime.now():
                        memory_file.unlink()
                        self.index["memories"].remove(mem_info)
                        count += 1
                except:
                    pass
        if count > 0:
            self.save_index()
            log(f"Cleaned up {count} expired memories")
        return count


class AgentMemory:
    """Agent 记忆管理器 - 支持跨任务上下文"""

    def __init__(self, agent_id: str = None):
        self.agent_id = agent_id or "global"
        self.store = MemoryStore(self.agent_id)
        self.task_memory: Dict[str, Any] = {}

    def store(self, key: str, value: Any, ttl: int = DEFAULT_TTL, **kwargs):
        """存储记忆 (代理到 store)"""
        return self.store.store(key, value, ttl, **kwargs)

    def recall(self, key: str) -> Optional[Any]:
        """召回记忆"""
        return self.store.recall(key)

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """搜索记忆"""
        return self.store.search(query, limit)

    def forget(self, key: str) -> bool:
        """删除记忆"""
        return self.store.forget(key)

    def get_context(self, task_id: str = None) -> Dict:
        """获取当前任务相关上下文"""
        context = {
            "recent_memories": [],
            "task_related": [],
        }

        # 获取最近的记忆
        memories = self.store.index.get("memories", [])
        for mem in memories[-5:]:
            context["recent_memories"].append(
                {
                    "key": mem["key"],
                    "tags": mem["tags"],
                }
            )

        # 如果有 task_id，获取任务相关记忆
        if task_id:
            task_memories = self.search(f"task:{task_id}", limit=5)
            context["task_related"] = task_memories

        return context

    def inherit_from(self, parent_task_id: str, keys: List[str] = None):
        """从父任务继承记忆"""
        parent_store = MemoryStore("global")

        if keys:
            # 只继承指定 keys
            for key in keys:
                value = parent_store.recall(key)
                if value:
                    self.store(
                        f"inherited:{key}", value, tags=["inherited", parent_task_id]
                    )
        else:
            # 继承所有相关记忆
            results = parent_store.search(f"task:{parent_task_id}")
            for r in results:
                self.store(
                    f"inherited:{r['key']}",
                    r["value"],
                    tags=["inherited", parent_task_id],
                )

        log(f"Inherited memories from task: {parent_task_id}")

    def store_task_result(self, task_id: str, result: Any, summary: str = ""):
        """存储任务结果到记忆"""
        self.store(
            f"task:{task_id}",
            {"result": result, "summary": summary},
            tags=["task", task_id],
            metadata={"task_id": task_id},
        )

    def get_task_result(self, task_id: str) -> Optional[Any]:
        """获取任务结果"""
        return self.recall(f"task:{task_id}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Agent Memory")
    parser.add_argument("--agent", default="global")
    parser.add_argument("--store", nargs=3, metavar=("KEY", "VALUE", "TTL"))
    parser.add_argument("--recall", metavar="KEY")
    parser.add_argument("--search", metavar="QUERY")
    parser.add_argument("--forget", metavar="KEY")
    parser.add_argument("--cleanup", action="store_true")
    parser.add_argument("--context", action="store_true")

    args = parser.parse_args()
    memory = AgentMemory(args.agent)

    if args.store:
        key, value, ttl = args.store
        memory.store(key, value, int(ttl))
        print(f"Stored: {key}")

    elif args.recall:
        result = memory.recall(args.recall)
        print(f"Recall: {result}")

    elif args.search:
        results = memory.search(args.search)
        for r in results:
            print(f"- {r['key']}: {r['value'][:100]}...")

    elif args.forget:
        memory.forget(args.forget)
        print(f"Forgotten: {args.forget}")

    elif args.cleanup:
        count = memory.store.cleanup_expired()
        print(f"Cleaned up: {count} memories")

    elif args.context:
        ctx = memory.get_context()
        print(json.dumps(ctx, indent=2))


if __name__ == "__main__":
    main()
