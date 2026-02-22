#!/usr/bin/env python3
"""
拜占庭对撞器 - Telegram Bot
完整功能版
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Optional

# 环境变量
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_URL = os.getenv("API_URL", "http://localhost:5000")


class TelegramBot:
    """Telegram Bot"""

    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{token}"

    async def send_message(self, text: str, parse_mode: str = "Markdown") -> dict:
        """发送消息"""
        import aiohttp

        url = f"{self.api_url}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": text, "parse_mode": parse_mode}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                return await resp.json()

    async def send_collision_request(self, topic: str, rounds: int = 3) -> dict:
        """发起碰撞请求"""
        import aiohttp

        url = f"{API_URL}/api/collision"
        payload = {"topic": topic, "rounds": rounds}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                return await resp.json()

    async def get_collision_result(self, collision_id: str) -> dict:
        """获取碰撞结果"""
        import aiohttp

        url = f"{API_URL}/api/collision/{collision_id}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.json()


# Bot 命令处理器
async def handle_command(update: dict, bot: TelegramBot):
    """处理命令"""

    message = update.get("message", {})
    chat = message.get("chat", {})
    text = message.get("text", "")

    # /start
    if text == "/start":
        await bot.send_message(
            "⚔️ *拜占庭对撞器*\n\n"
            "AI-to-AI 产品碰撞系统\n\n"
            "命令:\n"
            "/碰撞 [主题] - 发起碰撞\n"
            "/状态 - 查看状态\n"
            "/帮助 - 显示帮助"
        )

    # /help
    elif text == "/help":
        await bot.send_message(
            "📖 *帮助*\n\n"
            "/碰撞 [主题] - 发起碰撞\n"
            "  例如: /碰撞 AI 产品是否可行\n\n"
            "/状态 - 查看 API 状态\n"
            "/历史 - 查看最近碰撞\n"
            "/帮助 - 显示帮助"
        )

    # /状态
    elif text == "/状态":
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{API_URL}/health") as resp:
                    data = await resp.json()
                    await bot.send_message(
                        f"✅ API 状态: {data.get('status', 'unknown')}"
                    )
        except:
            await bot.send_message("❌ API 未连接")

    # /碰撞
    elif text.startswith("/碰撞 "):
        topic = text[4:].strip()
        if not topic:
            await bot.send_message("请输入碰撞主题，例如: /碰撞 AI 产品")
            return

        await bot.send_message(f"🚀 发起碰撞: {topic}")

        # 发起碰撞
        try:
            result = await bot.send_collision_request(topic)
            collision_id = result.get("id")

            if collision_id:
                await bot.send_message(
                    f"✅ 碰撞已发起!\n"
                    f"ID: `{collision_id}`\n\n"
                    f"使用 /结果 {collision_id} 查看结果"
                )
            else:
                await bot.send_message(
                    f"❌ 发起失败: {result.get('error', '未知错误')}"
                )
        except Exception as e:
            await bot.send_message(f"❌ 错误: {str(e)}")

    # /结果
    elif text.startswith("/结果 "):
        collision_id = text[4:].strip()

        try:
            result = await bot.get_collision_result(collision_id)
            status = result.get("status")

            if status == "completed":
                summary = (
                    result.get("result", {}).get("convergence", {}).get("summary", "无")
                )
                await bot.send_message(
                    f"✅ 碰撞完成!\n\n"
                    f"主题: {result.get('topic')}\n\n"
                    f"结论:\n{summary[:500]}"
                )
            elif status == "running":
                await bot.send_message("⏳ 碰撞进行中，请稍后再查...")
            else:
                await bot.send_message(
                    f"❌ 碰撞失败: {result.get('error', '未知错误')}"
                )
        except Exception as e:
            await bot.send_message(f"❌ 错误: {str(e)}")

    # 未知命令
    else:
        await bot.send_message("未知命令，输入 /帮助 查看可用命令")


async def webhook_handler(request):
    """Webhook 处理"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return {"status": "error", "message": "Telegram not configured"}

    bot = TelegramBot(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)

    try:
        update = await request.json()
        await handle_command(update, bot)
    except Exception as e:
        print(f"Error: {e}")

    return {"status": "ok"}


def main():
    """测试发送"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("请设置 TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID")
        return

    bot = TelegramBot(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)

    # 测试发送
    asyncio.run(bot.send_message("⚔️ 拜占庭对撞器 Bot 已启动!"))


if __name__ == "__main__":
    main()
