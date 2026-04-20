import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://cellphones.com.vn/mobile/apple.html", wait_until="domcontentloaded")
        await page.evaluate("window.scrollTo(0, 800);")
        await asyncio.sleep(2)
        try:
            await page.click("div.cps-block-content_btn-showmore")
            print("Clicked showmore")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"No showmore button: {e}")
            
        items = await page.query_selector_all(".product-info")
        for i in range(min(2, len(items))):
            html = await items[i].inner_html()
            print(f"ITEM {i}:\n{html}\n")
        await browser.close()

asyncio.run(run())
