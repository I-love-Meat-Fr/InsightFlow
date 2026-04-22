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
                        # Chờ page load ổn định
                        await asyncio.sleep(3)
                        await page.evaluate("window.scrollTo(0, 500);") 
                        await asyncio.sleep(1)
                        
                        max_items = int(sel.get("max_items", 40))
                        item_sel = str(sel.get("item") or "li.item")
                        
                        for click_idx in range(60): # Allow up to 60 clicks for TGDD
                            try:
                                # Đếm số lượng item (ưu tiên data-id hoặc item selector)
                                current_count = await page.evaluate(f"document.querySelectorAll('{item_sel}, li[data-id]').length")
                                if current_count >= max_items:
                                    logger.info("Reached target item count (%d >= %d) for TGDD", current_count, max_items)
                                    break
                                    
                                # Tìm nút Xem thêm với nhiều class phổ biến của TGDD
                                btn = await page.query_selector(".see-more-btn, .view-more, .btn-view-more, a.viewmore")
                                if btn and await btn.is_visible():
                                    await page.evaluate("el => el.scrollIntoView({block: 'center'})", btn)
                                    await asyncio.sleep(1)
                                    
                                    # Click giả lập người dùng
                                    try:
                                        await btn.click(force=True, timeout=5000)
                                    except:
                                        await page.evaluate("el => el.click()", btn)
                                        
                                    # Chờ load và "rung" trang để kích hoạt lazy-load
                                    await asyncio.sleep(4)
                                    await page.evaluate("window.scrollBy(0, 200);")
                                    await asyncio.sleep(0.5)
                                    await page.evaluate("window.scrollBy(0, -200);")
                                else:
                                    # Thử cuộn xuống cuối trang nếu không thấy nút (đôi khi nút tự hiện khi scroll)
                                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                                    await asyncio.sleep(2)
                                    if not await page.query_selector(".see-more-btn, .view-more"):
                                        break
                            except Exception as e:
                                logger.warning("Error clicking show more on TGDD: %s", e)
                                break
                    
                    elif "fptshop.com.vn" in url:
                        # FPT Shop: Gọi API trực tiếp để lấy toàn bộ sản phẩm
                        # API: POST https://papi.fptshop.com.vn/gw/v1/public/fulltext-search-service/category
                        import json as _json
                        
                        api_url = "https://papi.fptshop.com.vn/gw/v1/public/fulltext-search-service/category"
                        slug = url.rstrip("/").split("/")[-1]  # "dien-thoai"
                        page_size = 24
                        skip = 0
                        total = None
                        
                        while True:
                            payload = _json.dumps({
                                "skipCount": skip,
                                "maxResultCount": page_size,
                                "sortMethod": "noi-bat",
                                "slug": slug,
                                "categoryType": "category",
                                "location": {}
                            })
                            
                            # Gọi API từ browser context (giữ cookies/headers)
                            resp_data = await page.evaluate(f"""async () => {{
                                const resp = await fetch('{api_url}', {{
                                    method: 'POST',
                                    headers: {{'Content-Type': 'application/json'}},
                                    body: '{payload}'
                                }});
                                return await resp.json();
                            }}""")
                            
                            if total is None:
                                total = resp_data.get("totalCount", 0)
                                logger.info("FPT Shop API: Total products = %d", total)
                            
                            items = resp_data.get("items", [])
                            if not items:
                                break
                            
                            for item in items:
                                item_name = item.get("name") or item.get("displayName") or ""
                                item_slug = item.get("slug", "")
                                item_url = f"https://fptshop.com.vn/{item_slug}" if item_slug else url
                                current_price = item.get("currentPrice", 0)
                                original_price = item.get("originalPrice", 0)
                                
                                products.append(
                                    ProductSnapshot(
                                        target_id=target.id,
                                        url=item_url,
                                        title=item_name,
                                        price=float(current_price) if current_price else None,
                                        original_price=float(original_price) if original_price else None,
                                        currency="VND",
                                        specs={},
                                        scraped_at=utc_now(),
                                        source_kind="playwright",
                                    )
                                )
                            
                            skip += page_size
                            logger.info("FPT Shop API: Collected %d / %d", min(skip, total), total)
                            
                            if skip >= total:
                                break
                            
                            await asyncio.sleep(0.5)  # Tránh rate limit
                        
                        logger.info("FPT Shop API: Done. Total products collected: %d", len(products))
                        continue  # Bỏ qua generic extraction
                                
                    elif "cellphones.com.vn" in url:
                        # Chờ page load ổn định
                        try:
                            await page.wait_for_load_state("networkidle", timeout=5000)
                        except:
                            pass
                            
                        # Click the show more button until it's no longer visible or we reach max_items
                        max_items = int(sel.get("max_items", 40))
                        item_sel = str(sel.get("item") or "")
                        
                        for click_idx in range(100): # Allow up to 100 clicks (~2000-3000 items)
                            try:
                                # Kiểm tra số lượng item hiện tại
                                if item_sel:
                                    current_items = await page.query_selector_all(item_sel)
                                    if len(current_items) >= max_items:
                                        logger.info("Reached target item count (%d >= %d) for %s", len(current_items), max_items, url)
                                        break
                                
                                # Kiểm tra xem page có đang bị chuyển hướng không (chỉ break nếu đang crawl brand mà bị về mobile.html)
                                if "/mobile.html" in page.url and "/mobile/" in url and "/mobile.html" not in url:
                                    logger.warning("Redirected from %s to %s, stopping show more", url, page.url)
                                    break

                                # Đóng các popup che chắn nếu có
                                await page.evaluate("""() => {
                                    const overlay = document.querySelector('#subscriberEmailOverlay');
                                    if (overlay) overlay.style.display = 'none';
                                    const modal = document.querySelector('#subscriberEmail');
                                    if (modal) modal.style.display = 'none';
                                }""")

                                btn = await page.query_selector("div.cps-block-content_btn-showmore")
                                if btn and await btn.is_visible():
                                    # Cuộn tới nút và di chuyển chuột tới đó để giả lập người dùng
                                    await page.evaluate("el => el.scrollIntoView({block: 'center'})", btn)
                                    await asyncio.sleep(1)
                                    
                                    # Click mạnh hơn bằng force=True
                                    try:
                                        await btn.click(force=True, timeout=5000)
                                    except:
                                        await page.evaluate("el => el.click()", btn)
                                    
                                    # Chờ load và cuộn nhẹ để kích hoạt lazy-load
                                    await asyncio.sleep(4)
                                    await page.evaluate("window.scrollBy(0, 300);")
                                    await asyncio.sleep(0.5)
                                    await page.evaluate("window.scrollBy(0, -300);")
                                    
                                    # Đếm số lượng item (ưu tiên data-id vì nó rất ổn định)
                                    count = await page.evaluate(f"document.querySelectorAll('{item_sel}, [data-id]').length")
                                    
                                    if click_idx % 5 == 0:
                                        logger.info("Clicked show more %d times for %s (detected items: %d)...", click_idx + 1, url, count)
                                    
                                    if count >= max_items:
                                        logger.info("Reached target item count (%d >= %d) for %s", count, max_items, url)
                                        break
                                else:
                                    # Nếu không thấy nút, có thể đã hết hoặc cần cuộn thêm
                                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                                    await asyncio.sleep(2)
                                    btn_check = await page.query_selector("div.cps-block-content_btn-showmore")
                                    if not btn_check:
                                        break
                            except Exception as e:
                                if "destroyed" in str(e) or "navigation" in str(e).lower():
                                    logger.warning("Context destroyed during show more for %s, waiting...", url)
                                    await asyncio.sleep(2)
                                    await page.wait_for_load_state("domcontentloaded")
                                    continue
                                logger.warning("Error clicking show more button on cellphones: %s", e)
                                break
                        
                        # Scroll a bit to ensure lazy loading images/data
                        try:
                            await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                            await asyncio.sleep(1)
                        except:
                            pass
                    item_sel = str(sel.get("item") or "")
                    if item_sel:
                        items = []
                        for retry in range(2):
                            try:
                                items = await page.query_selector_all(item_sel)
                                break
                            except Exception as e:
                                if "destroyed" in str(e) or "navigation" in str(e).lower():
                                    await asyncio.sleep(2)
                                    await page.wait_for_load_state("domcontentloaded")
                                    continue
                                logger.warning("Failed to query_selector_all on %s: %s", url, e)
                                break
                            
                        if not items:
                            continue

                        title_w = str(sel.get("title_within") or "h2")
                        price_w = str(sel.get("price_within") or ".price")
                        orig_price_w = str(sel.get("original_price_within") or "")
                        link_w = str(sel.get("link_within") or "a")
                        for it in items:
                            try:
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
                            except Exception as e:
                                # Nếu context bị hủy giữa chừng, bỏ qua các item còn lại của trang này
                                if "destroyed" in str(e) or "different document" in str(e):
                                    logger.warning("Context lost while parsing items on %s", url)
                                    break
                                logger.warning("Failed to parse an item on %s: %s", url, e)
                                continue
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
