#!/usr/bin/env python3
"""
Session Agent - 每个 Session 的 ClawBot 分身

职责:
- 理解当前 Session 的意图
- 记住上下文 (之前做了什么)
- 协调任务分发
- 决策执行方案
"""

import os
import sys
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import subprocess

# 配置
DISPATCH_DIR = Path.home() / "Downloads" / "dispatch"
SPECS_DIR = Path.home() / "Downloads" / "specs"
SESSION_DIR = DISPATCH_DIR / "sessions"


class SessionAgent:
    """Session-Scoped ClawBot 分身"""

    def __init__(self, session_id: str = None, project: str = None):
        self.session_id = session_id or str(uuid.uuid4())[:8]
        self.project = project
        self.created_at = datetime.now().isoformat()

        # Session 上下文
        self.context = {
            "session_id": self.session_id,
            "project": project,
            "history": [],  # 执行历史
            "pending_tasks": [],  # 待处理任务
            "completed_tasks": [],  # 已完成任务
            "current_intent": None,  # 当前意图
        }

        # 确保 session 目录存在
        SESSION_DIR.mkdir(parents=True, exist_ok=True)

        # 加载已有上下文
        self._load_context()

        print(f"[SessionAgent {self.session_id}] Initialized for project: {project}")

    def _load_context(self):
        """加载已有上下文"""
        session_file = SESSION_DIR / f"{self.session_id}.json"
        if session_file.exists():
            try:
                self.context = json.loads(session_file.read_text())
                print(f"[SessionAgent {self.session_id}] Loaded existing context")
            except:
                pass

    def _save_context(self):
        """保存上下文"""
        session_file = SESSION_DIR / f"{self.session_id}.json"
        session_file.write_text(json.dumps(self.context, indent=2, ensure_ascii=False))

    def set_intent(self, intent: str):
        """设置当前 Session 的意图"""
        self.context["current_intent"] = intent
        self.context["history"].append(
            {
                "type": "intent_set",
                "content": intent,
                "timestamp": datetime.now().isoformat(),
            }
        )
        self._save_context()
        print(f"[SessionAgent {self.session_id}] Intent set: {intent}")

    def understand_intent(self, intent: str) -> Dict[str, Any]:
        """理解意图 - 决定执行方案"""

        # 读取项目 CLAUDE.md
        claude_md = ""
        if self.project:
            for p in [
                Path.home() / "Downloads" / self.project / "CLAUDE.md",
                SPECS_DIR / self.project / "CLAUDE.md",
            ]:
                if p.exists():
                    claude_md = p.read_text()[:3000]
                    break

        # 构建理解 prompt
        prompt = f"""Analyze this intent and create an execution plan.

## Project Context
{claude_md}

## Intent
{intent}

## Your Session Context
{json.dumps(self.context.get("history", [])[-3:], indent=2)}

## Output JSON with:
{{
    "intent_summary": "简短总结意图",
    "execution_mode": "single|parallel|sequential",
    "tasks": [
        {{"id": "S001", "description": "任务描述", "priority": 1}}
    ],
    "dependencies": ["task_id dependencies"],
    "estimated_duration": "minutes estimate",
    "risks": ["potential issues"]
}}

Output ONLY JSON, no explanations.
"""

        # 调用 LLM 理解 (fallback to simple parsing)
        try:
            result = subprocess.run(
                ["~/bin/mm", prompt] if Path("~/bin/mm").exists() else ["echo", prompt],
                capture_output=True,
                text=True,
                timeout=30,
            )
            plan = self._parse_plan(result.stdout or prompt)
        except:
            plan = self._simple_parse(intent)

        self.set_intent(intent)
        self.context["execution_plan"] = plan
        self._save_context()

        return plan

    def _parse_plan(self, response: str) -> Dict:
        """解析 LLM 响应"""
        # 简单 JSON 提取
        try:
            import re

            json_match = re.search(r"\{[\s\S]*\}", response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        return self._simple_parse(response)

    def _simple_parse(self, intent: str) -> Dict:
        """简单解析意图"""
        intent_lower = intent.lower()

        # 推断执行模式
        if "同时" in intent or "并行" in intent:
            mode = "parallel"
        elif "先" in intent or "然后" in intent:
            mode = "sequential"
        else:
            mode = "single"

        # 生成任务
        task_id = f"S{datetime.now().strftime('%m%d')}-001"

        return {
            "intent_summary": intent[:100],
            "execution_mode": mode,
            "tasks": [{"id": task_id, "description": intent, "priority": 2}],
            "estimated_duration": "10-30 minutes",
            "risks": [],
        }

    def add_task(self, task_id: str, description: str):
        """添加任务到 Session"""
        self.context["pending_tasks"].append(
            {
                "id": task_id,
                "description": description,
                "added_at": datetime.now().isoformat(),
            }
        )
        self._save_context()

    def complete_task(self, task_id: str, result: str = None):
        """标记任务完成"""
        # 从 pending 移到 completed
        pending = self.context["pending_tasks"]
        self.context["pending_tasks"] = [t for t in pending if t["id"] != task_id]

        self.context["completed_tasks"].append(
            {
                "id": task_id,
                "completed_at": datetime.now().isoformat(),
                "result": result,
            }
        )

        self.context["history"].append(
            {
                "type": "task_completed",
                "task_id": task_id,
                "timestamp": datetime.now().isoformat(),
            }
        )
        self._save_context()

    def get_status(self) -> Dict:
        """获取 Session 状态"""
        return {
            "session_id": self.session_id,
            "project": self.project,
            "intent": self.context.get("current_intent"),
            "pending": len(self.context["pending_tasks"]),
            "completed": len(self.context["completed_tasks"]),
            "history_count": len(self.context["history"]),
        }

    def run_dispatch(self, project: str = None, task_id: str = None):
        """运行 dispatch"""
        proj = project or self.project
        if not proj:
            print("[SessionAgent] No project specified")
            return

        cmd = ["python3", str(DISPATCH_DIR / "dispatch.py"), "start", proj]

        if task_id:
            # 只运行特定任务
            print(f"[SessionAgent] Running task: {task_id}")
        else:
            print(f"[SessionAgent] Starting dispatch for: {proj}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            print(result.stdout)
            return result.returncode == 0
        except Exception as e:
            print(f"[SessionAgent] Dispatch error: {e}")
            return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Session Agent - ClawBot分身")
    parser.add_argument("--init", help="Initialize new session with project")
    parser.add_argument("--session", help="Resume existing session")
    parser.add_argument("--intent", help="Set intent for session")
    parser.add_argument("--status", action="store_true", help="Show session status")
    parser.add_argument("--run", help="Run dispatch for project")

    args = parser.parse_args()

    if args.init:
        agent = SessionAgent(project=args.init)
        print(f"Created new session: {agent.session_id}")

    elif args.session:
        agent = SessionAgent(session_id=args.session)
        print(f"Resumed session: {agent.session_id}")

    elif args.intent:
        # 从参数或读取
        if " " in args.intent or not Path(args.intent).exists():
            intent = args.intent
        else:
            intent = Path(args.intent).read_text()

        agent = SessionAgent(project="clawmarketing")
        plan = agent.understand_intent(intent)
        print(f"\n=== Execution Plan ===")
        print(json.dumps(plan, indent=2, ensure_ascii=False))

    elif args.status:
        agent = SessionAgent()
        print(json.dumps(agent.get_status(), indent=2))

    elif args.run:
        agent = SessionAgent(project=args.run)
        agent.run_dispatch()

    else:
        # Interactive mode
        print("Session Agent Interactive Mode")
        print("Commands: --init, --session, --intent, --status, --run")

        # 创建默认 session
        agent = SessionAgent(project="clawmarketing")
        print(f"Session: {agent.session_id}")
        print(f"Status: {json.dumps(agent.get_status(), indent=2)}")


if __name__ == "__main__":
    main()
