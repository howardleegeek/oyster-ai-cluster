#!/usr/bin/env python3
"""
Fill in username (handle) in Bluesky registration
"""

import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Go to create account - start fresh
        await page.goto("https://bsky.app/settings")
        await page.wait_for_timeout(2000)

        # Click Create account
        create_link = page.get_by_text("Create account")
        await create_link.first.click()
        await page.wait_for_timeout(3000)

        # Fill Step 1
        await page.get_by_label("Email").fill("howard.mba.apply@gmail.com")
        await page.get_by_label("Password").fill("Howard@3503")

        # Click Next
        await page.get_by_role("button", name="Next").click()
        await page.wait_for_timeout(3000)

        print("On Step 2 - username")

        # Fill in username/handle
        username_input = page.get_by_label("Username")
        await username_input.fill("clawglasses")
        await page.wait_for_timeout(2000)

        # Check if there's a confirmation or Next button
        await page.screenshot(path="/tmp/bluesky_step2.png")

        # Click Next
        next_btn = page.get_by_role("button", name="Next")
        await next_btn.click()
        await page.wait_for_timeout(3000)

        print("After Step 2:")
        text = await page.inner_text("body")
        print(text[:1500])

        await browser.close()
        print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
