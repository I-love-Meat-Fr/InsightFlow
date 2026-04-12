from __future__ import annotations

import pandas as pd


def flag_price_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Add column price_outlier (bool) per target_id using IQR on non-null prices."""
    if df.empty or "price" not in df.columns:
        return df
    out = df.copy()
    out["price_outlier"] = False
    for _tid, grp in out.groupby("target_id"):
        idx = grp.index
        s = grp["price"].dropna()
        if len(s) < 4:
            continue
        q1 = s.quantile(0.25)
        q3 = s.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        low = q1 - 1.5 * iqr
        high = q3 + 1.5 * iqr
        sub = out.loc[idx, "price"]
        mask = sub.notna() & ((sub < low) | (sub > high))
        hit = sub[mask].index
        out.loc[hit, "price_outlier"] = True
    return out
