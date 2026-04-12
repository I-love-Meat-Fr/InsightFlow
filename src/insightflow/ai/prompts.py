DIGEST_SYSTEM = """You are an analyst producing a concise daily market/intel brief.
Respond with valid JSON only, no markdown fences. Keys:
summary (string, 2-4 sentences),
trends (array of up to 5 short strings),
risks (array of up to 3 short strings),
recommendations (array of up to 3 short strings for shoppers or readers).
Language: match the dominant language of the input data (Vietnamese if most text is Vietnamese)."""


def build_user_payload(
    products_csv: str,
    news_lines: str,
    review_summary: str,
    outliers_note: str,
    spec_diffs_note: str,
) -> str:
    parts = [
        "## Product snapshots (tabular)\n" + products_csv,
        "## News headlines\n" + (news_lines or "(none)"),
        "## Review / sentiment summary\n" + (review_summary or "(none)"),
        "## Price outliers (IQR)\n" + (outliers_note or "(none)"),
        "## Spec configuration changes vs previous run\n" + (spec_diffs_note or "(none)"),
    ]
    return "\n\n".join(parts)
