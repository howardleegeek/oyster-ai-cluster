#!/usr/bin/env python3
"""
Agent Communication System - Agent 间通信与协作

功能:
- 消息发送/接收
- 任务委托
- 广播
- 消息队列管理
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict

# 配置
DISPATCH_DIR = Path.home() / "dispatch"
MAILBOX_DIR = DISPATCH_DIR / "agent_mailbox"


def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [AgentComm] {msg}", flush=True)


@dataclass
class Message:
    """Agent 消息"""

    id: str
    from_agent: str
    to_agent: str  # "*" for broadcast
    subject: str
    body: str
    timestamp: str
    status: str = "pending"  # pending, read, processed
    task_id: Optional[str] = None
    priority: int = 1


class AgentMailbox:
    """Agent 邮箱 - 消息队列管理"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.mailbox_dir = MAILBOX_DIR / agent_id
        self.mailbox_dir.mkdir(parents=True, exist_ok=True)
        self.inbox = self.mailbox_dir / "inbox"
        self.outbox = self.mailbox_dir / "outbox"
        self.inbox.mkdir(exist_ok=True)
        self.outbox.mkdir(exist_ok=True)

    def send_message(
        self,
        to_agent: str,
        subject: str,
        body: str,
        task_id: Optional[str] = None,
        priority: int = 1,
    ) -> str:
        """发送消息到其他 Agent"""
        msg_id = f"{self.agent_id}_{to_agent}_{int(time.time() * 1000)}"

        msg = Message(
            id=msg_id,
            from_agent=self.agent_id,
            to_agent=to_agent,
            subject=subject,
            body=body,
            timestamp=datetime.now().isoformat(),
            task_id=task_id,
            priority=priority,
        )

        # 保存到目标 Agent 的 inbox
        if to_agent == "*":
            # 广播 - 保存到所有 Agent
            for agent_dir in MAILBOX_DIR.iterdir():
                if agent_dir.is_dir() and agent_dir.name != self.agent_id:
                    msg_file = agent_dir / "inbox" / f"{msg_id}.json"
                    msg_file.write_text(json.dumps(asdict(msg), indent=2))
        else:
            target_dir = MAILBOX_DIR / to_agent / "inbox"
            target_dir.mkdir(parents=True, exist_ok=True)
            msg_file = target_dir / f"{msg_id}.json"
            msg_file.write_text(json.dumps(asdict(msg), indent=2))

        # 保存到自己的 outbox
        out_file = self.outbox / f"{msg_id}.json"
        out_file.write_text(json.dumps(asdict(msg), indent=2))

        log(f"Message sent: {self.agent_id} -> {to_agent}: {subject}")
        return msg_id

    def receive_messages(self, limit: int = 10) -> List[Message]:
        """接收待处理消息"""
        messages = []
        for msg_file in sorted(
            self.inbox.glob("*.json"), key=lambda x: x.stat().st_mtime
        ):
            try:
                data = json.loads(msg_file.read_text())
                if data.get("status") == "pending":
                    messages.append(Message(**data))
                    if len(messages) >= limit:
                        break
            except:
                continue
        return messages

    def mark_read(self, msg_id: str):
        """标记消息为已读"""
        msg_file = self.inbox / f"{msg_id}.json"
        if msg_file.exists():
            try:
                data = json.loads(msg_file.read_text())
                data["status"] = "read"
                msg_file.write_text(json.dumps(data, indent=2))
            except:
                pass

    def mark_processed(self, msg_id: str):
        """标记消息为已处理"""
        msg_file = self.inbox / f"{msg_id}.json"
        if msg_file.exists():
            try:
                data = json.loads(msg_file.read_text())
                data["status"] = "processed"
                # 移动到 processed 目录
                processed_dir = self.mailbox_dir / "processed"
                processed_dir.mkdir(exist_ok=True)
                msg_file.rename(processed_dir / f"{msg_id}.json")
            except:
                pass

    def get_unread_count(self) -> int:
        """获取未读消息数"""
        count = 0
        for msg_file in self.inbox.glob("*.json"):
            try:
                data = json.loads(msg_file.read_text())
                if data.get("status") == "pending":
                    count += 1
            except:
                continue
        return count


class AgentComm:
    """Agent 通信管理器"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.mailbox = AgentMailbox(agent_id)

    def post_message(self, to_agent: str, subject: str, body: str, **kwargs) -> str:
        """发送消息"""
        return self.mailbox.send_message(to_agent, subject, body, **kwargs)

    def broadcast_message(self, subject: str, body: str, **kwargs) -> str:
        """广播消息到所有 Agent"""
        return self.mailbox.send_message("*", subject, body, **kwargs)

    def receive_messages(self, limit: int = 10) -> List[Message]:
        """接收消息"""
        return self.mailbox.receive_messages(limit)

    def delegate_task(self, target_agent: str, task_spec: Dict[str, Any]) -> str:
        """委托任务给其他 Agent"""
        task_id = task_spec.get("task_id", f"delegated_{int(time.time())}")
        body = json.dumps(task_spec)
        return self.post_message(
            target_agent,
            subject=f"Task Delegation: {task_id}",
            body=body,
            task_id=task_id,
            priority=2,
        )

    def get_inbox_summary(self) -> Dict:
        """获取收件箱摘要"""
        messages = self.receive_messages(limit=100)
        return {
            "agent_id": self.agent_id,
            "unread_count": len(messages),
            "recent_subjects": [m.subject for m in messages[:5]],
        }


def list_all_agents() -> List[str]:
    """列出所有 Agent"""
    if not MAILBOX_DIR.exists():
        return []
    return [d.name for d in MAILBOX_DIR.iterdir() if d.is_dir()]


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Agent Communication")
    parser.add_argument("--from", dest="from_agent", required=True)
    parser.add_argument("--to", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--body", default="")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--broadcast", action="store_true")

    args = parser.parse_args()

    if args.list:
        print("All Agents:", list_all_agents())
        return

    comm = AgentComm(args.from_agent)

    if args.broadcast:
        comm.broadcast_message(args.subject, args.body)
    else:
        comm.post_message(args.to, args.subject, args.body)

    print("Message sent!")


if __name__ == "__main__":
    main()
