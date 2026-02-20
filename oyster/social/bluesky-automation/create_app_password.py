#!/usr/bin/env python3
"""
Create new App Password for clawglasses
"""

import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Login
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

        # Click Add App Password
        add_btn = page.get_by_text("Add App Password")
        await add_btn.click()
        await page.wait_for_timeout(2000)

        print("Add App Password dialog")

        # Fill in a name
        name_input = page.get_by_label("Name")
        if await name_input.count() > 0:
            await name_input.fill("opencode-api")
            print("Filled name")

        await page.wait_for_timeout(1000)

        # Look for Next/Continue button
        buttons = await page.query_selector_all("button")
        for btn in buttons:
            try:
                text = await btn.inner_text()
                if "Next" in text or "Continue" in text or "Create" in text:
                    print(f"Clicking: {text}")
                    await btn.click()
                    await page.wait_for_timeout(3000)
                    break
            except:
                pass

        # Take screenshot to capture the password
        await page.screenshot(path="/tmp/new_app_password.png")
        print("Screenshot saved!")

        text = await page.inner_text("body")
        print("Page content:")
        print(text[:1500])

        await browser.close()
        print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
