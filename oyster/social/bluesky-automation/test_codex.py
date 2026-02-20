#!/usr/bin/env python3
"""
Test Playwright on codex-node-1
"""

import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto("https://bsky.app")
        await page.wait_for_timeout(3000)

        print("Page title:", await page.title())

        await page.goto("https://bsky.app/settings")
        await page.wait_for_timeout(2000)

        text = await page.inner_text("body")
        print("Settings content:", text[:500])

        await browser.close()
        print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
