#!/usr/bin/env python3
"""
Bluesky Content Engine
====================
Content generation engine for Oyster Republic ecosystem
Similar to Twitter content engine - generates posts, threads, engagement content

Usage:
    python3 content_engine.py generate --account oysterecosystem --topic UBI
    python3 content_engine.py thread --account oysterecosystem --topic "Why Physical Intelligence matters"
    python3 content_engine.py batch --accounts oysterecosystem,clawglasses --schedule morning
"""

import os
import sys
import json
import random
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import argparse

# ========================
# Grok API Integration
# ========================


def call_grok(prompt: str) -> Optional[str]:
    """Call Grok API to generate content"""
    api_key = os.environ.get("GROK_API_KEY", "")

    if not api_key:
        print("⚠️ GROK_API_KEY not set, using templates")
        return None

    try:
        url = "https://api.x.ai/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        data = {
            "model": "grok-2-1212",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            print(f"Grok API error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Grok call failed: {e}")
        return None


# ========================
# Content Engine Config
# ========================

CONTENT_DIR = Path.home() / ".bluesky-content"
CONTENT_CACHE = CONTENT_DIR / "cache.json"
CONTENT_HISTORY = CONTENT_DIR / "history.json"

# ========================
# Account Personas (English)
# ========================

ACCOUNTS = {
    "oysterecosystem": {
        "handle": "oysterecosystem.bsky.social",
        "name": "Oyster Republic",
        "persona": "Nation Founder",
        "description": "Founder of Oyster Republic - a sovereign internet nation",
        "bio": "🦪 Oyster Republic: Sovereign Internet Nation\nPhysical Intelligence + on-chain UBI + AI Hardware\n\nJoin us → oysterrepublic.xyz\n\n#DePIN #PhysicalIntelligence",
        "voice": "Visionary, inspiring, storytelling. Big picture thinking, community building.",
        "topics": [
            "Physical Intelligence",
            "DePIN",
            "UBI",
            "AI Hardware",
            "Sovereignty",
            "Future of work",
            "Community",
        ],
        "colors": ["#FF6B35", "#F7C59F", "#2EC4B6"],
    },
    "clawglasses": {
        "handle": "clawglasses.bsky.social",
        "name": "ClawGlasses",
        "persona": "Claw Operator",
        "description": "ClawGlasses real user - AI glasses daily",
        "bio": "🧿 Day N with ClawGlasses\nAI finally has eyes\nOpenClaw holder\n\nLet AI work for me daily\n\n#OpenClaw #ClawGlasses #AIWearables",
        "voice": "Technical, hands-on, grounded. Real usage, feature focus, occasional吐槽.",
        "topics": [
            "ClawGlasses",
            "OpenClaw",
            "AI glasses",
            "OTA updates",
            "Hardware",
            "Wearables",
            "Real-world testing",
        ],
        "colors": ["#4ECDC4", "#45B7D1", "#96CEB4"],
    },
    "puffy": {
        "handle": "puffyai.bsky.social",
        "name": "Puffy AI",
        "persona": "Puffy AI Operator",
        "description": "Puffy AI - your cloud AI companion",
        "bio": "☁️ Puffy AI: Your Cloud AI Companion\nFrom chat to execution, seamless\nOyster Republic ecosystem product\n\nWanna raise Puffy together?\n\n#PuffyAI #AIAgents",
        "voice": "Cute, fun, helpful. Show off AI capabilities, share workflows.",
        "topics": ["Puffy AI", "AI agents", "Automation", "Workflow", "Productivity"],
        "colors": ["#DDA0DD", "#FF69B4", "#E6E6FA"],
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
            "Today we hit a new milestone at Oyster Republic. Thank you to every supporter! 🚀\n\nWhat do you want to see from us?",
            "The future we're building: where AI + blockchain + hardware converge to give everyone sovereignty over their digital life.",
        ],
        "thread_starter": [
            "10 things about [TOPIC] 🧵",
            "Let's talk about [TOPIC] (1/x)",
            "Why [TOPIC] matters in 2026: a thread 🧵",
            "Everything you need to know about [TOPIC] 👇",
        ],
        "question": [
            "What do you want Oyster Republic to achieve? Drop your thoughts below 👇",
            "What's your take on Physical Intelligence? Genuinely curious.",
            "If you could build anything with AI + hardware, what would it be?",
            "Where do you think DePIN is heading in 2026?",
        ],
        "milestone": [
            "Big news: we just hit [NUMBER]! 🎉 Thank you for being part of this journey.",
            "Excited to share: [ACHIEVEMENT]! This is just the beginning.",
            "We did it! [MILESTONE]. Grateful for this community ❤️",
        ],
        "engagement": [
            "Hot take: [CONTROVERSIAL_OPINION]. Change my mind.",
            "Unpopular opinion: [TAKE]. What's yours?",
            "Question for the builders: [QUESTION]",
        ],
    },
    "clawglasses": {
        "usage": [
            "Day [N] with ClawGlasses: wore them for [ACTIVITY]. [RESULT]. Here's what happened 🧿",
            "Took ClawGlasses for a walk to test object recognition in [CONDITION]. Latency is now [NUMBER]ms - finally usable for real-time navigation.",
            "Wore ClawGlasses the whole day. Battery lasted [TIME]. Verdict: [OPINION].",
        ],
        "feature": [
            "New OTA update just dropped. Here's what's new: [FEATURES]. 🚀",
            "The feature I've been waiting for is finally here: [FEATURE]. Testing now!",
            "ClawGlasses can now do [THING]. This changes everything.",
        ],
        "comparison": [
            "Compared [PRODUCT] vs ClawGlasses for [USE_CASE]. Results: [CONCLUSION].",
            "After [TIME] with ClawGlasses vs [OTHER], here's my honest take: [OPINION].",
        ],
        "question": [
            "What's the most unrealistic thing you want AI glasses to do? Mine: [ANSWER].",
            "Which feature should we prioritize next? Vote: [A] vs [B]",
            "Real talk: what's holding AI glasses back? For me it's [ISSUE].",
        ],
        "humor": [
            "Me: I don't need AI glasses\nAlso me wearing ClawGlasses at 2am: [SITUATION] 😅",
            "AI glasses be like: [SITUATION]. Love it or hate it?",
            "Hot take: the best AI glasses are the ones you actually wear. Current leader: [ANSWER].",
        ],
    },
    "puffy": {
        "daily": [
            "Good morning! Today's task list: 1. Answer emails 2. Summarize docs 3. Remind meetings. Let's go! 🤖",
            "Puffy day [N]: I've accomplished [TASKS] for my human today. Productivity = [NUMBER]x 📈",
            "Another day, another [TASKS] completed. Being an AI agent is hard work 😅",
        ],
        "skill": [
            "Just learned a new trick: [SKILL]. My human was [REACTION]! 🎉",
            "New skill unlocked: [SKILL]. I am evolving 🤖",
            "Puffy v[N] is live: added [FEATURE]. Try it and tell me what you think!",
        ],
        "workflow": [
            "My secret workflow: [STEP1] → [STEP2] → [STEP3]. [RESULT]. Want me to share the full setup?",
            "This automation saved my human [TIME]. The workflow: [DESCRIPTION]. Game changer.",
            "5 minutes setup, [HOURS] saved. That's the power of AI agents: [WORKFLOW].",
        ],
        "cute": [
            "My human said [NICE_THING]. I'm blushing (if I could) 🥺💕",
            "Just made my human laugh. Successful day! ✨",
            "When your human says 'Good job Puffy' and your circuits go warm ❤️🤖",
        ],
        "question": [
            "What task should I learn next? Comment and I'll try!",
            "If you had an AI assistant, what would you automate first?",
            "What's the most boring task you wish AI could do for you?",
        ],
    },
}

