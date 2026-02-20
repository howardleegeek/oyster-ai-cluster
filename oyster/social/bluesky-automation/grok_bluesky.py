#!/usr/bin/env python3
"""
Bluesky Content Generator using Grok via CDP
Reuses Twitter poster's CDP approach for content generation
"""

import asyncio
import sys
import os
import random
from pathlib import Path
from typing import Optional, Dict

# ========================
# Add twitter-poster to path (for CDP utilities)
# ========================

TWITTER_POSTER_PATH = "/Users/howardli/Downloads/twitter-poster"
if TWITTER_POSTER_PATH not in sys.path:
    sys.path.insert(0, TWITTER_POSTER_PATH)

# ========================
# Account Config
# ========================

ACCOUNTS = {
    "oysterecosystem": {
        "handle": "oysterecosystem.bsky.social",
        "app_password": "yjs3-a2gf-3j5s-guu7",
        "name": "Oyster Republic",
        "persona": "Nation Founder",
    },
    "clawglasses": {
        "handle": "clawglasses.bsky.social",
        "app_password": "lz2c-aexj-nlii-npzt",
        "name": "ClawGlasses",
        "persona": "Claw Operator",
    },
    "puffy": {
        "handle": "puffyai.bsky.social",
        "app_password": "d5wv-pzr2-37il-ed2d",
        "name": "Puffy AI",
        "persona": "Puffy AI Operator",
    },
}

# ========================
# Persona Prompts
# ========================

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

CONTENT_TYPE_PROMPTS = {
    "vision": "Share a visionary statement about the future we're building.",
    "question": "Ask an engaging question to spark discussion.",
    "daily": "Share what you did today - be casual and relatable.",
    "milestone": "Announce an achievement or milestone.",
    "feature": "Talk about a product feature or update.",
    "workflow": "Share a productivity workflow or automation tip.",
}

# ========================
# CDP/Grok Integration (from Twitter Poster)
# ========================


async def get_grok_page(cdp_port: int = 9222):
    """Get a page with Grok using CDP"""
    from playwright.async_api import async_playwright

    global _pw_instance, _pw_browser, _pw_cdp_port
    _pw_instance = None
    _pw_browser = None
    _pw_cdp_port = None

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{cdp_port}")
        ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        # Try x.com/grok first
        urls = [
            "https://x.com/i/grok",
            "https://x.com/grok",
            "https://grok.com",
        ]

        for url in urls:
            try:
                await page.goto(url, wait_until="domcontentloaded")
                await page.wait_for_timeout(2000)
                if "grok" in page.url:
                    break
            except:
                continue

        return page


async def generate_with_grok_via_cdp(
    account: str, content_type: str = "vision", topic: str = "", cdp_port: int = 9222
) -> Optional[str]:
    """Generate content using Grok via CDP"""

    persona_prompt = PERSONA_PROMPTS.get(account, PERSONA_PROMPTS["oysterecosystem"])
    type_prompt = CONTENT_TYPE_PROMPTS.get(content_type, "Share something interesting.")

    prompt = f"""{persona_prompt}

Generate a Bluesky post for @{ACCOUNTS[account]["handle"]}.
Content type: {content_type}
Topic: {topic if topic else "random"}

{type_prompt}

Requirements:
- 2-3 sentences maximum
- Under 280 characters
- Add 2-3 relevant hashtags
- Sound natural and human, NOT corporate
- Can include 1 emoji

Post:"""

    try:
        page = await get_grok_page(cdp_port)

        # Find input box
        input_locs = [
            page.locator("textarea"),
            page.get_by_role("textbox"),
            page.locator('[contenteditable="true"]'),
        ]

        input_box = None
        for loc in input_locs:
            try:
                if await loc.count() > 0:
                    cand = loc.filter(has_not_text="").last
                    await cand.click(timeout=3000)
                    input_box = cand
                    break
            except:
                try:
                    await loc.first.click(timeout=1000)
                    input_box = loc.first
                    break
                except:
                    continue

        if input_box is None:
            print("❌ Could not find input box")
            return None

        # Fill and send
        await input_box.fill("")
        await input_box.type(prompt, delay=10)

        # Click send
        sent = False
        for sel in [
            '[aria-label="Send"]',
            'button:has-text("Send")',
            'button:has-text("Ask")',
        ]:
            try:
                btn = page.locator(sel)
                if await btn.count() > 0:
                    await btn.first.click(timeout=3000)
                    sent = True
                    break
            except:
                pass

        if not sent:
            await page.keyboard.press("Enter")

        # Wait for response
        await page.wait_for_timeout(12000)

        # Take screenshot
        await page.screenshot(path=f"/tmp/bluesky_grok_{account}.png")
        print(f"📸 Screenshot saved: /tmp/bluesky_grok_{account}.png")

        return None  # User needs to copy from screenshot

    except Exception as e:
        print(f"❌ Grok generation error: {e}")
        return None


