import asyncio
import os
from playwright.async_api import async_playwright

async def debug_cellphones():
    async with async_playwright() as p:
        # Use the specific Playwright Chromium path
        chromium_path = "/home/quocanh/.cache/ms-playwright/chromium-1208/chrome-linux64/chrome"
        browser = await p.chromium.launch(headless=True, executable_path=chromium_path)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        url = "https://cellphones.com.vn/mobile.html"
        print(f"Navigating to {url}...")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(5)
        
        # Initial count
        initial = await page.evaluate("document.querySelectorAll('.product-item').length")
        print(f"Initial .product-item count: {initial}")
        
        # Try to click 'Show More' 5 times
        for i in range(5):
            print(f"Clicking Show More ({i+1}/5)...")
            btn = await page.query_selector("div.cps-block-content_btn-showmore")
            if btn and await btn.is_visible():
                await page.evaluate("el => el.click()", btn)
                await asyncio.sleep(4) # Wait more for loading
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1)
            else:
                print("Button not found or not visible")
                break
        
        final_count = await page.evaluate("document.querySelectorAll('.product-item').length")
        print(f"Final .product-item count after 5 clicks: {final_count}")
        
        # If count didn't increase much, find ALL divs with classes containing 'product'
        if final_count < 100:
            print("Selector .product-item might be wrong. Investigating other classes...")
            classes = await page.evaluate("""() => {
                const results = {};
                document.querySelectorAll('div[class*="product"]').forEach(el => {
                    const cls = el.className;
                    results[cls] = (results[cls] || 0) + 1;
                });
                return results;
            }""")
            # Sort by count
            sorted_classes = sorted(classes.items(), key=lambda x: x[1], reverse=True)
            print("Top 'product' classes found:")
            for cls, count in sorted_classes[:10]:
                print(f"  {cls}: {count}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_cellphones())
