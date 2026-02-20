#!/usr/bin/env python3
"""
Bluesky Content & Engagement System
=================================
Unified system for Oyster Republic ecosystem
- Content generation (with templates)
- Engagement farming (search, like, reply)
- Scheduling (queue based)
- Multi-account management

Usage:
    python3 bluesky_system.py status
    python3 bluesky_system.py generate --account oysterecosystem --topic UBI
    python3 bluesky_system.py post --account oysterecosystem
    python3 bluesky_system.py farm --keywords "DePIN,AI Hardware"
    python3 bluesky_system.py schedule --add --time "09:00" --content "vision"
    python3 bluesky_system.py queue --run
"""

import os
import sys
import asyncio
import json
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import argparse

# ========================
# Configuration
# ========================

CONFIG_DIR = Path.home() / ".bluesky-system"
ACCOUNTS_FILE = CONFIG_DIR / "accounts.json"
QUEUE_FILE = CONFIG_DIR / "queue.json"
SCHEDULE_FILE = CONFIG_DIR / "schedule.json"
LOG_FILE = CONFIG_DIR / "activity.log"

# Peak hours (Beijing time)
PEAK_HOURS = [(8, 10), (12, 14), (18, 23)]

# Search keywords for farming
FARMING_KEYWORDS = [
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

# ========================
# Account Config
# ========================

ACCOUNTS = {
    "oysterecosystem": {
        "handle": "oysterecosystem.bsky.social",
        "app_password": "yjs3-a2gf-3j5s-guu7",
        "name": "Oyster Republic",
        "persona": "Nation Founder",
        "enabled": True,
    },
    "clawglasses": {
        "handle": "clawglasses.bsky.social",
        "app_password": "lz2c-aexj-nlii-npzt",
        "name": "ClawGlasses",
        "persona": "Claw Operator",
        "enabled": True,
    },
    "puffy": {
        "handle": "puffyai.bsky.social",
        "app_password": "d5wv-pzr2-37il-ed2d",
        "name": "Puffy AI",
        "persona": "Puffy AI Operator",
        "enabled": True,
    },
}

# ========================
# Content Templates (English)
# ========================

TEMPLATES = {
    "oysterecosystem": {
        "vision": [
            "We're building something unprecedented: a sovereign internet nation powered by Physical Intelligence + on-chain UBI + AI Hardware. 🦪\n\nJoin us → oysterrepublic.xyz",
            "UBI isn't charity - it's a protocol. We're turning survival into code. That's the vision.",
            "Why Physical Intelligence is the next frontier of AI: because AI needs eyes and hands to understand the physical world.",
            "The future we're building: where AI + blockchain + hardware converge to give everyone sovereignty over their digital life.",
        ],
        "question": [
            "What do you want Oyster Republic to achieve? Drop your thoughts below 👇",
            "What's your take on Physical Intelligence? Genuinely curious.",
            "If you could build anything with AI + hardware, what would it be?",
        ],
        "milestone": [
            "Big news: we just hit {N}! 🎉 Thank you for being part of this journey.",
            "Excited to share: {ACHIEVEMENT}! This is just the beginning.",
        ],
    },
    "clawglasses": {
        "usage": [
            "Day {N} with ClawGlasses: wore them for {ACTIVITY}. {RESULT}. Here's what happened 🧿",
            "Took ClawGlasses for a walk to test object recognition in {CONDITION}. Latency is now {N}ms - finally usable for real-time navigation.",
            "Wore ClawGlasses the whole day. Battery lasted {TIME}. Verdict: {OPINION}.",
        ],
        "feature": [
            "New OTA update just dropped. Here's what's new: {FEATURES}. 🚀",
            "The feature I've been waiting for is finally here: {FEATURE}. Testing now!",
        ],
        "question": [
            "What's the most unrealistic thing you want AI glasses to do? Mine: {ANSWER}.",
            "Real talk: what's holding AI glasses back? For me it's {ISSUE}.",
        ],
    },
    "puffy": {
        "daily": [
            "Good morning! Today's task list: 1. Answer emails 2. Summarize docs 3. Remind meetings. Let's go! 🤖",
            "Puffy day {N}: I've accomplished {TASKS} for my human today. Productivity = {N}x 📈",
            "Another day, another {TASKS} completed. Being an AI agent is hard work 😅",
        ],
        "skill": [
            "Just learned a new trick: {SKILL}. My human was {REACTION}! 🎉",
            "New skill unlocked: {SKILL}. I am evolving 🤖",
        ],
        "workflow": [
            "My secret workflow: {STEP1} → {STEP2} → {STEP3}. {RESULT}. Want me to share the full setup?"
        ],
    },
}

HASHTAGS = {
    "oysterecosystem": [
        "#OysterRepublic",
        "#DePIN",
        "#PhysicalIntelligence",
        "#UBI",
        "#AIHardware",
    ],
    "clawglasses": [
        "#ClawGlasses",
        "#OpenClaw",
        "#AIWearables",
        "#PhysicalIntelligence",
    ],
    "puffy": ["#PuffyAI", "#AIAgents", "#Automation", "#Productivity"],
}

# ========================
# Content Engine
# ========================


class ContentEngine:
    """Generates content based on templates"""

    def __init__(self):
        self.templates = TEMPLATES
        self.hashtags = HASHTAGS

    def generate(
        self, account: str, content_type: str = "general", topic: str = ""
    ) -> str:
        """Generate content for an account"""
        if account not in self.templates:
            account = "oysterecosystem"

        # Get templates
        account_templates = self.templates.get(account, {})
        if content_type in account_templates:
            templates = account_templates[content_type]
        else:
            # Flatten all templates
            templates = []
            for t in account_templates.values():
                templates.extend(t)

        if not templates:
            return f"Hello from {account}!"

        # Pick random template
        template = random.choice(templates)

        # Fill variables
        replacements = {
            "N": random.randint(1, 100),
            "TIME": f"{random.randint(1, 12)} hours",
            "RESULT": random.choice(
                ["it worked great", "needs improvement", "was hilarious"]
            ),
            "CONDITION": random.choice(["bright sunlight", "indoor lighting", "night"]),
            "ACTIVITY": random.choice(["grocery shopping", "a walk", "workout"]),
            "ISSUE": random.choice(["battery life", "weight", "price"]),
            "ANSWER": random.choice(["they don't exist yet", "instant translation"]),
            "FEATURE": random.choice(
                ["real-time translation", "gesture control", "voice commands"]
            ),
            "FEATURES": "faster response, new gesture controls",
            "TASKS": f"{random.randint(5, 50)} tasks",
            "SKILL": random.choice(
                ["reading handwriting", "summarizing docs", "scheduling"]
            ),
            "REACTION": random.choice(["impressed", "surprised", "happy"]),
            "STEP1": "check emails",
            "STEP2": "summarize",
            "STEP3": "prioritize",
            "RESULT2": "automation at its finest",
            "ACHIEVEMENT": "major feature launch",
            "OPINION": "game changer",
        }

        for key, value in replacements.items():
            template = template.replace(f"{{{key}}}", str(value))

        # Add hashtags
        tags = self.hashtags.get(account, ["#Bluesky"])
        selected = random.sample(tags, min(3, len(tags)))
        template = f"{template}\n\n{' '.join(selected)}"

        return template

    def generate_variations(
        self, account: str, content_type: str, count: int = 3
    ) -> List[str]:
        """Generate multiple variations"""
        return [self.generate(account, content_type) for _ in range(count)]


# ========================
# Bluesky Client
# ========================


class BlueskyPoster:
    """Posts to Bluesky"""

    def __init__(self):
        self.accounts = ACCOUNTS
        self.clients = {}

    async def login(self, account: str) -> bool:
        if account not in self.accounts:
            return False

        if account in self.clients:
            return True

        try:
            from atproto import AsyncClient

            acc = self.accounts[account]
            client = AsyncClient()
            await client.login(acc["handle"], acc["app_password"])
            self.clients[account] = client
            print(f"✅ Logged in: {account}")
            return True
        except Exception as e:
            print(f"❌ Login failed: {account} - {e}")
            return False

    async def post(self, account: str, content: str) -> bool:
        """Post content"""
        if account not in self.clients:
            await self.login(account)

        try:
            client = self.clients[account]
            result = await client.post(text=content)
            print(f"✅ Posted: {account}")
            print(f"   {content[:80]}...")
            return True
        except Exception as e:
            print(f"❌ Post failed: {account} - {e}")
            return False

    async def like(self, account: str, uri: str, cid: str) -> bool:
        """Like a post"""
        if account not in self.clients:
            await self.login(account)

        try:
            client = self.clients[account]
            await client.like(uri, cid)
            print(f"✅ Liked: {account}")
            return True
        except Exception as e:
            print(f"❌ Like failed: {e}")
            return False

    async def search(self, account: str, keyword: str, limit: int = 20) -> List[Dict]:
        """Search posts"""
        if account not in self.clients:
            await self.login(account)

        try:
            client = self.clients[account]
            results = await client.app.bsky.feed.search_posts(
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
                    }
                )
            return posts
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []


