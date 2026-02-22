#!/usr/bin/env python3
"""
Try to login with the new account
"""

import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Try to login with clawglasses
        await page.goto("https://bsky.app")
        await page.wait_for_timeout(2000)

        # Click Sign in
        await page.goto("https://bsky.app/settings")
        await page.wait_for_timeout(2000)

        # Click Sign in
        signin_link = page.get_by_text("Sign in")
        await signin_link.click()
        await page.wait_for_timeout(3000)

        print("On sign in page")
        text = await page.inner_text("body")
        print(text[:1000])

        # Try to find username input
        inputs = await page.query_selector_all("input")
        print(f"\nFound {len(inputs)} inputs")

        for i, inp in enumerate(inputs):
            try:
                placeholder = await inp.get_attribute("placeholder")
                print(f"Input {i}: placeholder={placeholder}")
            except:
                pass

        await browser.close()
        print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
