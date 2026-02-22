#!/usr/bin/env python3
"""
Login and generate App Password
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

        # Click Sign in
        signin_link = page.get_by_text("Sign in")
        await signin_link.click()
        await page.wait_for_timeout(3000)

        # Fill username
        await page.get_by_placeholder("Username or email address").fill(
            "clawglasses.bsky.social"
        )
        await page.get_by_role("button", name="Next").click()
        await page.wait_for_timeout(3000)

        # Fill password
        await page.get_by_placeholder("Password").fill("Howard@3503")
        await page.get_by_role("button", name="Next").click()
        await page.wait_for_timeout(5000)

        print("Logged in!")

        # Now go to privacy and security
        await page.goto("https://bsky.app/settings/privacy-and-security")
        await page.wait_for_timeout(3000)

        text = await page.inner_text("body")
        print("Page content:")
        print(text[:1500])

        await browser.close()
        print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