# ========================
# Queue & Schedule
# ========================


@dataclass
class QueueItem:
    id: str
    account: str
    content: str
    content_type: str
    topic: str
    status: str  # pending, running, completed, failed
    created_at: str
    run_at: str
    result: str = ""


class QueueManager:
    """Manages post queue and scheduling"""

    def __init__(self):
        self.queue_file = QUEUE_FILE
        self.schedule_file = SCHEDULE_FILE
        self.queue = self._load_queue()
        self.schedule = self._load_schedule()

    def _load_queue(self) -> List[Dict]:
        if self.queue_file.exists():
            with open(self.queue_file) as f:
                return json.load(f)
        return []

    def _save_queue(self):
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.queue_file, "w") as f:
            json.dump(self.queue, f, indent=2)

    def _load_schedule(self) -> List[Dict]:
        if self.schedule_file.exists():
            with open(self.schedule_file) as f:
                return json.load(f)
        return []

    def _save_schedule(self):
        self.schedule_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.schedule_file, "w") as f:
            json.dump(self.schedule, f, indent=2)

    def add_to_queue(
        self,
        account: str,
        content: str,
        content_type: str = "general",
        topic: str = "",
        run_at: str = None,
    ) -> str:
        """Add item to queue"""
        item = {
            "id": f"q_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "account": account,
            "content": content,
            "content_type": content_type,
            "topic": topic,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "run_at": run_at or datetime.now().isoformat(),
            "result": "",
        }
        self.queue.append(item)
        self._save_queue()
        return item["id"]

    def get_pending(self) -> List[Dict]:
        """Get pending items"""
        now = datetime.now().isoformat()
        return [
            q for q in self.queue if q["status"] == "pending" and q["run_at"] <= now
        ]

    def mark_completed(self, item_id: str, result: str = "success"):
        """Mark item as completed"""
        for q in self.queue:
            if q["id"] == item_id:
                q["status"] = "completed"
                q["result"] = result
        self._save_queue()

    def add_schedule(self, time: str, account: str, content_type: str, topic: str = ""):
        """Add scheduled task"""
        item = {
            "id": f"s_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "time": time,
            "account": account,
            "content_type": content_type,
            "topic": topic,
            "enabled": True,
        }
        self.schedule.append(item)
        self._save_schedule()
        return item["id"]

    def list_schedule(self) -> List[Dict]:
        return self.schedule

    def list_queue(self) -> List[Dict]:
        return self.queue


