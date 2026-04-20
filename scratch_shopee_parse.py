from selectolax.parser import HTMLParser
import json

with open("shopee_flash_sale.html", "r", encoding="utf-8") as f:
    html = f.read()

tree = HTMLParser(html)

# Let's search for the product link elements
links = tree.css('a[href*="-i."]')
print(f"Found {len(links)} product links")

products = []
for link in links:
    href = link.attributes.get('href')
    text = link.text(strip=True)
    if href and text:
        products.append({"href": href, "text": text[:100]})

print(f"Extracted {len(products)} products with text.")
for p in products[:5]:
    print(p)

# Let's try to extract specific prices by finding text nodes that contain "₫"
nodes = tree.css('*')
price_texts = []
for n in nodes:
    if n.child is None: # leaf node
        t = n.text(strip=True)
        if "₫" in t:
            price_texts.append(t)

print(f"Found {len(price_texts)} price texts")
print(price_texts[:10])

