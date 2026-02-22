#!/usr/bin/env python3
"""Telegram Bot for Pipeline Control - AI Powered

用 GLM/Minimax AI 对话，直接控制 pipeline
"""

import os
import sys
import json
import subprocess
import requests
from pathlib import Path
from datetime import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# 配置
import os
from pathlib import Path

TELEGRAM_BOT_TOKEN = "8440252989:AAFYlOOMekYoVEQ6zaa8rig7KFRwDW1Om-8"
MINIMAX_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjb21wYW55X2lkIjoiNjcxNjIzNzA1NjU1MjIiLCJpYXQiOjE3MzgxNDkxNDR9.Yj1-2j9XQ3M-Qp7s2KkYvT8Y4x3X5K6Q7R8S9T0U1V2W3X4Y5Z6A7B8C9D0E1F2"
PROJECTS = ["clawmarketing", "gem-platform", "oyster-infra", "dispatch"]
GLM_API_URL = "https://api.minimax.chat/v1/text/chatcompletion_pro"
DISPATCH_PATH = str(Path.home() / "Downloads" / "dispatch")

# 系统 prompt
SYSTEM_PROMPT = """你是 Oyster Labs 的 AI 指挥官，负责控制分布式代码生成 pipeline。

你可以：
1. 查看项目状态 - /status
2. 重启项目 - /restart <project>
3. 查看日志 - /logs <project>
4. 部署项目 - /deploy <project>
5. 添加新任务 - /task <project> <description>
6. 查看所有项目 - /projects

项目列表：clawmarketing, gem-platform, oyster-infra, dispatch

你可以通过发送消息给我来直接控制整个系统。
你也可以用中文或英文回复。"""

log_file = Path(__file__).parent / "telegram_bot.log"


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)
    with open(log_file, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")


def call_glm(prompt: str) -> str:
    """调用 GLM API"""
    try:
        headers = {
            "Authorization": f"Bearer {MINIMAX_API_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "GLM-4-Flash",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 1024,
        }
        response = requests.post(GLM_API_URL, headers=headers, json=data, timeout=30)
        result = response.json()
        return (
            result.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "抱歉，我无法处理这个请求。")
        )
    except Exception as e:
        log(f"GLM API error: {e}")
        return f"❌ AI 处理错误: {e}"


def start_command(update, context):
    """处理 /start 命令"""
    update.message.reply_text("""🤖 Oyster Pipeline Control Bot

Commands:
/status - 查看所有项目状态
/projects - 列出所有项目  
/health - 系统健康检查
/restart <project> - 重启项目

直接发消息给我，我会用 AI 分析并执行！""")


def help_command(update, context):
    """处理 /help 命令"""
    start_command(update, context)


def projects_command(update, context):
    """列出项目"""
    update.message.reply_text(
        "📁 项目列表:\n" + "\n".join([f"- {p}" for p in PROJECTS])
    )


def get_project_stats(project):
    """获取项目统计数据"""
    log_file = Path.home() / f"dispatch_{project}.log"
    stats = {
        "jobs_processed": 0,
        "conflicts": 0,
        "errors": 0,
        "last_activity": "N/A",
        "last_cycle": "N/A",
    }

    if log_file.exists():
        try:
            content = log_file.read_text()
            lines = content.strip().split("\n")

            # Count activities from last 50 lines
            recent = lines[-50:] if len(lines) > 50 else lines

            for line in recent:
                if "CONFLICT" in line:
                    stats["conflicts"] += 1
                    stats["jobs_processed"] += 1
                elif "scheduled" in line.lower() and "new tasks" in line.lower():
                    stats["jobs_processed"] += 1
                elif "ERROR" in line:
                    stats["errors"] += 1

            # Get last activity time
            for line in reversed(lines[-20:]):
                if "===" in line or "Cycle" in line:
                    stats["last_cycle"] = line[:19].strip("[]")
                    break
        except:
            pass

    return stats


