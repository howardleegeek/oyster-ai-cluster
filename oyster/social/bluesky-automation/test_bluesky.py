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

        # Try to find the profile/avatar button
        # Look for elements with "account" in aria-label or data-testid
        buttons = await page.query_selector_all("button")

        for btn in buttons[:10]:
            try:
                aria_label = await btn.get_attribute("aria-label")
                data_testid = await btn.get_attribute("data-testid")
                text = await btn.inner_text()

                if aria_label or data_testid or text:
                    print(
                        f"Button: aria-label={aria_label}, data-testid={data_testid}, text={text[:50]}"
                    )
            except:
                pass

        await browser.close()
        print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
