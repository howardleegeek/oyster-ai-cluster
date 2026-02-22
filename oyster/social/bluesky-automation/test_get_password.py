#!/usr/bin/env python3
"""
Click on opencode to see the password
"""

import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Login first
        await page.goto("https://bsky.app/settings")
        await page.wait_for_timeout(2000)

        signin_link = page.get_by_text("Sign in")
        await signin_link.click()
        await page.wait_for_timeout(3000)

        await page.get_by_placeholder("Username or email address").fill(
            "clawglasses.bsky.social"
        )
        await page.get_by_role("button", name="Next").click()
        await page.wait_for_timeout(3000)

        await page.get_by_placeholder("Password").fill("Howard@3503")
        await page.get_by_role("button", name="Next").click()
        await page.wait_for_timeout(5000)

        # Go to app passwords
        await page.goto("https://bsky.app/settings/app-passwords")
        await page.wait_for_timeout(3000)

        # Click on opencode
        opencode_link = page.get_by_text("opencode")
        await opencode_link.click()
        await page.wait_for_timeout(2000)

        # Take screenshot to see the password
        await page.screenshot(path="/tmp/app_password.png")
        print("Screenshot saved!")

        text = await page.inner_text("body")
        print("Page content:")
        print(text[:2000])

        await browser.close()
        print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
