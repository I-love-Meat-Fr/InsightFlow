from __future__ import annotations

import json
import logging
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


def _today_str() -> str:
    return date.today().isoformat()


class HistoryStore:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.history_dir = data_dir / "history"
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def append_products(self, rows: list[dict[str, Any]]) -> Path:
        path = self.history_dir / f"products_{_today_str()}.parquet"
        if not rows:
            logger.info("No product rows; skip history parquet write")
            return path
        for row in rows:
            if "specs" in row:
                if not row["specs"] or not isinstance(row["specs"], dict):
                    row["specs"] = {"status": "no_specs"} 
        df = pd.DataFrame(rows)
        if "scraped_at" in df.columns:
            df["scraped_at"] = pd.to_datetime(df["scraped_at"], utc=True)
        df.to_parquet(path, index=False)
        logger.info("Wrote product history %s rows=%s", path, len(df))
        return path

    def load_latest_before(self, day: date | None = None) -> pd.DataFrame:
        """Load most recent products parquet strictly before given day (default today)."""
        if day is None:
            day = date.today()
        files = sorted(self.history_dir.glob("products_*.parquet"))
        prev: Path | None = None
        for f in files:
            try:
                stem = f.stem.replace("products_", "")
                d = date.fromisoformat(stem)
            except ValueError:
                continue
            if d < day:
                prev = f
        if prev is None:
            return pd.DataFrame()
        return pd.read_parquet(prev)

    def load_today_products(self) -> pd.DataFrame:
        p = self.history_dir / f"products_{_today_str()}.parquet"
        if not p.exists():
            return pd.DataFrame()
        return pd.read_parquet(p)


def specs_dict_from_row(row: pd.Series) -> dict[str, str]:
    if "specs_json" in row.index and isinstance(row["specs_json"], str):
        try:
            return json.loads(row["specs_json"])
        except json.JSONDecodeError:
            return {}
    if "specs" in row.index and isinstance(row["specs"], dict):
        return dict(row["specs"])
    return {}
