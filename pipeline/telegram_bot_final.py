#!/usr/bin/env python3
"""Telegram Bot v2 - Full Pipeline Control for Oyster Labs AI Factory"""

import os
import json
import sqlite3
import subprocess
import requests
from pathlib import Path
from datetime import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = "8440252989:AAFYlOOMekYoVEQ6zaa8rig7KFRwDW1Om-8"
BASE = str(Path.home())
DB_PATH = Path(BASE) / "Downloads" / "dispatch" / "dispatch.db"
DISPATCH_DIR = Path(BASE) / "Downloads" / "dispatch"
MINIMAX_KEY = os.environ.get(
    "MINIMAX_API_KEY",
    "sk-cp-T_Nj3VHn3G7Eyi3r50YumUyh-9cxvyV5xBd2RInrLvWKNHJsK-rCeMToiCy0rgWk2F1ZtOsZciTLjHxGYXipI2swY0ihhGfFY0K88q5XNJnLmBzqRbQLL_g",
)


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def get_db():
    """Get database connection with row_factory"""
    conn = sqlite3.connect(str(DB_PATH), timeout=5)
    conn.row_factory = sqlite3.Row
    return conn


def get_all_projects():
    """Get all projects from DB"""
    try:
        with get_db() as conn:
            rows = conn.execute(
                "SELECT DISTINCT project FROM tasks ORDER BY project"
            ).fetchall()
            return [r["project"] for r in rows]
    except Exception:
        return []


def get_active_projects():
    """Get projects that have pending or running tasks"""
    try:
        with get_db() as conn:
            rows = conn.execute(
                "SELECT DISTINCT project FROM tasks WHERE status IN ('pending', 'running') ORDER BY project"
            ).fetchall()
            return [r["project"] for r in rows]
    except Exception:
        return []


def get_running_dispatchers():
    """Get running dispatch processes"""
    try:
        r = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=5)
        running = {}
        for line in r.stdout.split("\n"):
            if "dispatch.py start" in line and "grep" not in line:
                parts = line.split()
                pid = parts[1]
                # Extract project name
                for i, part in enumerate(parts):
                    if part == "start" and i + 1 < len(parts):
                        project = parts[i + 1]
                        running[project] = pid
                        break
        return running
    except Exception:
        return {}


# ===== COMMANDS =====


def cmd_status(update, context):
    """Full pipeline status from DB"""
    try:
        with get_db() as conn:
            # Overall counts
            total = conn.execute(
                "SELECT status, COUNT(*) as cnt FROM tasks GROUP BY status"
            ).fetchall()
            counts = {r["status"]: r["cnt"] for r in total}

            # Per-project breakdown
            projects = conn.execute(
                """SELECT project, status, COUNT(*) as cnt
                   FROM tasks GROUP BY project, status
                   ORDER BY project"""
            ).fetchall()

            # Node usage
            nodes = conn.execute(
                """SELECT name, slots, running_count, enabled
                   FROM nodes WHERE slots > 0 ORDER BY name"""
            ).fetchall()

        dispatchers = get_running_dispatchers()

        # Build message
        pending = counts.get("pending", 0)
        running = counts.get("running", 0)
        completed = counts.get("completed", 0)
        failed = counts.get("failed", 0)
        total_tasks = pending + running + completed + failed

        txt = "🏭 AI FACTORY STATUS\n"
        txt += "━━━━━━━━━━━━━━━━\n"
        txt += f"📊 Total: {total_tasks} tasks\n"
        txt += f"⏳ Pending: {pending}\n"
        txt += f"🔄 Running: {running}\n"
        txt += f"✅ Done: {completed}\n"
        if failed > 0:
            txt += f"❌ Failed: {failed}\n"
        txt += f"🚀 Dispatchers: {len(dispatchers)}\n"
        txt += "\n"

        # Node utilization
        total_slots = sum(n["slots"] for n in nodes)
        used_slots = sum(min(n["running_count"], n["slots"]) for n in nodes)
        txt += f"💻 NODES: {used_slots}/{total_slots} slots\n"
        for n in nodes:
            used = min(n["running_count"], n["slots"])
            bar_len = 8
            filled = int(bar_len * used / n["slots"]) if n["slots"] > 0 else 0
            bar = "█" * filled + "░" * (bar_len - filled)
            txt += f"  {bar} {n['name']}: {used}/{n['slots']}\n"

        txt += "\n📦 PROJECTS:\n"
        # Group by project
        proj_data = {}
        for row in projects:
            p = row["project"]
            if p not in proj_data:
                proj_data[p] = {}
            proj_data[p][row["status"]] = row["cnt"]

        for p in sorted(proj_data.keys()):
            d = proj_data[p]
            p_pending = d.get("pending", 0)
            p_running = d.get("running", 0)
            p_done = d.get("completed", 0)
            p_failed = d.get("failed", 0)
            p_total = p_pending + p_running + p_done + p_failed

            # Progress bar
            pct = int(100 * p_done / p_total) if p_total > 0 else 0
            dispatcher_icon = "🟢" if p in dispatchers else "⚪"
            status_icon = "✅" if p_done == p_total else "🔨" if p_running > 0 else "⏳"

            txt += f"\n{dispatcher_icon} {p} {status_icon}\n"
            txt += f"  {p_done}/{p_total} done ({pct}%)"
            if p_running > 0:
                txt += f" | {p_running} running"
            if p_pending > 0:
                txt += f" | {p_pending} queued"
            if p_failed > 0:
                txt += f" | ❌{p_failed}"
            txt += "\n"

        update.message.reply_text(txt)
    except Exception as e:
        log(f"Status error: {e}")
        update.message.reply_text(f"Error: {e}")


