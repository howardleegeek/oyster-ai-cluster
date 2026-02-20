#!/usr/bin/env python3
"""
Navigate to profile page to find account switcher
"""

import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Go to the profile of the current user
        await page.goto("https://bsky.app/profile/bakerart.bsky.social")
        await page.wait_for_timeout(3000)

        print("Profile page title:", await page.title())

        # Look for the profile avatar/header area
        # Try to find "Manage account" or "Add account" buttons

        # Scroll down to find more elements
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)

        # Look for buttons with specific text
        texts = ["Add account", "Switch", "Manage", "Sign up", "Create"]

        for text in texts:
            try:
                elem = page.get_by_text(text, exact=False).first
                if await elem.count() > 0:
                    print(f"Found: {text}")
            except:
                pass

        # Also look at the bottom of the screen where the left nav is
        # Try to take a screenshot to see the layout
        await page.screenshot(path="/tmp/bluesky_profile.png")
        print("Screenshot saved to /tmp/bluesky_profile.png on mac2")

        # Now try to hover over the left bottom area (where user avatar usually is in Bluesky)
        # and look for the account switcher

        # Click on what might be the profile avatar
        try:
            # Look for avatar image
            avatar = page.locator("img[alt*='avatar'], img[aria-label*='avatar']").first
            if await avatar.count() > 0:
                print("Found avatar image")
        except Exception as e:
            print(f"Error: {e}")

        await browser.close()
        print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
