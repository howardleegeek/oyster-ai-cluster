#!/usr/bin/env python3
"""
Debug verification step
"""

import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto("https://bsky.app/settings")
        await page.wait_for_timeout(2000)

        # Click Create account
        create_link = page.get_by_text("Create account")
        await create_link.first.click()
        await page.wait_for_timeout(3000)

        # Fill Step 1
        await page.get_by_label("Email").fill("howard.mba.apply@gmail.com")
        await page.get_by_label("Password").fill("Howard@3503")
        await page.get_by_role("button", name="Next").click()
        await page.wait_for_timeout(3000)

        # Fill username
        await page.get_by_placeholder(".bsky.social").fill("clawglasses")
        await page.get_by_role("button", name="Next").click()
        await page.wait_for_timeout(3000)

        print("On Step 3 - verification")

        # Get all page content
        text = await page.inner_text("body")
        print("Page content:")
        print(text)

        await page.screenshot(path="/tmp/bluesky_verify_debug.png")

        await browser.close()
        print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