def cmd_pipeline(update, context):
    """Show running tasks with details"""
    try:
        with get_db() as conn:
            running = conn.execute(
                """SELECT id, project, node,
                          CAST((strftime('%s','now') - strftime('%s', started_at)) AS INTEGER) as elapsed
                   FROM tasks WHERE status = 'running'
                   ORDER BY started_at ASC"""
            ).fetchall()

        if not running:
            update.message.reply_text("🟢 No tasks currently running.")
            return

        txt = f"🔄 RUNNING TASKS ({len(running)})\n"
        txt += "━━━━━━━━━━━━━━━━\n"

        by_node = {}
        for t in running:
            node = t["node"] or "unknown"
            if node not in by_node:
                by_node[node] = []
            by_node[node].append(t)

        for node in sorted(by_node.keys()):
            tasks = by_node[node]
            txt += f"\n💻 {node} ({len(tasks)} tasks):\n"
            for t in tasks[:10]:  # Limit to 10 per node
                elapsed = t["elapsed"] or 0
                mins = elapsed // 60
                secs = elapsed % 60
                txt += f"  {t['id']} ({mins}m{secs}s)\n"
            if len(tasks) > 10:
                txt += f"  ...and {len(tasks) - 10} more\n"

        update.message.reply_text(txt)
    except Exception as e:
        update.message.reply_text(f"Error: {e}")


def cmd_failed(update, context):
    """Show and optionally retry failed tasks"""
    try:
        with get_db() as conn:
            failed = conn.execute(
                """SELECT id, project, node, attempt, error
                   FROM tasks WHERE status = 'failed'
                   ORDER BY project, id"""
            ).fetchall()

        if not failed:
            update.message.reply_text("✅ No failed tasks!")
            return

        # Check if user wants to retry
        if context.args and context.args[0] == "retry":
            with get_db() as conn:
                conn.execute(
                    "UPDATE tasks SET status = 'pending', node = NULL, attempt = 0, error = NULL WHERE status = 'failed'"
                )
                conn.commit()
            update.message.reply_text(
                f"🔄 Reset {len(failed)} failed task(s) to pending for retry."
            )
            return

        txt = f"❌ FAILED TASKS ({len(failed)})\n"
        txt += "━━━━━━━━━━━━━━━━\n"
        for t in failed[:20]:
            reason = str(t["attempt"])[:50] if t["attempt"] else "unknown"
            txt += f"\n{t['id']} ({t['project']})\n"
            txt += f"  Node: {t['node']}\n"
            txt += f"  Reason: {reason}\n"

        if len(failed) > 20:
            txt += f"\n...and {len(failed) - 20} more"

        txt += "\n\nUse /failed retry to reset all."
        update.message.reply_text(txt)
    except Exception as e:
        update.message.reply_text(f"Error: {e}")


