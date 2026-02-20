#!/usr/bin/env python3
"""
Click on Manage button to find account settings
"""

import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto("https://bsky.app/profile/bakerart.bsky.social")
        await page.wait_for_timeout(3000)

        print("Page title:", await page.title())

        # Try to find and click the "Manage" button
        # Look for it in the header/right side of the profile page
        try:
            # Try clicking on a button with "Manage" in it
            manage_btn = page.get_by_role(
                "button", name=lambda x: x and "manage" in x.lower()
            )
            if await manage_btn.count() > 0:
                print("Found Manage button, clicking...")
                await manage_btn.first.click()
                await page.wait_for_timeout(2000)

                print("After clicking Manage:")
                text = await page.inner_text("body")
                print(text[:1500])
            else:
                print("No Manage button found")
        except Exception as e:
            print(f"Error: {e}")

        await browser.close()
        print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