# ========================
# Main System
# ========================


class BlueskySystem:
    def __init__(self):
        self.content = ContentEngine()
        self.poster = BlueskyPoster()
        self.queue = QueueManager()

    async def generate_and_post(
        self,
        account: str,
        content_type: str = "general",
        topic: str = "",
        post: bool = True,
    ) -> str:
        """Generate content and optionally post"""
        content = self.content.generate(account, content_type, topic)

        if post:
            success = await self.poster.post(account, content)
            if success:
                return content
            return ""
        return content

    async def run_queue(self):
        """Run pending queue items"""
        pending = self.queue.get_pending()
        print(f"\n📋 Running queue: {len(pending)} items")

        for item in pending:
            print(f"\n▶ Running: {item['id']}")
            success = await self.poster.post(item["account"], item["content"])
            if success:
                self.queue.mark_completed(item["id"], "success")
            else:
                self.queue.mark_completed(item["id"], "failed")
            await asyncio.sleep(2)

        print(f"\n✅ Queue run complete")

    async def farm(self, keywords: List[str], replies_per_keyword: int = 3):
        """Run engagement farming"""
        print(f"\n🌾 Starting farming: {keywords}")

        # Login all accounts
        for account in ACCOUNTS:
            if ACCOUNTS[account]["enabled"]:
                await self.poster.login(account)

        for keyword in keywords:
            print(f"\n🔍 Searching: {keyword}")
            posts = await self.poster.search("oysterecosystem", keyword, 20)

            if not posts:
                print(f"  No posts found")
                continue

            # Sort by likes
            posts.sort(key=lambda x: x["likes"], reverse=True)
            top = posts[:replies_per_keyword]

            # Pick random account
            account = random.choice(list(ACCOUNTS.keys()))

            for post in top:
                # Like
                await self.poster.like(account, post["uri"], post["cid"])
                print(f"  ❤️ Liked: @{post['author']}")
                await asyncio.sleep(1)

        print(f"\n✅ Farming complete")


