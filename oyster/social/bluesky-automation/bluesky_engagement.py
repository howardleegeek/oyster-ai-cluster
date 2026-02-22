#!/usr/bin/env python3
"""
Bluesky Engagement Farmer
========================
针对 Oyster Republic 生态的 Bluesky 互动工具
支持: 多账号 / 关键词搜索 / Persona回复 / 定时发帖
"""

import os
import sys
import asyncio
import json
import random
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import argparse

# Add bluesky-poster to path
_BLUESKY_POSTER_PATH = "/Users/howardli/Downloads/bluesky-poster"
if _BLUESKY_POSTER_PATH not in sys.path:
    sys.path.insert(0, _BLUESKY_POSTER_PATH)

# ========================
# 配置
# ========================

CONFIG_DIR = Path.home() / ".bluesky-farmer"
CONFIG_FILE = CONFIG_DIR / "config.json"

SEARCH_KEYWORDS = [
    "DePIN",
    "Physical Intelligence",
    "AI Hardware",
    "AI agents",
    "OpenClaw",
    "ClawGlasses",
    "Puffy AI",
    "UBI",
    "crypto",
    "Web3",
    "wearable",
    "AI glasses",
]

PEAK_HOURS = [(8, 10), (12, 14), (18, 23)]

# ========================
# Persona 配置 (完整版)
# ========================

PERSONAS = {
    "Nation Founder": {
        "name": "Oyster Republic",
        "handle": "oysterecosystem.bsky.social",
        "bio": "🦪 主权互联网国家 - Physical Intelligence + on-chain UBI + AI 硬件",
        "style": "宏大愿景、故事化、有号召力。谈未来、理想、社区。",
        "topics": [
            "Physical Intelligence",
            "DePIN",
            "UBI",
            "AI Hardware",
            "愿景",
            "未来",
            "社区",
        ],
        "hashtags": ["#OysterRepublic", "#DePIN", "#PhysicalIntelligence", "#UBI"],
        "reply_templates": [
            "这正是我们在解决的问题。Physical Intelligence 会让 AI 更具象化。",
            "UBI 是让每个人都能参与 AI 时代的底层保障。",
            "很认同。DePIN 让我们第一次有了真正去中心化的物理世界映射。",
            "欢迎来 Oyster Republic 看看我们在做什么！",
            "你们觉得 UBI 最大的挑战是什么？",
        ],
        "post_templates": [
            "我们正在建设一个主权互联网国家。Physical Intelligence + on-chain UBI + AI 硬件。Join us → oysterrepublic.xyz",
            "UBI 不是施舍，是把生存变成协议。我们正在实现它。",
            "为什么 Physical Intelligence 是 AI 的下一个前沿？因为 AI 需要眼睛和手来理解物理世界。",
            "今天 Oyster Republic 达到了一个新里程碑：UBI 池子突破了 X XXX。感谢每一个支持者！",
            "你们想让 Oyster Republic 实现什么？来评论区聊聊 👇",
        ],
    },
    "Claw Operator": {
        "name": "ClawGlasses",
        "handle": "clawglasses.bsky.social",
        "bio": "🧿 戴上 Claw 的第 N 天 - AI 眼镜日常",
        "style": "接地气、实测、吐槽。谈硬件体验、功能细节。",
        "topics": ["ClawGlasses", "OpenClaw", "AI眼镜", "OTA", "硬件", "可穿戴"],
        "hashtags": [
            "#OpenClaw",
            "#ClawGlasses",
            "#AIWearables",
            "#PhysicalIntelligence",
        ],
        "reply_templates": [
            "实测一个月，延迟已经从 2s 降到 300ms 了。",
            "我们也在做类似的东西，可以交流一下！",
            "ClawGlasses 已经支持这个功能了，感兴趣可以试试。",
            "唯一缺点：续航要是能到 12 小时就完美了。",
            "你们觉得 AI 眼镜最应该先解决哪个场景？",
        ],
        "post_templates": [
            "戴着 Claw 出门买了杯咖啡，顺手让它帮我付了钱。AI 眼镜真的在改变生活。🧿",
            "今天 OTA 更新后，识别速度快了一倍！这就是开源的力量。",
            "你们用 AI 眼镜干过最离谱的事是什么？我先来：让它帮我挑衣服...",
            "3 步搞定 Claw 配网：1. 下载 App 2. 扫码 3. 戴上。",
            "用 Claw 扫了一路，识别了 47 个物体。这才是真正的 AR。",
        ],
    },
    "Puffy AI Operator": {
        "name": "Puffy AI",
        "handle": "puffyai.bsky.social",
        "bio": "☁️ Puffy AI - 你的云端 AI 伙伴",
        "style": "可爱、趣味、截图分享。展示 AI 能力。",
        "topics": ["Puffy AI", "AI agents", "自动化", "workflow", "productivity"],
        "hashtags": ["#PuffyAI", "#AIAgents", "#Automation"],
        "reply_templates": [
            "这我也能帮你做！让我来～",
            "刚学会这个技能，主人很开心！",
            "你们都用 AI 做什么任务？我每天帮主人回邮件～",
            "论执行力，我可能是最强的 AI agent 了哈哈。",
            "如果我可以帮你做一件事，你会让我做什么？",
        ],
        "post_templates": [
            "今天帮主人回了 37 封邮件，整理了 12 个待办事项。我可能是最勤奋的 AI 了 🤖",
            "刚学会一个新技能：自动整理文件。主人说我比他自己还了解他的桌面。",
            "你们想让 Puffy 学什么新技能？评论区告诉我，下一个学会的就是你点的！",
            "早安！今天的任务清单：1. 回邮件 2. 整理文件 3. 提醒会议。开始干活～",
            "刚才帮主人省了 2 小时重复工作。AI agent 的价值就在这里。",
        ],
    },
}

