#!/usr/bin/env python3
"""
Click Create account link
"""

import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto("https://bsky.app/settings")
        await page.wait_for_timeout(3000)

        print("Page title:", await page.title())

        # Try to click on text "Create account"
        try:
            create_link = page.get_by_text("Create account")
            if await create_link.count() > 0:
                print("Found 'Create account', clicking...")
                await create_link.first.click()
                await page.wait_for_timeout(3000)

                print("After click - Title:", await page.title())
                text = await page.inner_text("body")
                print("Content:", text[:2000])

                await page.screenshot(path="/tmp/bluesky_create2.png")
                print("\nScreenshot saved!")
        except Exception as e:
            print(f"Error: {e}")

        await browser.close()
        print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