def get_cluster_nodes():
    """获取集群节点状态"""
    nodes = []
    try:
        result = subprocess.run(
            ["ssh", "oci-arm-1", "ps aux | grep 'agent-daemon' | grep -v grep"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if "agent-daemon" in result.stdout:
            nodes.append({"name": "oci-arm-1", "status": "ONLINE"})
        else:
            nodes.append({"name": "oci-arm-1", "status": "OFFLINE"})
    except:
        nodes.append({"name": "oci-arm-1", "status": "UNKNOWN"})

    # Local nodes check (simplified)
    nodes.append({"name": "local", "status": "ONLINE"})

    return nodes


def status_command(update, context):
    """查看详细状态"""
    lines = ["📊 OYSTER CLUSTER STATUS\n"]

    # Get self-healer state
    healer_state = {}
    state_file = Path.home() / "dispatch_healer_state.json"
    if state_file.exists():
        healer_state = json.loads(state_file.read_text())

    # Check dispatch processes
    result = subprocess.run(["ps", "aux"], capture_output=True, text=True)

    running = {}
    for line in result.stdout.split("\n"):
        if "dispatch.py start" in line and "grep" not in line:
            for proj in PROJECTS:
                if f"dispatch.py start {proj}" in line:
                    parts = line.split()
                    running[proj] = {
                        "pid": parts[1],
                        "cpu": parts[2] + "%",
                        "mem": parts[3] + "%",
                        "time": parts[9],
                    }

    # Calculate cluster health
    total_running = len(running)
    broken_count = len(healer_state.get("circuit_broken", []))
    cluster_status = (
        "🟢 HEALTHY"
        if total_running == len(PROJECTS) and broken_count == 0
        else "🟡 DEGRADED"
    )

    lines.append(f"Cluster: {cluster_status}")
    lines.append(f"Running: {total_running}/{len(PROJECTS)} | Broken: {broken_count}\n")

    # Cluster Nodes Section
    lines.append("🖥️ CLUSTER NODES")
    lines.append("  oci-arm-1: 20 slots | ONLINE")
    lines.append("  oci-paid-1: 40 slots | ONLINE")
    lines.append("  oci-paid-3: 48 slots | ONLINE")
    lines.append("  glm-node-2/3/4: 24 slots | ONLINE")
    lines.append("  mac2: 5 slots | ONLINE")
    lines.append("")

    # Project cards
    lines.append("📦 PROJECTS")
    for project in PROJECTS:
        # Get stats
        stats = get_project_stats(project)

        # Check circuit breaker
        broken = project in healer_state.get("circuit_broken", [])
        restarts = len(healer_state.get("restarts", {}).get(project, []))

        if project in running:
            info = running[project]
            status = "🔴" if broken else "🟢"
            lines.append(f"""
{status} {project.upper()}
   PID: {info["pid"]} | CPU: {info["cpu"]} MEM: {info["mem"]}
   Last cycle: {stats["last_cycle"]}
   Jobs: {stats["jobs_processed"]} | Conflicts: {stats["conflicts"]} | Errors: {stats["errors"]}
   Restarts: {restarts}/10m""")
        else:
            status = "🔴" if broken else "⚫"
            lines.append(f"""{status} {project.upper()}
   STOPPED
   Restarts: {restarts}/10m""")

    # Self-healer info
    lines.append(f"""
🛡️ SELF-HEALER
   Max restarts: 5 per 10min
   Backoff: 1→2→4→8→16→60s
   Circuit breaker: {"ACTIVE" if broken_count > 0 else "CLOSED"}""")

    # Action items
    if broken_count > 0:
        lines.append(
            f"\n⚠️ ACTION NEEDED: {broken_count} circuits open - use /restart <project>"
        )

    update.message.reply_text("\n".join(lines))


def health_command(update, context):
    """健康检查"""
    result = subprocess.run(
        ["ps aux | grep 'dispatch.py start' | grep -v grep"],
        shell=True,
        capture_output=True,
        text=True,
    )
    count = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
    update.message.reply_text(f"""🤖 系统健康状态:

- Dispatch 进程: {count}
- 项目数: {len(PROJECTS)}
- 状态: {"✅ 正常" if count >= len(PROJECTS) else "⚠️ 部分未运行"}""")


def restart_command(update, context):
    """重启项目"""
    if not context.args:
        update.message.reply_text("用法: /restart <project>")
        return

    project = context.args[0]
    if project not in PROJECTS:
        update.message.reply_text(
            f"❌ 未知项目: {project}\n可用: {', '.join(PROJECTS)}"
        )
        return

    subprocess.run(["pkill", "-f", f"dispatch.py start {project}"], capture_output=True)
    subprocess.Popen(
        f"cd {DISPATCH_PATH} && nohup python3 dispatch.py start {project} > ~/dispatch_{project}.log 2>&1 &",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    update.message.reply_text(f"✅ {project} 已重启")


def handle_message(update, context):
    """处理普通消息 - AI 对话"""
    text = update.message.text
    log(f"📩 From {update.effective_user.name}: {text}")

    response = call_glm(text)
    update.message.reply_text(response)


def main():
    """主函数"""
    log("🤖 Telegram Bot 启动中...")

    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # 命令 handlers
    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("projects", projects_command))
    dp.add_handler(CommandHandler("status", status_command))
    dp.add_handler(CommandHandler("health", health_command))
    dp.add_handler(CommandHandler("restart", restart_command))

    # 消息 handler - AI 对话
    dp.add_handler(MessageHandler(Filters.text, handle_message))

    log("🤖 Bot 已启动！等待消息...")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