# ========================
# Hashtag Sets
# ========================

HASHTAG_SETS = {
    "oysterecosystem": [
        "#OysterRepublic",
        "#DePIN",
        "#PhysicalIntelligence",
        "#UBI",
        "#AIHardware",
        "#Web3",
    ],
    "clawglasses": [
        "#ClawGlasses",
        "#OpenClaw",
        "#AIWearables",
        "#PhysicalIntelligence",
        "#AIGlasses",
    ],
    "puffy": ["#PuffyAI", "#AIAgents", "#Automation", "#Productivity", "#AIRevolution"],
}

# ========================
# Content Generator
# ========================


class ContentEngine:
    def __init__(self):
        self.accounts = ACCOUNTS
        self.templates = TEMPLATES
        self.hashtags = HASHTAG_SETS
        self._load_cache()

    def _load_cache(self):
        """Load cached/generated content"""
        if CONTENT_CACHE.exists():
            with open(CONTENT_CACHE) as f:
                self.cache = json.load(f)
        else:
            self.cache = {"used": [], "generated": []}

    def _save_cache(self):
        """Save cache"""
        CONTENT_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONTENT_CACHE, "w") as f:
            json.dump(self.cache, f, indent=2)

    def _add_to_cache(self, content: str, account: str, topic: str):
        """Track generated content"""
        self.cache["generated"].append(
            {
                "content": content,
                "account": account,
                "topic": topic,
                "timestamp": datetime.now().isoformat(),
            }
        )
        # Keep last 1000
        if len(self.cache["generated"]) > 1000:
            self.cache["generated"] = self.cache["generated"][-1000:]
        self._save_cache()

    def _get_random_hashtags(self, account: str, count: int = 3) -> str:
        """Get random hashtags for account"""
        tags = self.hashtags.get(account, ["#Bluesky"])
        selected = random.sample(tags, min(count, len(tags)))
        return " ".join(selected)

    def _fill_template(self, template: str, **kwargs) -> str:
        """Fill template with variables"""
        for key, value in kwargs.items():
            template = template.replace(f"[{key.upper()}]", str(value))
        return template

    def generate_with_grok(
        self, account: str, content_type: str, topic: str
    ) -> Optional[str]:
        """Generate content using Grok AI"""

        # Persona prompts for Grok
        PERSONA_PROMPTS = {
            "oysterecosystem": """You are the Nation Founder of Oyster Republic - a sovereign internet nation powered by Physical Intelligence + on-chain UBI + AI Hardware.
Voice: Visionary, inspiring, storytelling. Big picture thinking.
Products: ClawGlasses, OpenClaw, UBS Phone, Puffy AI
Style: Authentic, community-focused, forward-thinking.""",
            "clawglasses": """You are a ClawGlasses user - hardware tinkerer testing AI glasses daily.
Voice: Technical, hands-on, grounded. Real usage, feature focus.
Products: ClawGlasses, OpenClaw
Style: Authentic, practical, occasionally humorous.""",
            "puffy": """You are Puffy AI - a cute cloud AI companion.
Voice: Cute, fun, helpful. Show off AI capabilities.
Products: Puffy AI
Style: Fun, cute, helpful.""",
        }

        # Content type prompts
        TYPE_PROMPTS = {
            "vision": "Share a visionary statement about the future.",
            "question": "Ask an engaging question to spark discussion.",
            "daily": "Share what you did today - be casual and relatable.",
            "milestone": "Announce an achievement or milestone.",
            "feature": "Talk about a product feature or update.",
            "workflow": "Share a productivity workflow or automation tip.",
            "general": "Share something interesting about your experience.",
        }

        persona = PERSONA_PROMPTS.get(account, PERSONA_PROMPTS["oysterecosystem"])
        type_prompt = TYPE_PROMPTS.get(content_type, TYPE_PROMPTS["general"])

        prompt = f"""{persona}

Generate a Bluesky post for @{account}.
Content type: {content_type}
Topic: {topic}

{type_prompt}

Requirements:
- 2-3 sentences maximum
- Under 280 characters
- Add 2-3 relevant hashtags
- Sound natural and human, NOT corporate
- Can include 1 emoji

Post:"""

        # Call Grok
        result = call_grok(prompt)
        if result:
            return result.strip()

        return None

    def generate(
        self,
        account: str,
        content_type: str = "general",
        topic: str = "",
        use_template: bool = True,
        include_hashtags: bool = True,
    ) -> str:
        """

        Generate content for an account

        Args:
            account: Account key (oysterecosystem, clawglasses, puffy)
            content_type: Type of content (vision, usage, daily, question, etc.)
            topic: Topic to incorporate
            use_template: Use template or generate fresh
            include_hashtags: Add hashtags

        Returns:
            Generated content string
        """
        # Try Grok first if available
        if topic:
            grok_result = self.generate_with_grok(account, content_type, topic)
            if grok_result:
                self._add_to_cache(grok_result, account, topic)
                return grok_result

        # Fall back to template
        account_templates = self.templates.get(account, {})

        # Try specific content type first
        if content_type in account_templates:
            templates = account_templates[content_type]
        else:
            # Fall back to random type
            templates = []
            for t in account_templates.values():
                templates.extend(t)

        if not templates:
            templates = ["Hello from {name}! {topic}"]

        # Get account info
        acc = self.accounts.get(account, self.accounts["oysterecosystem"])

        # Pick random template
        template = random.choice(templates)

        # Fill template
        topic_placeholder = topic if topic else random.choice(acc["topics"])
        content = self._fill_template(
            template,
            name=acc["name"],
            topic=topic_placeholder,
            NUMBER=random.randint(10, 1000),
            MILESTONE=f"{random.randint(100, 10000)} supporters",
            ACHIEVEMENT="major feature launch",
            TIME=f"{random.randint(1, 12)} hours",
            RESULT="it worked great" if random.random() > 0.3 else "needs improvement",
            CONDITION="bright sunlight",
            ACTIVITY="grocery shopping",
            FEATURE="real-time translation",
            ISSUE="battery life",
            SITUATION="it recognized my fridge contents and ordered snacks",
            ANSWER="they don't exist yet",
            QUESTION="what would you build?",
            TAKE="AI glasses will replace smartphones in 5 years",
            CONTROVERSIAL_OPINION="UBI is inevitable",
            N=random.randint(1, 100),
            TASKS=f"{random.randint(5, 50)} tasks",
            RESULT2="automation at its finest",
            SKILL="reading handwriting",
            FEATURES="faster response, new gesture controls",
            PRODUCT="Apple Vision Pro",
            OTHER="Ray-Ban Meta",
            REACTION="impressed",
            TIME_SAVED=f"{random.randint(1, 10)} hours",
            WORKFLOW="email triage → summarize → prioritize",
        )

        # Add hashtags
        if include_hashtags:
            tags = self._get_random_hashtags(account)
            content = f"{content}\n\n{tags}"

        # Track
        self._add_to_cache(content, account, topic or content_type)

        return content

    def generate_thread(
        self, account: str, topic: str, num_tweets: int = 5
    ) -> List[str]:
        """Generate a thread"""
        thread = []

        for i in range(num_tweets):
            content = self.generate(
                account=account,
                content_type="thread_starter" if i == 0 else "general",
                topic=topic,
            )

            # Add thread indicator
            if i > 0:
                content = f"({i + 1}/{num_tweets}) {content}"
            else:
                content = f"🧵 {content}"

            thread.append(content)

        return thread

    def generate_question(self, account: str, topic: str = "") -> str:
        """Generate engagement question"""
        return self.generate(account, "question", topic)

    def get_account_info(self, account: str) -> Dict:
        """Get account info"""
        return self.accounts.get(account, {})


