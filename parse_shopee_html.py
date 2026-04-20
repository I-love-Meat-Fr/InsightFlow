import json
import re
from selectolax.parser import HTMLParser

def extract_products(html_path):
    with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()

    tree = HTMLParser(html)
    products = []

    # Shopee products usually are inside <a> tags within a specific container.
    # In the flash sale page, let's find all <a> tags that look like products.
    # They usually have long text and prices.
    for a in tree.css('a'):
        text = a.text(strip=True)
        # Look for the currency symbol "₫" in the text
        if "₫" in text and len(text) > 20:
            href = a.attributes.get('href', '')
            
            # Simple regex to extract price information
            # Usually format is like "150.000₫-34%98.500₫"
            # or "Tên sản phẩm75.000₫-43%43.000₫ĐANG BÁN CHẠYMua ngay"
            
            # Let's find all instances of numbers followed by ₫
            prices = re.findall(r'([\d\.]+)\s*₫', text)
            prices = [float(p.replace('.', '')) for p in prices]
            
            if not prices:
                continue
                
            current_price = min(prices)
            original_price = max(prices) if len(prices) > 1 else current_price
            
            # Find discount percentage
            discount_match = re.search(r'-(\d+)%', text)
            discount = int(discount_match.group(1)) if discount_match else None
            
            # The title is usually at the beginning before the first price
            title_match = re.search(r'^(.*?)([\d\.]+)\s*₫', text)
            title = title_match.group(1).strip() if title_match else text[:50]
            
            # Clean up title if it has trailing parts
            if title and len(title) > 0:
                products.append({
                    'title': title,
                    'price': current_price,
                    'original_price': original_price,
                    'discount_percent': discount,
                    'url': "https://shopee.vn" + href if href.startswith('/') else href,
                    'raw_text': text
                })

    return products

if __name__ == '__main__':
    products = extract_products('../shopee_manual.html')
    print(f"Extracted {len(products)} products.")
    for p in products[:5]:
        print(json.dumps(p, ensure_ascii=False, indent=2))
    
    with open('shopee_extracted.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