def cmd_nodes(update, context):
    """Show detailed node status with SSH connectivity"""
    try:
        with get_db() as conn:
            nodes = conn.execute(
                """SELECT name, ssh_host, slots, running_count, executor, priority, enabled
                   FROM nodes ORDER BY priority ASC, name"""
            ).fetchall()

        txt = "💻 NODE STATUS\n"
        txt += "━━━━━━━━━━━━━━━━\n"

        total_slots = 0
        total_used = 0

        for n in nodes:
            if not n["enabled"]:
                continue
            slots = n["slots"]
            used = min(n["running_count"], slots)
            total_slots += slots
            total_used += used

            if slots == 0:
                icon = "⏸️"
            elif used == 0:
                icon = "🟢"
            elif used >= slots:
                icon = "🔴"
            else:
                icon = "🟡"

            pct = int(100 * used / slots) if slots > 0 else 0
            txt += f"\n{icon} {n['name']}\n"
            txt += f"  {used}/{slots} slots ({pct}%)"
            txt += f" | P{n['priority']} | {n['executor']}\n"

        txt += f"\n━━━━━━━━━━━━━━━━\n"
        total_pct = int(100 * total_used / total_slots) if total_slots > 0 else 0
        txt += f"Total: {total_used}/{total_slots} ({total_pct}%)"

        update.message.reply_text(txt)
    except Exception as e:
        update.message.reply_text(f"Error: {e}")


def cmd_restart(update, context):
    """Restart a project dispatcher"""
    try:
        projects = get_all_projects()
        if not context.args:
            active = get_active_projects()
            dispatchers = get_running_dispatchers()
            txt = "Usage: /restart <project>\n\n"
            txt += "Active projects:\n"
            for p in projects:
                icon = "🟢" if p in dispatchers else "⚪"
                tasks = "active" if p in active else "done"
                txt += f"  {icon} {p} ({tasks})\n"
            update.message.reply_text(txt)
            return

        p = context.args[0]
        # Kill existing
        subprocess.run(
            ["pkill", "-f", f"dispatch.py start {p}"], capture_output=True
        )

        # Start new
        subprocess.Popen(
            f"cd {DISPATCH_DIR} && python3 dispatch.py start {p} > {BASE}/dispatch_{p}.log 2>&1 &",
            shell=True,
        )
        update.message.reply_text(f"🔄 Restarting dispatcher for {p}...")
    except Exception as e:
        update.message.reply_text(f"Error: {e}")


def cmd_logs(update, context):
    """Show recent logs for a project"""
    try:
        if not context.args:
            update.message.reply_text("Usage: /logs <project>")
            return

        p = context.args[0]
        logf = Path(f"{BASE}/dispatch_{p}.log")

        if logf.exists():
            content = logf.read_text()[-2000:]
            # Telegram has 4096 char limit
            if len(content) > 3900:
                content = content[-3900:]
            update.message.reply_text(f"📋 {p} logs:\n```\n{content}\n```", parse_mode="Markdown")
        else:
            update.message.reply_text(f"No log file for {p}")
    except Exception as e:
        update.message.reply_text(f"Error: {e}")


def cmd_report(update, context):
    """Generate and show quick report"""
    try:
        with get_db() as conn:
            # Recent completions
            recent = conn.execute(
                """SELECT id, project, node, completed_at
                   FROM tasks WHERE status = 'completed'
                   ORDER BY completed_at DESC LIMIT 10"""
            ).fetchall()

            # Success rate
            total = conn.execute(
                "SELECT COUNT(*) as cnt FROM tasks WHERE status IN ('completed', 'failed')"
            ).fetchone()["cnt"]
            completed = conn.execute(
                "SELECT COUNT(*) as cnt FROM tasks WHERE status = 'completed'"
            ).fetchone()["cnt"]

        rate = int(100 * completed / total) if total > 0 else 0

        txt = "📊 PIPELINE REPORT\n"
        txt += "━━━━━━━━━━━━━━━━\n"
        txt += f"Success rate: {rate}% ({completed}/{total})\n\n"
        txt += "Recent completions:\n"
        for r in recent:
            time_str = r["completed_at"][:16] if r["completed_at"] else "?"
            txt += f"  ✅ {r['id']} on {r['node']} ({time_str})\n"

        update.message.reply_text(txt)
    except Exception as e:
        update.message.reply_text(f"Error: {e}")


