from __future__ import annotations

from typing import Any

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()


def _vader_compound(text: str) -> float:
    return float(_analyzer.polarity_scores(text or "")["compound"])


def enrich_reviews_sentiment(reviews: list[dict[str, Any]]) -> pd.DataFrame:
    """Add vader_compound, sentiment_label, composite_score (0-100)."""
    if not reviews:
        return pd.DataFrame()
    rows = []
    for r in reviews:
        text = str(r.get("text") or "")
        compound = _vader_compound(text)
        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"
        rating = r.get("rating")
        norm_rating = None
        if rating is not None:
            try:
                rv = float(rating)
                if rv <= 5:
                    norm_rating = (rv / 5.0) * 100
                elif rv <= 10:
                    norm_rating = (rv / 10.0) * 100
                else:
                    norm_rating = min(100.0, rv)
            except (TypeError, ValueError):
                norm_rating = None
        sentiment_0_100 = (compound + 1) / 2 * 100
        if norm_rating is not None:
            composite = 0.6 * norm_rating + 0.4 * sentiment_0_100
        else:
            composite = sentiment_0_100
        rows.append(
            {
                **r,
                "vader_compound": compound,
                "sentiment_label": label,
                "composite_buy_score": round(composite, 2),
            }
        )
    return pd.DataFrame(rows)
