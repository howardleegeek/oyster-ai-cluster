#!/usr/bin/env python3
"""
Try to enter the verification code
"""

import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Go back to the registration page
        await page.goto("https://bsky.app/settings")
        await page.wait_for_timeout(2000)

        # Click Create account to continue
        create_link = page.get_by_text("Create account")
        await create_link.first.click()
        await page.wait_for_timeout(3000)

        # Fill Step 1 again
        await page.get_by_label("Email").fill("howard.mba.apply@gmail.com")
        await page.get_by_label("Password").fill("Howard@3503")

        await page.get_by_role("button", name="Next").click()
        await page.wait_for_timeout(3000)

        # Fill username
        await page.get_by_placeholder(".bsky.social").fill("clawglasses")
        await page.get_by_role("button", name="Next").click()
        await page.wait_for_timeout(3000)

        print("On verification step")

        # Look for verification code input
        # Try to find input fields
        inputs = await page.query_selector_all("input")
        print(f"Found {len(inputs)} inputs")

        for i, inp in enumerate(inputs):
            try:
                placeholder = await inp.get_attribute("placeholder")
                aria_label = await inp.get_attribute("aria-label")
                print(f"Input {i}: placeholder={placeholder}, aria_label={aria_label}")
            except:
                pass

        # Try to fill the verification code
        # The code Howard provided: lz2c-aexj-nlii-npzt
        if len(inputs) > 0:
            await inputs[0].fill("lz2c-aexj-nlii-npzt")
            await page.wait_for_timeout(1000)

            await page.screenshot(path="/tmp/bluesky_verify.png")
            print("Filled verification code")

        await browser.close()
        print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
