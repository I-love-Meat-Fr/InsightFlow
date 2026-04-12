from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def build_digest_pdf(
    output_path: Path,
    digest: dict[str, Any],
    products_df_preview: list[list[Any]],
    extra_sections: list[tuple[str, str]] | None = None,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    story: list[Any] = []

    title = f"InsightFlow Daily Digest — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
    story.append(Paragraph(title, styles["Title"]))
    story.append(Spacer(1, 0.5 * cm))

    summary = digest.get("summary") or ""
    story.append(Paragraph("<b>Executive summary</b>", styles["Heading2"]))
    story.append(Paragraph(summary.replace("\n", "<br/>"), styles["BodyText"]))
    story.append(Spacer(1, 0.4 * cm))

    def bullets(label: str, items: list[Any]) -> None:
        story.append(Paragraph(f"<b>{label}</b>", styles["Heading3"]))
        if not items:
            story.append(Paragraph("(none)", styles["BodyText"]))
            return
        for it in items:
            story.append(Paragraph(f"• {it}", styles["BodyText"]))
        story.append(Spacer(1, 0.3 * cm))

    bullets("Trends", list(digest.get("trends") or []))
    bullets("Risks", list(digest.get("risks") or []))
    bullets("Recommendations", list(digest.get("recommendations") or []))

    if extra_sections:
        for heading, body in extra_sections:
            story.append(Paragraph(f"<b>{heading}</b>", styles["Heading3"]))
            story.append(Paragraph(body.replace("\n", "<br/>")[:8000], styles["BodyText"]))
            story.append(Spacer(1, 0.3 * cm))

    if products_df_preview:
        story.append(Paragraph("<b>Data snapshot (sample)</b>", styles["Heading2"]))
        t = Table(products_df_preview, repeatRows=1)
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
                ]
            )
        )
        story.append(t)

    doc.build(story)
    output_path.write_bytes(buf.getvalue())
    return output_path
