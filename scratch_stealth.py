import asyncio
from playwright.async_api import async_playwright
from playwright_stealth.stealth import Stealth

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        stealth = Stealth()
        await stealth.apply_stealth_async(page)
        
        url = "https://shopee.vn/flash_sale?promotionId=252939319459843"
        print(f"Navigating to {url}")
        
        await page.goto(url, wait_until="networkidle")
        
        print("Waiting for page load...")
        await page.wait_for_timeout(5000)
        
        title = await page.title()
        print(f"Title: {title}")
        
        html = await page.content()
        with open("stealth_shopee.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        print("Done.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
