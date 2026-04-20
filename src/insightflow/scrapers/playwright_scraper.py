from __future__ import annotations

import asyncio
import logging
from typing import Any
from urllib.parse import urljoin

from playwright.async_api import async_playwright

from insightflow.config.loader import TargetConfig
from insightflow.models import ProductSnapshot, ReviewItem, utc_now
from insightflow.scrapers.html_utils import parse_float_loose, parse_price

logger = logging.getLogger(__name__)


class PlaywrightScraper:
    async def scrape_target(
        self,
        target: TargetConfig,
        defaults: dict[str, Any],
    ) -> tuple[list[ProductSnapshot], list[ReviewItem]]:
        timeout_ms = int(float(defaults.get("timeout_seconds") or 30) * 1000)
        products: list[ProductSnapshot] = []
        reviews: list[ReviewItem] = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=str(defaults.get("user_agent") or "InsightFlow/0.1"),
            )
            page = await context.new_page()
            page.set_default_timeout(timeout_ms)

            try:
                for url in target.urls:
                    try:
                        await page.goto(url, wait_until="domcontentloaded")
                    except Exception as e:
                        logger.exception("playwright goto failed url=%s err=%s", url, e)
                        continue

                    sel = target.selectors
                    wait_for = str(sel.get("wait_for") or "body")
                    try:
                        await page.wait_for_selector(wait_for, timeout=timeout_ms)
                    except Exception as e:
                        logger.warning("wait_for selector missing url=%s sel=%s err=%s", url, wait_for, e)
                    if "thegioididong.com" in url:
                        # Cuộn xuống một chút để kích hoạt Render Flash Sale/Danh sách sản phẩm
                        await page.evaluate("window.scrollTo(0, 800);") 
                        await asyncio.sleep(2) # Chờ 2 giây để các component load xong
                    item_sel = str(sel.get("item") or "")
                    if item_sel:
                        items = await page.query_selector_all(item_sel)
                        title_w = str(sel.get("title_within") or "h2")
                        price_w = str(sel.get("price_within") or ".price")
                        orig_price_w = str(sel.get("original_price_within") or "")
                        link_w = str(sel.get("link_within") or "a")
                        for it in items:
                            title_el = await it.query_selector(title_w)
                            price_el = await it.query_selector(price_w)
                            orig_price_el = await it.query_selector(orig_price_w) if orig_price_w else None
                            link_el = await it.query_selector(link_w)
                            title = (await title_el.inner_text()).strip() if title_el else None
                            price_txt = (await price_el.inner_text()).strip() if price_el else None
                            orig_price_txt = (await orig_price_el.inner_text()).strip() if orig_price_el else None
                            price, currency = parse_price(price_txt)
                            original_price, _ = parse_price(orig_price_txt)
                            href = await link_el.get_attribute("href") if link_el else None
                            if href and not href.startswith("http"):
                                href = urljoin(url, href)
                            item_url = href or url
                            products.append(
                                ProductSnapshot(
                                    target_id=target.id,
                                    url=item_url,
                                    title=title,
                                    price=price,
                                    original_price=original_price,
                                    currency=currency,
                                    specs={},
                                    scraped_at=utc_now(),
                                    source_kind="playwright",
                                )
                            )
                    else:
                        title_sel = str(sel.get("title") or "h1")
                        price_sel = str(sel.get("price") or "")
                        orig_price_sel = str(sel.get("original_price") or "")
                        title_el = await page.query_selector(title_sel)
                        price_el = await page.query_selector(price_sel) if price_sel else None
                        orig_price_el = await page.query_selector(orig_price_sel) if orig_price_sel else None
                        title = (await title_el.inner_text()).strip() if title_el else None
                        price_txt = (await price_el.inner_text()).strip() if price_el else None
                        orig_price_txt = (await orig_price_el.inner_text()).strip() if orig_price_el else None
                        price, currency = parse_price(price_txt)
                        original_price, _ = parse_price(orig_price_txt)
                        products.append(
                            ProductSnapshot(
                                target_id=target.id,
                                url=url,
                                title=title,
                                price=price,
                                original_price=original_price,
                                currency=currency,
                                specs={},
                                scraped_at=utc_now(),
                                source_kind="playwright",
                            )
                        )

                    if target.reviews and target.reviews.selector:
                        rev_nodes = await page.query_selector_all(target.reviews.selector)
                        for rn in rev_nodes:
                            try:
                                text = (await rn.inner_text()).strip()
                            except Exception:
                                continue
                            if not text:
                                continue
                            rating = None
                            if target.reviews.rating_selector:
                                rel = await rn.query_selector(target.reviews.rating_selector)
                                if rel:
                                    rating = parse_float_loose((await rel.inner_text()).strip())
                            reviews.append(
                                ReviewItem(
                                    target_id=target.id,
                                    product_url=url,
                                    text=text[:8000],
                                    rating=rating,
                                    scraped_at=utc_now(),
                                )
                            )

                    await asyncio.sleep(0.2)
            finally:
                await context.close()
                await browser.close()

        return products, reviews
