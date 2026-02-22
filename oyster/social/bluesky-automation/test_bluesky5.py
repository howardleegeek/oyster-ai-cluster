#!/usr/bin/env python3
"""
Go directly to settings to manage accounts
"""

import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Go to settings
        await page.goto("https://bsky.app/settings")
        await page.wait_for_timeout(3000)

        print("Settings page title:", await page.title())

        # Get all the text on the page to understand the structure
        text = await page.inner_text("body")
        print("Page content:")
        print(text[:2000])

        # Look for "Add account" or similar
        if "Add account" in text or "add account" in text.lower():
            print("\n*** Found Add account option! ***")

        await page.screenshot(path="/tmp/bluesky_settings.png")
        print("\nScreenshot saved to /tmp/bluesky_settings.png")

        await browser.close()
        print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