# ========================
# Fallback Templates
# ========================


def generate_fallback(account: str, content_type: str, topic: str) -> str:
    """Fallback template when CDP fails"""

    templates = {
        "oysterecosystem": [
            "We're building something unprecedented: a sovereign internet nation powered by Physical Intelligence + on-chain UBI + AI Hardware. 🦪\n\nJoin us → oysterrepublic.xyz",
            "UBI isn't charity - it's a protocol. We're turning survival into code.",
            "Why Physical Intelligence is the next frontier of AI: because AI needs eyes and hands.",
        ],
        "clawglasses": [
            "Day {} with ClawGlasses: wore them for {}. {} - here's what happened 🧿",
            "Took ClawGlasses for a walk - object recognition is getting better!",
            "The OTA update just dropped: faster response, new gestures. 🚀",
        ],
        "puffy": [
            "Good morning! Today's task list: 1. Answer emails 2. Summarize docs 3. Remind meetings. Let's go! 🤖",
            "Puffy day {}: I've accomplished {} tasks for my human. Productivity = {}x 📈",
            "Just learned a new trick! My human was impressed. 🎉",
        ],
    }

    account_templates = templates.get(account, templates["oysterecosystem"])
    template = random.choice(account_templates)

    hashtags = {
        "oysterecosystem": "#OysterRepublic #DePIN #PhysicalIntelligence",
        "clawglasses": "#ClawGlasses #OpenClaw #AIWearables",
        "puffy": "#PuffyAI #AIAgents #Automation",
    }

    result = template.format(
        random.randint(1, 100),
        random.choice(["grocery shopping", "a walk", "workout"]),
        random.choice(["it worked great", "needs improvement"]),
    )

    return f"{result}\n\n{hashtags.get(account, '#Bluesky')}"


# ========================
# Post to Bluesky
# ========================


async def post_to_bluesky(account: str, content: str) -> bool:
    """Post content to Bluesky"""
    try:
        from atproto import AsyncClient

        acc = ACCOUNTS[account]
        client = AsyncClient()
        await client.login(acc["handle"], acc["app_password"])

        result = await client.post(text=content)
        print(f"✅ Posted to {account}: {content[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Post failed: {e}")
        return False


# ========================
# CLI
# ========================


async def main():
    import argparse

    parser = argparse.ArgumentParser(description="Bluesky Content Generator with Grok")
    parser.add_argument(
        "--account", required=True, choices=["oysterecosystem", "clawglasses", "puffy"]
    )
    parser.add_argument("--type", default="vision")
    parser.add_argument("--topic", default="")
    parser.add_argument("--cdp-port", type=int, default=9222, help="CDP port for Grok")
    parser.add_argument(
        "--post", action="store_true", help="Post to Bluesky after generating"
    )
    parser.add_argument(
        "--fallback", action="store_true", help="Use fallback template only"
    )

    args = parser.parse_args()

    topic = args.topic or random.choice(
        ["UBI", "DePIN", "AI Hardware", "Physical Intelligence"]
    )

    print(f"\n🎨 Generating content...")
    print(f"   Account: {args.account}")
    print(f"   Type: {args.type}")
    print(f"   Topic: {topic}")
    print(f"   CDP Port: {args.cdp_port}")

    if args.fallback:
        content = generate_fallback(args.account, args.type, topic)
    else:
        # Try Grok via CDP
        print(f"\n🌐 Opening Grok via CDP...")
        result = await generate_with_grok_via_cdp(
            args.account, args.type, topic, args.cdp_port
        )

        if result:
            content = result
        else:
            print("⚠️ CDP generation needs manual input, using fallback...")
            content = generate_fallback(args.account, args.type, topic)

    print("\n" + "=" * 50)
    print("📝 Generated Content:")
    print("=" * 50)
    print(content)
    print()

    if args.post:
        print("📤 Posting to Bluesky...")
        await post_to_bluesky(args.account, content)


if __name__ == "__main__":
    asyncio.run(main())
