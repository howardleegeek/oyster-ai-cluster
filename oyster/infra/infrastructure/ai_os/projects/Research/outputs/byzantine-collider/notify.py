#!/usr/bin/env python3
"""
拜占庭对撞器 - 通知模块
支持 Telegram 和 Discord
"""

import os
import threading
from typing import Optional


class Notifier:
    """通知器"""

    def __init__(self):
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")

    def notify(self, title: str, message: str, collision_id: str = None):
        """发送通知"""
        # 异步发送
        threading.Thread(target=self._send, args=(title, message, collision_id)).start()

    def _send(self, title: str, message: str, collision_id: str = None):
        """实际发送"""
        if self.telegram_token and self.telegram_chat_id:
            self._send_telegram(title, message, collision_id)

        if self.discord_webhook:
            self._send_discord(title, message, collision_id)

    def _send_telegram(self, title: str, message: str, collision_id: str = None):
        """发送 Telegram"""
        try:
            import requests

            text = f"⚔️ *{title}*\n\n{message}"
            if collision_id:
                text += f"\n\nID: `{collision_id}`"

            requests.post(
                f"https://api.telegram.org/bot{self.telegram_token}/sendMessage",
                json={
                    "chat_id": self.telegram_chat_id,
                    "text": text,
                    "parse_mode": "Markdown",
                },
                timeout=10,
            )
        except Exception as e:
            print(f"Telegram 发送失败: {e}")

    def _send_discord(self, title: str, message: str, collision_id: str = None):
        """发送 Discord"""
        try:
            import requests

            embed = {
                "title": f"⚔️ {title}",
                "description": message,
                "color": 0x6366F1,
                "footer": {"text": "拜占庭对撞器"},
            }

            if collision_id:
                embed["fields"] = [{"name": "ID", "value": collision_id}]

            requests.post(self.discord_webhook, json={"embeds": [embed]}, timeout=10)
        except Exception as e:
            print(f"Discord 发送失败: {e}")


# 全局实例
notifier = Notifier()


def notify_collision_complete(collision_id: str, topic: str, status: str):
    """通知碰撞完成"""
    if status == "completed":
        message = f"主题: {topic}\n状态: ✅ 完成"
    else:
        message = f"主题: {topic}\n状态: ❌ 失败"

    notifier.notify("碰撞完成", message, collision_id)
