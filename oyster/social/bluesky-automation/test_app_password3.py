#!/usr/bin/env python3
"""
Click on App passwords and create one
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

        # Go to privacy and security
        await page.goto("https://bsky.app/settings/privacy-and-security")
        await page.wait_for_timeout(3000)

        # Click on "App passwords"
        app_pw_link = page.get_by_text("App passwords")
        await app_pw_link.click()
        await page.wait_for_timeout(3000)

        print("On App passwords page")
        text = await page.inner_text("body")
        print(text[:1500])

        await browser.close()
        print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
