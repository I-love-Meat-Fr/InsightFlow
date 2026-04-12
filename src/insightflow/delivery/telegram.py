from __future__ import annotations

import logging
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)


async def send_pdf_telegram(token: str, chat_id: str, pdf_path: Path, caption: str) -> None:
    if not token or not chat_id:
        logger.warning("Telegram credentials missing; skip send")
        return
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    data = {"chat_id": chat_id, "caption": caption[:1024]}
    async with httpx.AsyncClient(timeout=120.0) as client:
        with pdf_path.open("rb") as f:
            r = await client.post(
                url,
                data=data,
                files={"document": (pdf_path.name, f, "application/pdf")},
            )
        r.raise_for_status()
    logger.info("Telegram sendDocument ok chat_id=%s", chat_id)