def cmd_help(update, context):
    """Help command"""
    update.message.reply_text(
        """🏭 OYSTER AI FACTORY BOT v2

📋 COMMANDS:
/status - 全局状态总览
/pipeline - 正在运行的任务
/nodes - 节点状态
/failed - 失败任务 (+ retry)
/report - 完成率报告
/restart <project> - 重启调度器
/logs <project> - 查看日志
/help - 帮助

💬 也可以直接发消息和 AI 聊天!"""
    )


def handle_msg(update, context):
    """Handle natural language messages"""
    try:
        text = update.message.text
        log(f"MSG: {text}")
        tl = text.lower()

        # Smart routing based on keywords
        projects = get_all_projects()
        for p in projects:
            if p in tl:
                if any(w in tl for w in ["restart", "重启", "reboot"]):
                    context.args = [p]
                    cmd_restart(update, context)
                    return
                elif any(w in tl for w in ["log", "日志"]):
                    context.args = [p]
                    cmd_logs(update, context)
                    return

        if any(w in tl for w in ["status", "状态", "健康", "health"]):
            cmd_status(update, context)
            return
        elif any(w in tl for w in ["pipeline", "管道", "running", "运行"]):
            cmd_pipeline(update, context)
            return
        elif any(w in tl for w in ["node", "节点", "机器"]):
            cmd_nodes(update, context)
            return
        elif any(w in tl for w in ["fail", "失败", "错误", "error"]):
            cmd_failed(update, context)
            return
        elif any(w in tl for w in ["report", "报告", "成功率"]):
            cmd_report(update, context)
            return

        # Default: AI chat via MiniMax
        try:
            # Build context-aware system prompt
            with get_db() as conn:
                stats = conn.execute(
                    "SELECT status, COUNT(*) as cnt FROM tasks GROUP BY status"
                ).fetchall()
                db_context = ", ".join(
                    f"{r['status']}: {r['cnt']}" for r in stats
                )

            system_prompt = (
                f"You are the Oyster Labs AI Factory assistant. "
                f"Current pipeline: {db_context}. "
                f"Answer concisely in the user's language (Chinese or English)."
            )

            r = requests.post(
                "https://api.minimax.io/v1/text/chatcompletion_v2",
                headers={"Authorization": f"Bearer {MINIMAX_KEY}"},
                json={
                    "model": "MiniMax/MiniMax-M2.5",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text},
                    ],
                },
                timeout=60,
            )
            data = r.json()

            if r.status_code == 200:
                resp = (
                    data.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "No response")
                )
                update.message.reply_text(resp)
            else:
                err_msg = data.get("base_resp", {}).get("status_msg", "Unknown")
                update.message.reply_text(f"LLM Error: {err_msg}")
        except Exception as e:
            log(f"LLM Error: {e}")
            update.message.reply_text(
                f"🤖 LLM offline. Use commands:\n/status /pipeline /nodes /failed /report"
            )

    except Exception as e:
        log(f"Error: {e}")
        update.message.reply_text(f"Error: {e}")


def main():
    log("🏭 Starting Oyster AI Factory Bot v2...")
    updater = Updater(TOKEN, use_context=True)

    # Set menu commands
    try:
        updater.bot.set_my_commands(
            [
                ("status", "全局状态总览"),
                ("pipeline", "运行中的任务"),
                ("nodes", "节点状态"),
                ("failed", "失败任务"),
                ("report", "完成率报告"),
                ("restart", "重启调度器"),
                ("logs", "查看日志"),
                ("help", "帮助"),
            ]
        )
        log("✅ Menu commands set!")
    except Exception as e:
        log(f"⚠️ Could not set menu: {e}")

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", cmd_help))
    dp.add_handler(CommandHandler("help", cmd_help))
    dp.add_handler(CommandHandler("status", cmd_status))
    dp.add_handler(CommandHandler("pipeline", cmd_pipeline))
    dp.add_handler(CommandHandler("nodes", cmd_nodes))
    dp.add_handler(CommandHandler("failed", cmd_failed))
    dp.add_handler(CommandHandler("report", cmd_report))
    dp.add_handler(CommandHandler("restart", cmd_restart))
    dp.add_handler(CommandHandler("logs", cmd_logs))
    dp.add_handler(MessageHandler(~Filters.command, handle_msg))

    log("🏭 Bot running! Commands: status, pipeline, nodes, failed, report, restart, logs")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
