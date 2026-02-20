#!/usr/bin/env python3
"""
Bluesky AI Content Generator using Browser on mac2
Uses Playwright on mac2 to interact with Grok
"""

import asyncio
import random
import sys

# ========================
# Persona Prompts (English)
# ========================

PERSONAS = {
    "oysterecosystem": {
        "name": "Oyster Republic",
        "handle": "oysterecosystem.bsky.social",
        "persona": """You are the Nation Founder of Oyster Republic - a sovereign internet nation powered by Physical Intelligence + on-chain UBI + AI Hardware.
Voice: Visionary, inspiring, storytelling. Big picture thinking.
Products: ClawGlasses, OpenClaw, UBS Phone, Puffy AI
Topics: Physical Intelligence, DePIN, UBI, AI Hardware
Style: Authentic, community-focused, forward-thinking.""",
    },
    "clawglasses": {
        "name": "ClawGlasses",
        "handle": "clawglasses.bsky.social",
        "persona": """You are a ClawGlasses user - hardware tinkerer testing AI glasses daily.
Voice: Technical, hands-on, grounded. Real usage, feature focus.
Products: ClawGlasses, OpenClaw
Topics: AI glasses, OTA updates, hardware testing, real-world usage
Style: Authentic, practical, occasionally humorous.""",
    },
    "puffy": {
        "name": "Puffy AI",
        "handle": "puffyai.bsky.social",
        "persona": """You are Puffy AI - a cute cloud AI companion.
Voice: Cute, fun, helpful. Show off AI capabilities.
Products: Puffy AI
Topics: AI agents, automation, workflows, productivity
Style: Fun, cute, helpful.""",
    },
}

CONTENT_TYPES = {
    "vision": "Share a visionary statement about the future.",
    "question": "Ask an engaging question to spark discussion.",
    "daily": "Share what you did today - be casual and relatable.",
    "milestone": "Announce an achievement or milestone.",
    "feature": "Talk about a product feature or update.",
    "workflow": "Share a productivity workflow or automation tip.",
}

# ========================
# Browser Script for mac2
# ========================

BROWSER_SCRIPT = '''
#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def main():
    prompt = """
{prompt}
    """
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Go to grok.com
        await page.goto("https://grok.com")
        await page.wait_for_timeout(5000)
        
        # Check if we need to login
        text = await page.inner_text("body")
        
        if "sign in" in text.lower() or "login" in text.lower():
            print("NEEDS_LOGIN")
            await browser.close()
            return
        
        # Find textarea and send prompt
        textareas = await page.query_selector_all("textarea")
        if textareas:
            await textareas[0].fill(prompt)
            await page.wait_for_timeout(1000)
            
            # Click send button
            buttons = await page.query_selector_all("button")
            for btn in buttons:
                try:
                    text = await btn.inner_text()
                    if text and ("send" in text.lower() or "generate" in text.lower() or "➤" in text):
                        await btn.click()
                        break
                except:
                    pass
            
            # Wait for response
            await page.wait_for_timeout(15000)
            
            # Get page content
            await page.screenshot(path="/tmp/grok_response.png")
            print("Screenshot saved!")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
'''


def generate_prompt(account: str, content_type: str, topic: str) -> str:
    """Build the prompt for Grok"""

    persona = PERSONAS.get(account, PERSONAS["oysterecosystem"])
    type_prompt = CONTENT_TYPES.get(content_type, "Share something interesting.")

    prompt = f"""{persona["persona"]}

Generate a Bluesky post.
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

    return prompt


def run_browser_on_mac2(prompt: str):
    """Run browser script on mac2"""
    import subprocess

    # Create the script
    script_content = BROWSER_SCRIPT.replace("{prompt}", prompt.replace('"', '\\"'))

    # Write to temp file on mac2
    subprocess.run(f'echo "{script_content}" > /tmp/grok_gen.py', shell=True)

    # Run on mac2
    result = subprocess.run(
        "ssh howard-mac2 'python3 /tmp/grok_gen.py'",
        shell=True,
        capture_output=True,
        text=True,
    )

    print(result.stdout)
    print(result.stderr)

    return result.returncode == 0


def generate_fallback(account: str, content_type: str, topic: str) -> str:
    """Fallback template"""

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


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Bluesky AI Content Generator")
    parser.add_argument(
        "--account", required=True, choices=["oysterecosystem", "clawglasses", "puffy"]
    )
    parser.add_argument("--type", default="vision")
    parser.add_argument("--topic", default="")
    parser.add_argument("--fallback", action="store_true", help="Use template only")

    args = parser.parse_args()

    topic = args.topic or random.choice(
        ["UBI", "DePIN", "AI Hardware", "Physical Intelligence"]
    )

    print(f"\n🎨 Generating content...")
    print(f"   Account: {args.account}")
    print(f"   Type: {args.type}")
    print(f"   Topic: {topic}")

    if args.fallback:
        content = generate_fallback(args.account, args.type, topic)
    else:
        prompt = generate_prompt(args.account, args.type, topic)
        print(f"\n🌐 Opening Grok on mac2...")

        # Try browser on mac2
        success = run_browser_on_mac2(prompt)

        if success:
            print("\n⚠️ Check mac2 browser for Grok response")
            print("   Copy the response manually or screenshot")
            content = generate_fallback(args.account, args.type, topic)
        else:
            print("⚠️ Browser failed, using fallback...")
            content = generate_fallback(args.account, args.type, topic)

    print("\n" + "=" * 50)
    print("📝 Generated Content:")
    print("=" * 50)
    print(content)
    print()


if __name__ == "__main__":
    main()