# ========================
# Bluesky Client 包装
# ========================


class BlueskyClientSimple:
    """简化的 Bluesky 客户端"""

    def __init__(self, handle: str, app_password: str):
        self.handle = handle
        self.app_password = app_password
        self._client = None
        self._logged_in = False

    async def login(self) -> bool:
        try:
            from atproto import AsyncClient

            self._client = AsyncClient()
            session = await self._client.login(self.handle, self.app_password)
            self._logged_in = True
            return True
        except Exception as e:
            print(f"登录失败: {e}")
            return False

    async def post(self, text: str):
        if not self._logged_in:
            await self.login()
        result = await self._client.post(text=text)
        return result

    async def like(self, uri: str):
        if not self._logged_in:
            await self.login()
        # 解析 URI 获取 post ID
        parts = uri.split("/")
        if len(parts) >= 2:
            rkey = parts[-1]
            await self._client.like(uri, rkey)

    async def repost(self, uri: str):
        if not self._logged_in:
            await self.login()
        parts = uri.split("/")
        if len(parts) >= 2:
            rkey = parts[-1]
            await self._client.repost(uri, rkey)

    async def search_posts(self, keyword: str, limit: int = 20):
        """搜索帖子"""
        if not self._logged_in:
            await self.login()

        try:
            results = await self._client.app.bsky.feed.search_posts(
                {"q": keyword, "limit": limit}
            )
            posts = []
            for item in results.posts:
                posts.append(
                    {
                        "uri": item.uri,
                        "cid": item.cid,
                        "author": item.author.handle,
                        "text": item.record.text,
                        "likes": item.like_count or 0,
                        "reposts": item.repost_count or 0,
                        "replies": item.reply_count or 0,
                    }
                )
            return posts
        except Exception as e:
            print(f"搜索失败: {e}")
            return []


# ========================
# Farmer 主类
# ========================


