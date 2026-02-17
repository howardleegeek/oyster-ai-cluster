#!/usr/bin/env python3
"""Telegram Bot v3 - AI Powered with OpenCode Integration"""

import os
import sys
import json
import subprocess
import re
import requests
from pathlib import Path
from datetime import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Configuration
TELEGRAM_BOT_TOKEN = "8440252989:AAFYlOOMekYoVEQ6zaa8rig7KFRwDW1Om-8"
MINIMAX_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjb21wYW55X2lkIjoiNjcxNjIzNzA1NjU1MjIiLCJpYXQiOjE3MzgxNDkxNDR9.Yj1-2j9XQ3M-Qp7s2KkYvT8Y4x3X5K6Q7R8S9T0U1V2W3X4Y5Z6A7B8C9D0E1F2"
GLM_API_URL = "https://api.minimax.chat/v1/text/chatcompletion_pro"
PROJECTS = ["clawmarketing", "gem-platform", "oyster-infra", "dispatch"]
DISPATCH_PATH = str(Path.home() / "Downloads" / "dispatch")

log_file = Path(__file__).parent / "telegram_bot.log"


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def call_glm(prompt: str) -> str:
    try:
        headers = {
            "Authorization": f"Bearer {MINIMAX_API_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "GLM-4-Flash",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 512,
        }
        response = requests.post(GLM_API_URL, headers=headers, json=data, timeout=30)
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "{}")
    except Exception as e:
        log(f"GLM error: {e}")
        return "{}"


def parse_intent(text: str) -> dict:
    text_lower = text.lower()
    intent = "question"
    project = "clawmarketing"

    if any(w in text_lower for w in ["fix", "修复", "add", "添加", "implement"]):
        intent = "code_task"
    if "status" in text_lower or "状态" in text_lower:
        intent = "status"
    if "log" in text_lower or "日志" in text_lower:
        intent = "logs"
    if "restart" in text_lower or "重启" in text_lower:
        intent = "restart"

    for p in PROJECTS:
        if p in text_lower:
            project = p
            break

    return {"intent": intent, "project": project, "goal": text}


def get_status() -> str:
    healer_state = {}
    state_file = Path.home() / "dispatch_healer_state.json"
    if state_file.exists():
        healer_state = json.loads(state_file.read_text())

    result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
    running = {}
    for line in result.stdout.split("\n"):
        if "dispatch.py start" in line and "grep" not in line:
            for proj in PROJECTS:
                if f"dispatch.py start {proj}" in line:
                    running[proj] = line.split()[1]

    broken = len(healer_state.get("circuit_broken", []))
    lines = [
        f"CLUSTER: {'HEALTHY' if len(running) == len(PROJECTS) and broken == 0 else 'DEGRADED'}",
        f"Running: {len(running)}/{len(PROJECTS)} | Broken: {broken}\n",
    ]

    for project in PROJECTS:
        if project in running:
            lines.append(f"[OK] {project} PID:{running[project]}")
        else:
            lines.append(f"[STOPPED] {project}")

    return "\n".join(lines)


def start_cmd(update, context):
    update.message.reply_text("""Oyster Pipeline Controller

Commands:
/status - Cluster status
/logs <project> - View logs
/restart <project> - Restart project
/task <project> <goal> - Create task

Or just tell me what to do!""")


def status_cmd(update, context):
    update.message.reply_text(get_status())


def logs_cmd(update, context):
    if not context.args:
        update.message.reply_text("Usage: /logs <project>")
        return
    project = context.args[0]
    log_file = Path.home() / f"dispatch_{project}.log"
    if log_file.exists():
        content = log_file.read_text()
        update.message.reply_text(f"```\n{content[-2000:]}\n```")
    else:
        update.message.reply_text(f"No log for {project}")


def restart_cmd(update, context):
    if not context.args:
        update.message.reply_text("Usage: /restart <project>")
        return
    project = context.args[0]
    subprocess.run(["pkill", "-f", f"dispatch.py start {project}"], capture_output=True)
    subprocess.Popen(
        f"cd {DISPATCH_PATH} && python3 dispatch.py start {project} > ~/dispatch_{project}.log 2>&1 &",
        shell=True,
    )
    update.message.reply_text(f"Restarting {project}...")


def task_cmd(update, context):
    if len(context.args) < 2:
        update.message.reply_text("Usage: /task <project> <goal>")
        return

    project = context.args[0]
    goal = " ".join(context.args[1:])

    update.message.reply_text(f"Creating task: {project} - {goal}")

    # Create spec
    task_id = f"S99-TG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    spec = f"""---
task_id: {task_id}
project: {project}
priority: 1
modifies: [""]
executor: glm
---

## Goal
{goal}
"""

    spec_dir = Path(DISPATCH_PATH) / "specs" / project
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / f"{task_id}.md").write_text(spec)

    update.message.reply_text(f"Task created: {task_id}")


def handle_msg(update, context):
    text = update.message.text
    if text.startswith("/"):
        update.message.reply_text("Unknown command")
        return

    log(f"Message: {text}")

    intent = parse_intent(text)

    if intent["intent"] == "code_task":
        task_cmd(update, context)
    elif intent["intent"] == "status":
        status_cmd(update, context)
    elif intent["intent"] == "logs":
        for p in PROJECTS:
            if p in text.lower():
                context.args = [p]
                break
        logs_cmd(update, context)
    elif intent["intent"] == "restart":
        for p in PROJECTS:
            if p in text.lower():
                context.args = [p]
                break
        restart_cmd(update, context)
    else:
        response = call_glm(f"Oyster AI assistant. User: {text}")
        update.message.reply_text(response)


def main():
    log("Bot starting...")
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start_cmd))
    dp.add_handler(CommandHandler("status", status_cmd))
    dp.add_handler(CommandHandler("logs", logs_cmd))
    dp.add_handler(CommandHandler("restart", restart_cmd))
    dp.add_handler(CommandHandler("task", task_cmd))
    dp.add_handler(MessageHandler(Filters.text, handle_msg))
    log("Bot running!")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
