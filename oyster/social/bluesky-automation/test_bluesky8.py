#!/usr/bin/env python3
"""
Fill in the Bluesky registration form
"""

import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Go to create account page
        await page.goto("https://bsky.app/settings")
        await page.wait_for_timeout(2000)

        # Click Create account
        create_link = page.get_by_text("Create account")
        await create_link.first.click()
        await page.wait_for_timeout(3000)

        print("On registration page")

        # Fill in email
        email_input = page.get_by_label("Email")
        await email_input.fill("howard.mba.apply@gmail.com")
        print("Filled email")

        # Fill in password
        password_input = page.get_by_label("Password")
        await password_input.fill("Howard@3503")
        print("Filled password")

        # Fill in birth date - need to find the right fields
        # Usually it's 3 dropdowns or inputs for month/day/year
        # Let's try to find them

        await page.screenshot(path="/tmp/bluesky_form_filled.png")
        print("Screenshot saved")

        # Look for date inputs
        date_inputs = await page.query_selector_all(
            "input[type='text'], input[type='number']"
        )
        print(f"Found {len(date_inputs)} inputs")

        # Try clicking Next to see what happens
        next_btn = page.get_by_role("button", name="Next")
        await next_btn.click()
        await page.wait_for_timeout(2000)

        print("After clicking Next:")
        text = await page.inner_text("body")
        print(text[:1500])

        await browser.close()
        print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
