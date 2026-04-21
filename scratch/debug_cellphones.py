import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, executable_path="/home/quocanh/.cache/ms-playwright/chromium-1208/chrome-linux64/chrome")
        page = await browser.new_page()
        await page.goto("https://cellphones.com.vn/mobile.html", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_selector(".product-info-container", timeout=10000)
        
        # Count initial items
        items = await page.query_selector_all(".product-info-container")
        print(f"Initial items (.product-info-container): {len(items)}")
        
        items2 = await page.query_selector_all(".product-item")
        print(f"Initial items (.product-item): {len(items2)}")

        # Click show more
        btn = await page.query_selector("div.cps-block-content_btn-showmore")
        if btn:
            await page.evaluate("el => el.click()", btn)
            await asyncio.sleep(3)
            items_after = await page.query_selector_all(".product-info-container")
            print(f"Items after 1 click: {len(items_after)}")
        else:
            print("Show more button not found")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
