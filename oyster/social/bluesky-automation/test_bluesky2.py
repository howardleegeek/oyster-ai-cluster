#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto("https://bsky.app")
        await page.wait_for_timeout(3000)

        print("Page title:", await page.title())

        # Look for elements in the header/nav area
        # Try to find by role
        nav_buttons = await page.query_selector_all("nav button")
        print(f"Found {len(nav_buttons)} nav buttons")

        # Look for the avatar button - try to find by the side nav
        # Bluesky typically has a side nav with the user avatar at the bottom left

        # Get all links and buttons
        all_elements = await page.query_selector_all("a, button")

        print("\nLooking for user avatar/switcher:")
        for elem in all_elements[:30]:
            try:
                role = await elem.get_attribute("role")
                aria_label = await elem.get_attribute("aria-label")
                data_testid = await elem.get_attribute("data-testid")
                href = await elem.get_attribute("href")

                if aria_label or data_testid:
                    print(
                        f"  {role}: aria-label={aria_label}, data-testid={data_testid}, href={href}"
                    )
            except:
                pass

        # Also try to find by looking at the left sidebar
        # The profile is usually at the bottom of the left nav

        # Try clicking on the left side of the screen where profile usually is
        await page.mouse.click(50, 600)  # Try clicking left area
        await page.wait_for_timeout(1000)

        text = await page.inner_text("body")
        if "Add account" in text or "Switch" in text or "Sign up" in text:
            print("\nFound account options!")
            print(text[:1000])

        await browser.close()
        print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