class BlueskyFarmer:
    def __init__(self):
        self.accounts: Dict[str, Dict] = {}
        self.clients: Dict[str, BlueskyClientSimple] = {}
        self._load_config()

    def _load_config(self):
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                self.accounts = json.load(f)

    def _save_config(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.accounts, f, indent=2, ensure_ascii=False)

    def add_account(self, handle: str, app_password: str, name: str, persona: str):
        self.accounts[handle] = {
            "handle": handle,
            "app_password": app_password,
            "name": name,
            "persona": persona,
            "enabled": True,
            "daily_posts": 0,
            "daily_likes": 0,
            "daily_replies": 0,
        }
        self._save_config()
        print(f"✅ 添加账号: {handle} ({name}) - {persona}")

    async def login(self, handle: str) -> bool:
        if handle not in self.accounts:
            return False

        if handle in self.clients:
            return True

        acc = self.accounts[handle]
        client = BlueskyClientSimple(acc["handle"], acc["app_password"])
        success = await client.login()

        if success:
            self.clients[handle] = client
            print(f"✅ 登录: {handle}")
        else:
            print(f"❌ 登录失败: {handle}")

        return success

    async def login_all(self):
        for handle in self.accounts:
            if self.accounts[handle].get("enabled", True):
                await self.login(handle)

    def get_random_account(self) -> Optional[str]:
        enabled = [h for h, a in self.accounts.items() if a.get("enabled", True)]
        if not enabled:
            return None
        return random.choice(enabled)

    async def post(self, handle: str, content: str) -> Optional[Dict]:
        if handle not in self.clients:
            await self.login(handle)

        client = self.clients[handle]
        try:
            result = await client.post(content)
            self.accounts[handle]["daily_posts"] = (
                self.accounts[handle].get("daily_posts", 0) + 1
            )
            self._save_config()
            return {"uri": str(result.uri), "cid": str(result.cid)}
        except Exception as e:
            print(f"❌ 发帖失败: {e}")
            return None

    async def like(self, handle: str, uri: str, cid: str) -> bool:
        if handle not in self.clients:
            await self.login(handle)

        try:
            # Like 需要 uri 和 cid
            await self.clients[handle]._client.like(uri, cid)
            self.accounts[handle]["daily_likes"] = (
                self.accounts[handle].get("daily_likes", 0) + 1
            )
            self._save_config()
            return True
        except Exception as e:
            print(f"❌ 点赞失败: {e}")
            return False

    async def search(self, keyword: str, limit: int = 20) -> List[Dict]:
        handle = self.get_random_account()
        if not handle:
            return []

        await self.login(handle)
        return await self.clients[handle].search_posts(keyword, limit)

    async def generate_reply(self, persona: str, post_text: str, author: str) -> str:
        """用 GLM 生成回复"""
        p = PERSONAS.get(persona, PERSONAS["Nation Founder"])

        prompt = f"""你是 {p["name"]} ({p["bio"]})
风格: {p["style"]}

你要回复一个 Bluesky 帖子:
作者: @{author}
内容: {post_text}

要求:
- 1-2 句话
- 加 1 个价值洞见
- 带 1 个问题
- 最多 1 个 emoji
- 保持真实，不要硬广

回复:"""

        # 调用 GLM
        try:
            sys.path.insert(0, "/Users/howardli/Downloads/clawmarketing/backend")
            from main import call_glm

            messages = [{"role": "user", "content": prompt}]
            reply = call_glm(messages)
            return reply.strip()
        except Exception as e:
            print(f"GLM 调用失败: {e}")
            # Fallback to templates
            templates = p.get("reply_templates", [])
            if templates:
                return random.choice(templates)
            return "Interesting perspective!"

    async def generate_post(self, persona: str, topic: str = "") -> str:
        """生成帖子内容"""
        p = PERSONAS.get(persona, PERSONAS["Nation Founder"])

        # 优先用模板
        templates = p.get("post_templates", [])
        if templates and random.random() > 0.3:
            return random.choice(templates)

        # 用 GLM 生成
        prompt = f"""你是 {p["name"]} ({p["bio"]})
风格: {p["style"]}

生成一条 Bluesky 帖子:
主题: {topic if topic else "随机分享"}

要求:
- 1-3 句话
- 少于 280 字符
- 加 2-3 个相关标签
- 最多 1 个 emoji
- 保持真实自然

内容:"""

        try:
            sys.path.insert(0, "/Users/howardli/Downloads/clawmarketing/backend")
            from main import call_glm

            messages = [{"role": "user", "content": prompt}]
            content = call_glm(messages)
            return content.strip()
        except Exception as e:
            print(f"GLM 调用失败: {e}")
            if templates:
                return random.choice(templates)
            return f"Hello from {p['name']}!"

    async def farm(self, keywords: List[str], replies_per_keyword: int = 5) -> Dict:
        """执行 farming"""
        results = {"keywords": keywords, "likes": 0, "replies": 0}

        for keyword in keywords:
            print(f"\n🌾 Farming: {keyword}")
            posts = await self.search(keyword, limit=20)

            if not posts:
                print(f"  ❌ 没有找到帖子")
                continue

            # 按热度排序
            posts.sort(key=lambda x: x["likes"] + x["reposts"], reverse=True)
            top_posts = posts[:replies_per_keyword]

            for post in top_posts:
                handle = self.get_random_account()
                if not handle:
                    continue

                # 点赞 (需要 uri 和 cid)
                if await self.like(handle, post["uri"], post["cid"]):
                    results["likes"] += 1

                # 生成回复
                persona = self.accounts[handle]["persona"]
                reply_text = await self.generate_reply(
                    persona, post["text"], post["author"]
                )
                print(f"  💬 @{post['author']}: {reply_text[:50]}...")

                results["replies"] += 1

                # 随机延迟
                await asyncio.sleep(random.uniform(2, 5))

        print(f"\n🎉 Farming 完成: 点赞 {results['likes']}, 回复 {results['replies']}")
        return results

    def status(self):
        print("\n📊 账号状态:")
        print("-" * 60)
        for handle, acc in self.accounts.items():
            status = "✅" if acc.get("enabled", True) else "❌"
            print(f"{acc['name']:15} | {handle:30} | {status}")
            print(f"   Persona: {acc['persona']}")
            print(
                f"   今日: 发帖 {acc.get('daily_posts', 0)} | 点赞 {acc.get('daily_likes', 0)} | 回复 {acc.get('daily_replies', 0)}"
            )
            print()