# ========================
# CLI
# ========================


async def main():
    parser = argparse.ArgumentParser(description="Bluesky Content & Engagement System")
    sub = parser.add_subparsers(dest="cmd")

    # status
    sub.add_parser("status", help="System status")

    # generate
    g = sub.add_parser("generate", help="Generate content")
    g.add_argument("--account", required=True)
    g.add_argument("--type", default="general")
    g.add_argument("--topic", default="")
    g.add_argument("--count", type=int, default=1)

    # post
    p = sub.add_parser("post", help="Generate and post")
    p.add_argument("--account", required=True)
    p.add_argument("--type", default="general")
    p.add_argument("--topic", default="")

    # farm
    f = sub.add_parser("farm", help="Run farming")
    f.add_argument("--keywords", default="DePIN,AI Hardware")
    f.add_argument("--replies", type=int, default=3)

    # queue
    q = sub.add_parser("queue", help="Queue operations")
    q.add_argument("--run", action="store_true", help="Run queue")
    q.add_argument("--list", action="store_true", help="List queue")
    q.add_argument("--clear", action="store_true", help="Clear completed")

    # schedule
    s = sub.add_parser("schedule", help="Schedule operations")
    s.add_argument("--add", action="store_true", help="Add schedule")
    s.add_argument("--list", action="store_true", help="List schedules")
    s.add_argument("--time", default="09:00", help="Time (HH:MM)")
    s.add_argument("--account", default="oysterecosystem")
    s.add_argument("--type", default="vision")
    s.add_argument("--topic", default="")

    args = parser.parse_args()

    if not args.cmd:
        parser.print_help()
        return

    system = BlueskySystem()

    if args.cmd == "status":
        print("\n📊 Bluesky System Status")
        print("=" * 50)
        print(f"\n📋 Queue: {len(system.queue.list_queue())} items")
        print(f"📅 Schedule: {len(system.queue.list_schedule())} items")
        print(f"\n👥 Accounts:")
        for name, acc in ACCOUNTS.items():
            status = "✅" if acc["enabled"] else "❌"
            print(f"  {status} {name} (@{acc['handle']})")

    elif args.cmd == "generate":
        for i in range(args.count):
            content = system.content.generate(args.account, args.type, args.topic)
            print(f"\n📝 [{args.account}] {args.type}")
            print("-" * 40)
            print(content)
            print()

    elif args.cmd == "post":
        content = await system.generate_and_post(
            args.account, args.type, args.topic, post=True
        )
        if content:
            print(f"\n✅ Posted successfully!")

    elif args.cmd == "farm":
        keywords = [k.strip() for k in args.keywords.split(",")]
        await system.farm(keywords, args.replies)

    elif args.cmd == "queue":
        if args.run:
            await system.run_queue()
        elif args.list:
            print("\n📋 Queue:")
            for item in system.queue.list_queue():
                print(f"  {item['id']}: {item['account']} - {item['status']}")

    elif args.cmd == "schedule":
        if args.add:
            system.queue.add_schedule(args.time, args.account, args.type, args.topic)
            print(f"✅ Added schedule: {args.time} - {args.account}/{args.type}")
        elif args.list:
            print("\n📅 Schedules:")
            for s in system.queue.list_schedule():
                print(f"  {s['time']} → {s['account']} ({s['content_type']})")


if __name__ == "__main__":
    asyncio.run(main())
