from __future__ import annotations

import logging
from typing import Any

import pandas as pd

from insightflow.analysis.history import specs_dict_from_row

logger = logging.getLogger(__name__)


def diff_specs_against_previous(current: pd.DataFrame, previous: pd.DataFrame) -> list[dict[str, Any]]:
    """Compare specs by url between two product dataframes."""
    if current.empty or previous.empty:
        return []
    diffs: list[dict[str, Any]] = []
    prev_by_url = previous.set_index("url", drop=False)
    for _, row in current.iterrows():
        url = row.get("url")
        if not url or url not in prev_by_url.index:
            continue
        old = prev_by_url.loc[url]
        if isinstance(old, pd.DataFrame):
            old = old.iloc[0]
        new_specs = specs_dict_from_row(row)
        old_specs = specs_dict_from_row(old)
        if new_specs == old_specs:
            continue
        keys = set(new_specs) | set(old_specs)
        changes: dict[str, tuple[str | None, str | None]] = {}
        for k in keys:
            a, b = old_specs.get(k), new_specs.get(k)
            if a != b:
                changes[k] = (a, b)
        if changes:
            diffs.append(
                {
                    "url": url,
                    "target_id": row.get("target_id"),
                    "title": row.get("title"),
                    "changes": {k: {"from": v[0], "to": v[1]} for k, v in changes.items()},
                }
            )
            logger.info("spec diff url=%s keys=%s", url, list(changes.keys()))
    return diffs
