from __future__ import annotations

import re
from typing import Any

from selectolax.parser import HTMLParser, Node

def first_text(node: Node | None, selector: str) -> str | None:
    if not node or not selector:
        return None
    el = node.css_first(selector)
    if el is None:
        return None
    t = el.text(strip=True)
    return t or None

def parse_price(text: str | None) -> tuple[float | None, str | None]:
    if not text:
        return None, None
    currency = None
    if "$" in text:
        currency = "USD"
    if "€" in text:
        currency = "EUR"
    if "£" in text:
        currency = "GBP"
    if "₫" in text or "đ" in text.lower():
        currency = "VND"
    digits = re.sub(r"[^\d.,]", "", text)
    if currency == "VND":
        digits = digits.replace(".", "").replace(",", "")
    else:
        digits = digits.replace(",", "")
    if not digits:
        return None, currency
    try:
        return float(digits), currency
    except ValueError:
        return None, currency

def parse_float_loose(text: str | None) -> float | None:
    if not text:
        return None
    m = re.search(r"[\d.]+", text.replace(",", ""))
    if not m:
        return None
    try:
        return float(m.group(0))
    except ValueError:
        return None

def extract_specs(root: Node, specs_map: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    if not isinstance(specs_map, dict):
        return out
    for key, sel in specs_map.items():
        if not isinstance(sel, str):
            continue
        t = first_text(root, sel)
        if t:
            out[str(key)] = t
    return out
