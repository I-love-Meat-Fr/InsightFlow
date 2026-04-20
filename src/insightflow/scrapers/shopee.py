import json
import os
import re
import logging
from typing import List, Dict, Any
from selectolax.parser import HTMLParser

logger = logging.getLogger(__name__)

def parse_shopee_manual_html(html_path: str) -> List[Dict[str, Any]]:
    """
    Parses a manually saved Shopee HTML file and extracts product details.
    This bypasses Shopee's strict anti-bot mechanisms.
    """
    if not os.path.exists(html_path):
        logger.error(f"File not found: {html_path}")
        return []

    with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()

    tree = HTMLParser(html)
    products = []

    for a in tree.css('a'):
        text = a.text(strip=True)
        if "₫" in text and len(text) > 20:
            href = a.attributes.get('href', '')
            
            prices = re.findall(r'([\d\.]+)\s*₫', text)
            prices = [float(p.replace('.', '')) for p in prices]
            
            if not prices:
                continue
                
            current_price = min(prices)
            original_price = max(prices) if len(prices) > 1 else current_price
            
            discount_match = re.search(r'-(\d+)%', text)
            discount = int(discount_match.group(1)) if discount_match else 0
            
            title_match = re.search(r'^(.*?)([\d\.]+)\s*₫', text)
            title = title_match.group(1).strip() if title_match else text[:100]
            
            if title:
                products.append({
                    'title': title,
                    'price': current_price,
                    'original_price': original_price,
                    'currency': 'VND',
                    'discount_percent': discount,
                    'url': "https://shopee.vn" + href if href.startswith('/') else href,
                })

    return products

if __name__ == "__main__":
    import sys
    html_file = sys.argv[1] if len(sys.argv) > 1 else "../shopee_manual.html"
    results = parse_shopee_manual_html(html_file)
    print(f"Successfully extracted {len(results)} products.")
    with open("shopee_extracted.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("Saved results to shopee_extracted.json")
