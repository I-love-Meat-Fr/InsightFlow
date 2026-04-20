import asyncio
import json
from playwright.async_api import async_playwright
from playwright_stealth.stealth import Stealth

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            storage_state="shopee_state.json",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        stealth = Stealth()
        await stealth.apply_stealth_async(page)
        
        intercepted_data = []

        async def handle_response(response):
            if "api/v4/flash_sale" in response.url or "api/v4/paged_item_list" in response.url:
                try:
                    data = await response.json()
                    intercepted_data.append(data)
                except:
                    pass
        
        page.on("response", handle_response)
        
        url = "https://shopee.vn/flash_sale?promotionId=252939319459843"
        print(f"Navigating to {url}")
        
        await page.goto(url, wait_until="networkidle")
        
        print("Scrolling...")
        for _ in range(5):
            await page.mouse.wheel(0, 1000)
            await page.wait_for_timeout(1000)
        
        await page.wait_for_timeout(5000)
        
        title = await page.title()
        print(f"Title: {title}")
        
        if intercepted_data:
            print("Successfully intercepted API data!")
            # check if it's error 90309999
            has_error = any(str(d.get("error")) == "90309999" for d in intercepted_data)
            if has_error:
                print("However, Shopee still returned Error 90309999 (Anti-bot block).")
            else:
                print("No anti-bot error detected in API response!")
        else:
            print("No flash sale API responses intercepted.")
            
        print("Done.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
