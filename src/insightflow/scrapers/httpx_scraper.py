from __future__ import annotations

import asyncio
import logging
from typing import Any
from urllib.parse import urljoin

import httpx
from selectolax.parser import HTMLParser

from insightflow.config.loader import TargetConfig
from insightflow.models import NewsItem, ProductSnapshot, ReviewItem, utc_now
from insightflow.scrapers.html_utils import extract_specs, first_text, parse_float_loose, parse_price

logger = logging.getLogger(__name__)


class HttpxScraper:
    def __init__(
        self,
        timeout: float = 30.0,
        max_concurrent: int = 20,
        user_agent: str | None = None,
    ) -> None:
        self._timeout = timeout
        self._sem = asyncio.Semaphore(max_concurrent)
        self._ua = user_agent or "InsightFlow/0.1"

    async def fetch(self, client: httpx.AsyncClient, url: str) -> str | None:
        async with self._sem:
            try:
                r = await client.get(url, follow_redirects=True)
                r.raise_for_status()
                return r.text
            except Exception as e:
                logger.exception("httpx fetch failed url=%s err=%s", url, e)
                return None

    async def scrape_target(
        self,
        target: TargetConfig,
        defaults: dict[str, Any],
    ) -> tuple[list[ProductSnapshot], list[NewsItem], list[ReviewItem]]:
        timeout = float(target.selectors.get("timeout_seconds") or defaults.get("timeout_seconds") or 30)
        max_c = int(defaults.get("max_concurrent") or 20)
        ua = str(defaults.get("user_agent") or self._ua)
        self._sem = asyncio.Semaphore(max_c)

        products: list[ProductSnapshot] = []
        news_items: list[NewsItem] = []
        reviews: list[ReviewItem] = []

        headers = {"User-Agent": ua}
        async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
            tasks = [self.fetch(client, u) for u in target.urls]
            bodies = await asyncio.gather(*tasks)

        for url, html in zip(target.urls, bodies):
            if not html:
                continue
            tree = HTMLParser(html)
            if tree.body is None:
                logger.warning("No HTML body for url=%s", url)
                continue

            if target.news:
                news_items.extend(self._parse_news(target, url, tree))
                continue

            if target.listing:
                products.extend(self._parse_listing(target, url, tree))
                continue

            sel = target.selectors
            title_sel = str(sel.get("title") or "h1")
            price_sel = str(sel.get("price") or "")

            title = first_text(tree.body, title_sel)
            price_text = first_text(tree.body, price_sel) if price_sel else None
            price, currency = parse_price(price_text)
            specs_map = sel.get("specs") or {}
            specs = extract_specs(tree.body, specs_map)

            products.append(
                ProductSnapshot(
                    target_id=target.id,
                    url=url,
                    title=title,
                    price=price,
                    currency=currency,
                    specs=specs,
                    scraped_at=utc_now(),
                    source_kind="httpx",
                )
            )

            if target.reviews and target.reviews.selector:
                for node in tree.body.css(target.reviews.selector):
                    text = node.text(strip=True)
                    if not text:
                        continue
                    rating = None
                    if target.reviews.rating_selector:
                        rnode = node.css_first(target.reviews.rating_selector)
                        if rnode:
                            rating = parse_float_loose(rnode.text(strip=True))
                    reviews.append(
                        ReviewItem(
                            target_id=target.id,
                            product_url=url,
                            text=text[:8000],
                            rating=float(rating) if rating is not None else None,
                            scraped_at=utc_now(),
                        )
                    )

        return products, news_items, reviews

    def _parse_listing(
        self,
        target: TargetConfig,
        page_url: str,
        tree: HTMLParser,
    ) -> list[ProductSnapshot]:
        cfg = target.listing
        assert cfg is not None
        out: list[ProductSnapshot] = []
        root = tree.body
        if not root:
            return out
        sels = cfg.selectors or {}
        title_sel = str(sels.get("title") or "h3 a")
        price_sel = str(sels.get("price") or "")
        link_sel = str(sels.get("link") or title_sel)

        for node in root.css(cfg.item_selector):
            link_el = node.css_first(link_sel)
            href = link_el.attributes.get("href") if link_el else None
            if href and not href.startswith("http"):
                href = urljoin(page_url, href)

            title = first_text(node, title_sel)
            if not title and link_el is not None:
                title = (link_el.attributes.get("title") or "").strip() or None
            if not title and link_el is not None:
                t = link_el.text(strip=True)
                title = t or None

            price_text = first_text(node, price_sel) if price_sel else None
            price, currency = parse_price(price_text)

            specs: dict[str, str] = {}
            for key, sel in sels.items():
                if key in ("title", "price", "link"):
                    continue
                val = first_text(node, str(sel))
                if val:
                    specs[key] = val

            item_url = href or page_url
            out.append(
                ProductSnapshot(
                    target_id=target.id,
                    url=item_url,
                    title=title,
                    price=price,
                    currency=currency,
                    specs=specs,
                    scraped_at=utc_now(),
                    source_kind="httpx",
                )
            )
        return out

    def _parse_news(self, target: TargetConfig, page_url: str, tree: HTMLParser) -> list[NewsItem]:
        cfg = target.news
        assert cfg is not None
        items: list[NewsItem] = []
        root = tree.body
        if not root:
            return items
        for art in root.css(cfg.list_selector):
            title = first_text(art, cfg.title_selector) or ""
            link_el = art.css_first(cfg.link_selector)
            href = link_el.attributes.get("href") if link_el else None
            if href and not href.startswith("http"):
                href = urljoin(page_url, href)
            if title:
                items.append(
                    NewsItem(
                        target_id=target.id,
                        url=page_url,
                        title=title,
                        link=href,
                        scraped_at=utc_now(),
                    )
                )
        return items
