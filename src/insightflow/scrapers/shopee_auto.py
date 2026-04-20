import time
import json
import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from insightflow.scrapers.shopee import parse_shopee_manual_html

logger = logging.getLogger(__name__)

def auto_scrape_shopee(url: str, output_file: str = "shopee_auto.html"):
    """
    Uses undetected-chromedriver to bypass Shopee's anti-bot, navigate to the flash sale,
    scroll to load all items, and extract the HTML.
    """
    logger.info(f"Starting undetected-chromedriver for URL: {url}")
    print(f"Starting auto-scraper for {url}")
    
    options = uc.ChromeOptions()
    # Adding a user-data-dir allows it to save cookies and bypass captchas more easily over time
    options.add_argument("--user-data-dir=./chrome_profile")
    
    # Locate Playwright's Chromium binary so we don't need system Chrome installed
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        chromium_path = p.chromium.executable_path
    
    # We use headless=False because undetected-chromedriver is often detected in headless mode
    driver = uc.Chrome(options=options, headless=False, browser_executable_path=chromium_path, version_main=145)
    
    try:
        driver.get(url)
        print("Page loaded. Waiting for anti-bot checks to pass...")
        time.sleep(5)
        
        # Check if we are redirected to login page within 10 seconds
        is_login = False
        for _ in range(10):
            if "login" in driver.current_url.lower() or "đăng nhập" in driver.title.lower():
                is_login = True
                break
            time.sleep(1)
            
        if is_login:
            print("\n" + "="*60)
            print("🚨 DETECTED LOGIN PAGE 🚨")
            print("Please manually log in to your Shopee account in the Chrome window.")
            print("Once you are fully logged in and can see the flash sale,")
            input("PRESS ENTER IN THIS TERMINAL TO CONTINUE...")
            print("="*60 + "\n")
            # Wait a few seconds for page to settle after login
            time.sleep(5)
        
        print("Scrolling page to trigger lazy-loading of products...")
        # Scroll down incrementally
        for i in range(10):
            driver.execute_script(f"window.scrollBy(0, 1000);")
            time.sleep(1)
            
        print("Waiting for products to render...")
        time.sleep(5)
        
        # Save the HTML source
        page_source = driver.page_source
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(page_source)
            
        print(f"Successfully saved HTML to {output_file}")
        
    except Exception as e:
        logger.error(f"Error during auto-scraping: {e}")
        print(f"Error: {e}")
    finally:
        driver.quit()
        
    print("Parsing extracted HTML...")
    products = parse_shopee_manual_html(output_file)
    
    # Save the parsed products
    with open("shopee_auto_extracted.json", "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
        
    print(f"Extraction complete! Found {len(products)} products.")
    return products

if __name__ == "__main__":
    import sys
    target_url = sys.argv[1] if len(sys.argv) > 1 else "https://shopee.vn/flash_sale?promotionId=252939319459843"
    auto_scrape_shopee(target_url)
