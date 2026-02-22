#!/usr/bin/env python3
"""
Generate App Password for clawglasses
"""

import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Already logged in, go to privacy and security
        await page.goto("https://bsky.app/settings/privacy-and-security")
        await page.wait_for_timeout(3000)

        print("On privacy and security page")
        text = await page.inner_text("body")
        print(text[:1000])

        # Look for App Passwords
        if "app password" in text.lower():
            print("\n*** Found App Password option! ***")

        await browser.close()
        print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
