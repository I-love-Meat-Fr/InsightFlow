from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from insightflow.ai.prompts import DIGEST_SYSTEM, build_user_payload

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    async def daily_digest(
        self,
        products_csv: str,
        news_lines: str,
        review_summary: str,
        outliers_note: str,
        spec_diffs_note: str,
    ) -> dict[str, Any]:
        user = build_user_payload(products_csv, news_lines, review_summary, outliers_note, spec_diffs_note)
        url = f"{self.base_url}/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": DIGEST_SYSTEM},
                {"role": "user", "content": user[:120_000]},
            ],
            "temperature": 0.4,
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(url, headers=headers, json=body)
            r.raise_for_status()
            data = r.json()
        content = data["choices"][0]["message"]["content"]
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[-1]
            content = content.rsplit("```", 1)[0].strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            logger.warning("LLM returned non-JSON; wrapping as summary")
            return {
                "summary": content[:4000],
                "trends": [],
                "risks": [],
                "recommendations": [],
            }
