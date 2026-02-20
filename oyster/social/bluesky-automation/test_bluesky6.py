#!/usr/bin/env python3
"""
Try to create a new account on Bluesky
"""

import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Go to settings (which shows create account)
        await page.goto("https://bsky.app/settings")
        await page.wait_for_timeout(3000)

        print("Page title:", await page.title())

        # Click on "Create account" button
        try:
            create_btn = page.get_by_role("link", name="Create account")
            if await create_btn.count() > 0:
                print("Found 'Create account' button, clicking...")
                await create_btn.first.click()
                await page.wait_for_timeout(3000)

                print("After clicking Create account:")
                print("Title:", await page.title())

                # Get the page content
                text = await page.inner_text("body")
                print("Content:", text[:1500])

                await page.screenshot(path="/tmp/bluesky_create.png")
                print("\nScreenshot saved!")
            else:
                print("No Create account button found")
                # Try other ways to find the button
                buttons = await page.query_selector_all("button, a")
                for btn in buttons[:10]:
                    try:
                        text = await btn.inner_text()
                        if text:
                            print(f"Button/link: {text[:50]}")
                    except:
                        pass
        except Exception as e:
            print(f"Error: {e}")

        await browser.close()
        print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
