#!/usr/bin/env python3
"""
Debug the username field
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

        print("On Step 2")

        # Look at the form fields
        inputs = await page.query_selector_all("input")
        print(f"Found {len(inputs)} inputs")

        for i, inp in enumerate(inputs):
            try:
                label = await inp.get_attribute("aria-label")
                placeholder = await inp.get_attribute("placeholder")
                name = await inp.get_attribute("name")
                id = await inp.get_attribute("id")
                print(
                    f"Input {i}: label={label}, placeholder={placeholder}, name={name}, id={id}"
                )
            except:
                pass

        # Also look for labels
        labels = await page.query_selector_all("label")
        print(f"\nFound {len(labels)} labels")
        for i, lab in enumerate(labels):
            try:
                text = await lab.inner_text()
                for_attr = await lab.get_attribute("for")
                print(f"Label {i}: text={text[:50]}, for={for_attr}")
            except:
                pass

        await page.screenshot(path="/tmp/bluesky_step2_debug.png")

        await browser.close()
        print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
