#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto("https://grok.com")
        await page.wait_for_timeout(5000)

        print("URL:", page.url)

        # Take screenshot
        await page.screenshot(path="/tmp/grok_ui.png", full_page=True)
        print("Screenshot: /tmp/grok_ui.png")

        # Get all inputs
        inputs = await page.query_selector_all("input, textarea")
        print(f"Found {len(inputs)} inputs")

        for i, inp in enumerate(inputs):
            try:
                print(f"  {i}: {await inp.get_attribute('placeholder')}")
            except:
                pass

        await browser.close()


asyncio.run(main())
