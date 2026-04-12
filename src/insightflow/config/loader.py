from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class ReviewSelectors(BaseModel):
    selector: str = ""
    rating_selector: str = ""


class NewsConfig(BaseModel):
    list_selector: str = "article"
    title_selector: str = "h2"
    link_selector: str = "a"


class ListingConfig(BaseModel):
    """Many items per page (e.g. e-commerce grid)."""

    item_selector: str
    selectors: dict[str, str] = Field(default_factory=dict)


class TargetConfig(BaseModel):
    id: str
    kind: str  # httpx | playwright
    urls: list[str] = Field(default_factory=list)
    selectors: dict[str, Any] = Field(default_factory=dict)
    reviews: ReviewSelectors | None = None
    news: NewsConfig | None = None
    listing: ListingConfig | None = None


class TargetsFile(BaseModel):
    defaults: dict[str, Any] = Field(default_factory=dict)
    targets: list[TargetConfig] = Field(default_factory=list)


def load_targets_file(path: Path) -> TargetsFile:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Invalid YAML root in {path}")
    return TargetsFile.model_validate(raw)