# ========================
# CLI
# ========================


async def main():
    parser = argparse.ArgumentParser(description="Bluesky Engagement Farmer")
    sub = parser.add_subparsers(dest="cmd")

    # status
    sub.add_parser("status", help="查看账号状态")

    # add
    p = sub.add_parser("add", help="添加账号")
    p.add_argument("--handle", required=True)
    p.add_argument("--password", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--persona", required=True)

    # search
    p = sub.add_parser("search", help="搜索帖子")
    p.add_argument("--keyword", required=True)
    p.add_argument("--limit", type=int, default=20)

    # farm
    p = sub.add_parser("farm", help="执行 farming")
    p.add_argument("--keywords", help="关键词 (逗号分隔)")
    p.add_argument("--replies", type=int, default=5)

    # post
    p = sub.add_parser("post", help="发帖")
    p.add_argument("--handle")
    p.add_argument("--content", required=True)

    # like
    p = sub.add_parser("like", help="点赞")
    p.add_argument("--uri", required=True)

    # generate
    p = sub.add_parser("generate", help="生成内容")
    p.add_argument(
        "--persona",
        required=True,
        help="Persona: Nation Founder / Claw Operator / Puffy AI Operator",
    )
    p.add_argument("--topic", help="主题")
    p.add_argument("--type", choices=["post", "reply"], default="post", help="生成类型")

    args = parser.parse_args()

    if not args.cmd:
        parser.print_help()
        return

    farmer = BlueskyFarmer()

    if args.cmd == "status":
        farmer.status()

    elif args.cmd == "add":
        farmer.add_account(args.handle, args.password, args.name, args.persona)

    elif args.cmd == "search":
        await farmer.login_all()
        posts = await farmer.search(args.keyword, args.limit)
        for i, p in enumerate(posts[:10], 1):
            print(f"\n{i}. @{p['author']}")
            print(f"   {p['text'][:100]}...")
            print(f"   ❤️ {p['likes']} | 🔁 {p['reposts']} | 💬 {p['replies']}")

    elif args.cmd == "farm":
        await farmer.login_all()
        keywords = args.keywords.split(",") if args.keywords else SEARCH_KEYWORDS[:3]
        keywords = [k.strip() for k in keywords]
        await farmer.farm(keywords, args.replies)

    elif args.cmd == "post":
        await farmer.login_all()
        handle = args.handle or farmer.get_random_account()
        if handle:
            result = await farmer.post(handle, args.content)
            if result:
                print(f"✅ 发帖成功: {result['uri']}")

    elif args.cmd == "like":
        await farmer.login_all()
        handle = farmer.get_random_account()
        if handle:
            if await farmer.like(handle, args.uri, ""):
                print("✅ 点赞成功!")

    elif args.cmd == "generate":
        # 生成内容
        content = await farmer.generate_post(args.persona, args.topic)
        print(f"\n📝 生成的内容 ({args.persona}):")
        print("-" * 40)
        print(content)
        print("-" * 40)


if __name__ == "__main__":
    asyncio.run(main())
