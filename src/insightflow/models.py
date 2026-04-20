from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ProductSnapshot(BaseModel):
    target_id: str
    url: str
    title: str | None = None
    price: float | None = None
    original_price: float | None = None
    currency: str | None = None
    specs: dict[str, str] = Field(default_factory=dict)
    scraped_at: datetime = Field(default_factory=utc_now)
    source_kind: str = "httpx"

    def model_dump_row(self) -> dict[str, Any]:
        d = self.model_dump()
        d["specs_json"] = json.dumps(self.specs, ensure_ascii=False)
        return d


class NewsItem(BaseModel):
    target_id: str
    url: str
    title: str
    link: str | None = None
    scraped_at: datetime = Field(default_factory=utc_now)


class ReviewItem(BaseModel):
    target_id: str
    product_url: str
    text: str
    rating: float | None = None
    scraped_at: datetime = Field(default_factory=utc_now)