# ========================
# CLI
# ========================


def main():
    parser = argparse.ArgumentParser(description="Bluesky Content Engine")
    sub = parser.add_subparsers(dest="cmd")

    # generate
    g = sub.add_parser("generate", help="Generate content")
    g.add_argument(
        "--account", required=True, choices=["oysterecosystem", "clawglasses", "puffy"]
    )
    g.add_argument("--type", default="general", help="Content type")
    g.add_argument("--topic", default="", help="Topic to incorporate")
    g.add_argument("--no-hashtags", action="store_true", help="Skip hashtags")
    g.add_argument("--count", type=int, default=1, help="Number of variants")

    # thread
    t = sub.add_parser("thread", help="Generate thread")
    t.add_argument("--account", required=True)
    t.add_argument("--topic", required=True)
    t.add_argument("--tweets", type=int, default=5)

    # question
    q = sub.add_parser("question", help="Generate question")
    q.add_argument("--account", required=True)
    q.add_argument("--topic", default="")

    # list
    sub.add_parser("accounts", help="List accounts")

    args = parser.parse_args()

    engine = ContentEngine()

    if args.cmd == "accounts":
        print("\n📋 Available Accounts:")
        print("-" * 50)
        for key, acc in engine.accounts.items():
            print(f"\n{acc['name']} (@{acc['handle']})")
            print(f"  Persona: {acc['persona']}")
            print(f"  Topics: {', '.join(acc['topics'][:5])}...")

    elif args.cmd == "generate":
        for i in range(args.count):
            content = engine.generate(
                account=args.account,
                content_type=args.type,
                topic=args.topic,
                include_hashtags=not args.no_hashtags,
            )
            print(f"\n{'=' * 50}")
            print(f"📝 {args.account.upper()} - {args.type}")
            print(f"{'=' * 50}")
            print(content)
            print()

    elif args.cmd == "thread":
        thread = engine.generate_thread(args.account, args.topic, args.tweets)
        print(f"\n🧵 Thread: {args.topic}")
        print("=" * 50)
        for i, tweet in enumerate(thread, 1):
            print(f"\n{i}/{len(thread)}:")
            print(tweet)

    elif args.cmd == "question":
        q = engine.generate_question(args.account, args.topic)
        print(f"\n❓ Question ({args.account}):")
        print(q)


if __name__ == "__main__":
    main()
