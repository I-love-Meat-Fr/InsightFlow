import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # Headless=False helps sometimes with anti-bot, we can observe locally
        page = await browser.new_page()
        
        url = "https://shopee.vn/flash_sale?promotionId=252939319459843"
        print(f"Navigating to {url}")
        
        await page.goto(url, wait_until="networkidle")
        
        # Wait a bit for dynamic content
        await page.wait_for_timeout(5000)
        
        print(await page.title())
        
        # Take a screenshot
        await page.screenshot(path="shopee_test.png")
        
        # Try to extract some items
        html = await page.content()
        with open("shopee_test.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
