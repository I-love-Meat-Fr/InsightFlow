from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

import pandas as pd
from rich.progress import Progress, TaskID

from insightflow.ai.llm_client import LLMClient
from insightflow.analysis import (
    diff_specs_against_previous,
    enrich_reviews_sentiment,
    flag_price_outliers,
)
from insightflow.analysis.history import HistoryStore
from insightflow.config.loader import TargetsFile, load_targets_file
from insightflow.config.settings import Settings
from insightflow.delivery.email_delivery import send_pdf_email
from insightflow.delivery.telegram import send_pdf_telegram
from insightflow.models import NewsItem, ProductSnapshot, ReviewItem
from insightflow.report.pdf_builder import build_digest_pdf
from insightflow.scrapers import HttpxScraper, PlaywrightScraper

logger = logging.getLogger(__name__)


async def run_pipeline(
    config_path: Path,
    settings: Settings,
    no_send: bool = False,
    no_llm: bool = False,
    progress: Progress | None = None,
    crawl_task: TaskID | None = None,
) -> dict[str, Any]:
    tf: TargetsFile = load_targets_file(config_path)
    defaults = tf.defaults or {}

    all_products: list[ProductSnapshot] = []
    all_news: list[NewsItem] = []
    all_reviews: list[ReviewItem] = []

    httpx_scraper = HttpxScraper(
        timeout=float(defaults.get("timeout_seconds") or 30),
        max_concurrent=int(defaults.get("max_concurrent") or 20),
        user_agent=str(defaults.get("user_agent") or "InsightFlow/0.1"),
    )
    pw_scraper = PlaywrightScraper()

    total_targets = len(tf.targets)
    if total_targets == 0 and progress is not None and crawl_task is not None:
        progress.update(crawl_task, description="No targets", completed=1)
    for i, target in enumerate(tf.targets):
        if progress is not None and crawl_task is not None:
            progress.update(crawl_task, description=f"Crawl: {target.id}", completed=i)
        try:
            if target.kind == "httpx":
                p, n, r = await httpx_scraper.scrape_target(target, defaults)
                all_products.extend(p)
                all_news.extend(n)
                all_reviews.extend(r)
            elif target.kind == "playwright":
                p, r = await pw_scraper.scrape_target(target, defaults)
                all_products.extend(p)
                all_reviews.extend(r)
            else:
                logger.warning("Unknown target kind %s id=%s", target.kind, target.id)
        except Exception as e:
            logger.exception("Target failed id=%s err=%s", target.id, e)
        if progress is not None and crawl_task is not None:
            progress.update(crawl_task, completed=i + 1)

    if progress is not None and crawl_task is not None:
        progress.update(crawl_task, description="Crawl done", completed=total_targets)

    product_rows = [p.model_dump_row() for p in all_products]
    store = HistoryStore(settings.data_dir)
    store.append_products(product_rows)

    df = pd.DataFrame(product_rows) if product_rows else pd.DataFrame()
    if not df.empty and "price" in df.columns:
        df = flag_price_outliers(df)

    prev_df = store.load_latest_before()
    spec_diffs = diff_specs_against_previous(df, prev_df) if not df.empty else []

    review_dicts = [r.model_dump() for r in all_reviews]
    reviews_enriched = enrich_reviews_sentiment(review_dicts)

    products_csv = df.head(80).to_csv(index=False) if not df.empty else ""
    news_lines = "\n".join(f"- {n.title} ({n.link or n.url})" for n in all_news) if all_news else ""
    if not reviews_enriched.empty:
        g = reviews_enriched.groupby("target_id")["composite_buy_score"].mean()
        review_summary = "Average composite buy score by target:\n" + g.to_string()
        review_summary += "\n" + reviews_enriched.head(30).to_csv(index=False)
    else:
        review_summary = ""

    outliers_note = ""
    if not df.empty and "price_outlier" in df.columns:
        sub = df[df["price_outlier"]]
        outliers_note = sub[["target_id", "url", "title", "price"]].to_csv(index=False)

    spec_diffs_note = ""
    if spec_diffs:
        spec_diffs_note = "\n".join(str(x) for x in spec_diffs[:50])

    api_key = (settings.openai_api_key or "").strip()
    if no_llm or not api_key:
        if not no_llm and not api_key:
            logger.warning("OPENAI_API_KEY empty; using stub digest (use --no-llm to silence)")
        digest: dict[str, Any] = {
            "summary": "LLM digest skipped. Review tabular exports and outlier/spec sections in this PDF.",
            "trends": [
                f"Collected {len(all_products)} product rows, {len(all_news)} news lines, {len(all_reviews)} reviews."
            ],
            "risks": ["Automated scraping may break when sites change layout; check logs."],
            "recommendations": ["Configure real selectors in targets.yaml for your sources."],
        }
    else:
        llm = LLMClient(settings.openai_api_url, api_key, settings.llm_model)
        digest = await llm.daily_digest(
            products_csv,
            news_lines,
            review_summary,
            outliers_note,
            spec_diffs_note,
        )

    extra_sections: list[tuple[str, str]] = [
        ("Price outliers (IQR)", outliers_note or "(none)"),
        ("Spec diffs vs previous snapshot", spec_diffs_note or "(none)"),
    ]
    if not reviews_enriched.empty:
        extra_sections.append(("Review sentiment sample", reviews_enriched.head(40).to_csv(index=False)))

    preview_cols = [c for c in ["target_id", "url", "title", "price", "currency", "price_outlier"] if c in df.columns]
    if df.empty:
        table_data: list[list[Any]] = []
    else:
        sub = df[preview_cols].head(25) if preview_cols else df.head(25)
        table_data = [sub.columns.tolist()] + sub.values.tolist()

    reports_dir = settings.data_dir / "reports"
    pdf_path = reports_dir / f"digest_{pd.Timestamp.utcnow().strftime('%Y%m%d_%H%M')}.pdf"
    build_digest_pdf(pdf_path, digest, table_data, extra_sections=extra_sections)
    logger.info("PDF written %s", pdf_path)

    caption = str(digest.get("summary") or "InsightFlow digest")[:900]

    if not no_send:
        await send_pdf_telegram(
            settings.telegram_bot_token,
            settings.telegram_chat_id,
            pdf_path,
            caption,
        )
        await asyncio.to_thread(
            send_pdf_email,
            settings.smtp_host,
            settings.smtp_port,
            settings.smtp_user,
            settings.smtp_password,
            settings.smtp_from,
            settings.smtp_to,
            pdf_path,
            "InsightFlow daily digest",
            caption,
        )

    return {
        "pdf_path": str(pdf_path),
        "products_count": len(all_products),
        "news_count": len(all_news),
        "reviews_count": len(all_reviews),
        "digest": digest,
    }
