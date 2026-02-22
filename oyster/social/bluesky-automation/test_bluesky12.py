#!/usr/bin/env python3
"""
Check the verification page and try to resend
"""

import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Go to create account - try to continue from where we left off
        # Bluesky might have saved the session
        await page.goto("https://bsky.app")
        await page.wait_for_timeout(3000)

        print("Current page:", await page.title())

        text = await page.inner_text("body")
        print("Page content:", text[:1000])

        # Check if we're still in the verification step
        if (
            "verification" in text.lower()
            or "code" in text.lower()
            or "email" in text.lower()
        ):
            print("\n=== Still on verification step ===")

        # Try to go to settings again to see if we can continue
        await page.goto("https://bsky.app/settings")
        await page.wait_for_timeout(2000)

        print("\nAfter going to settings:")
        text = await page.inner_text("body")
        print(text[:1000])

        await browser.close()
        print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
