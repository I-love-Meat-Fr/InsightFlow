import asyncio
from playwright.async_api import async_playwright
import time
import os
import pandas as pd
import re
from selectolax.parser import HTMLParser
from datetime import datetime

def parse_html(html, timeline_info):
    tree = HTMLParser(html)
    products = []
    
    for a in tree.css('a'):
        text = a.text(strip=True)
        if "₫" in text and len(text) > 20:
            href = a.attributes.get('href', '')
            
            # Capture numbers, dots, and question marks
            prices_str = re.findall(r'([?\d\.]+)\s*₫', text)
            
            if not prices_str:
                continue
                
            numeric_prices = []
            for p in prices_str:
                clean_p = p.replace('.', '').replace('?', '')
                if clean_p.isdigit():
                    numeric_prices.append(float(clean_p))
                else:
                    numeric_prices.append(0.0)
                    
            if not numeric_prices:
                continue
                
            current_price = min(numeric_prices)
            original_price = max(numeric_prices) if len(numeric_prices) > 1 else current_price
            
            min_idx = numeric_prices.index(current_price)
            display_price = prices_str[min_idx] + " ₫"
            
            discount_match = re.search(r'-(\d+)%', text)
            discount = int(discount_match.group(1)) if discount_match else None
            
            # Update regex to stop at ? as well
            title_match = re.search(r'^(.*?)([?\d\.]+)\s*₫', text)
            title = title_match.group(1).strip() if title_match else text[:50]
            
            if title and len(title) > 0:
                products.append({
                    'title': title,
                    'display_price': display_price,
                    'price': current_price,
                    'original_price': original_price,
                    'discount_percent': discount,
                    'url': "https://shopee.vn" + href if href.startswith('/') else href,
                    'timeline': timeline_info
                })
    return products

def crawl_shopee_flash_sale():
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from playwright.sync_api import sync_playwright
    
    # Locate Playwright's Chromium binary so we don't need system Chrome installed
    with sync_playwright() as p:
        chromium_path = p.chromium.executable_path

    options = uc.ChromeOptions()
    options.add_argument("--user-data-dir=./chrome_profile")
    
    driver = uc.Chrome(options=options, headless=False, browser_executable_path=chromium_path, version_main=145)
    
    try:
        url = "https://shopee.vn/flash_sale"
        print(f"Navigating to {url}")
        driver.get(url)
        print("Page loaded. Waiting 10s for anti-bot checks to pass...")
        time.sleep(10)
        
        all_products = []
        
        # Get tabs list length to iterate via index to avoid stale element exceptions
        tabs = driver.find_elements(By.CSS_SELECTOR, "ul.image-carousel__item-list > li.image-carousel__item")
        num_tabs = len(tabs)
        print(f"Found {len(tabs)} tabs, will crawl {num_tabs} tabs.")
        
        for i in range(num_tabs):
            # Refetch tabs to avoid StaleElementReferenceException
            tabs = driver.find_elements(By.CSS_SELECTOR, "ul.image-carousel__item-list > li.image-carousel__item")
            if i >= len(tabs):
                break
                
            tab = tabs[i]
            
            try:
                time_div = tab.find_element(By.CSS_SELECTOR, "div.my4eAL")
                status_div = tab.find_element(By.CSS_SELECTOR, "div.D0ox6e")
                time_text = time_div.text if time_div else f"Tab {i+1}"
                status_text = status_div.text if status_div else ""
            except:
                time_text = f"Tab {i+1}"
                status_text = ""
                
            timeline_info = f"{time_text} - {status_text}"
            print(f"Crawling timeline: {timeline_info}")
            
            # Click the tab
            try:
                # scroll to the tab to make sure it's clickable
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tab)
                time.sleep(1)
                try:
                    tab.click()
                except:
                    # use JS to click to avoid interception
                    driver.execute_script("arguments[0].click();", tab)
            except Exception as e:
                print(f"Failed to click tab {i+1}: {e}")
                continue
                
            print("Waiting for products to render...")
            time.sleep(5)
            
            print("Scrolling page to trigger lazy-loading of products...")
            for _ in range(10):
                driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(1)
            
            time.sleep(2)
            
            html = driver.page_source
            products = parse_html(html, timeline_info)
            print(f"Extracted {len(products)} products for {timeline_info}")
            all_products.extend(products)
            
            # Scroll back to top for the next tab iteration
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
        if all_products:
            df = pd.DataFrame(all_products)
            df = df.drop_duplicates(subset=['title', 'timeline'])
            
            data_dir = "data/history"
            os.makedirs(data_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(data_dir, f"products_shopee_{timestamp}.parquet")
            
            df.to_parquet(file_path, index=False)
            print(f"Saved {len(df)} total products to {file_path}")
        else:
            print("No products extracted.")
            
    except Exception as e:
        print(f"Error during execution: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    crawl_shopee_flash_sale()
