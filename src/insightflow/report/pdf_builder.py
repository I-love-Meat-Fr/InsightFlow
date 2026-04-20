from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _cell_paragraph(text: Any, style: ParagraphStyle) -> Paragraph:
    if text is None:
        s = ""
    elif isinstance(text, bool):
        s = "yes" if text else "no"
    else:
        s = str(text)
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(s, style)


def _build_snapshot_table(
    raw: list[list[Any]],
    usable_width: float,
    styles: ParagraphStyle,
    header_style: ParagraphStyle,
) -> Table:
    """Turn raw header + rows into a wrapped-cell table with sane column widths."""
    if not raw or len(raw) < 2:
        return Table([["(no rows)"]])

    header = raw[0]
    ncols = len(header)

    def norm_key(h: Any) -> str:
        return str(h).strip().lower()

    keys = [norm_key(h) for h in header]
    width_fracs: list[float] = []
    for k in keys:
        if k == "title":
            width_fracs.append(0.26)
        elif k == "url":
            width_fracs.append(0.34)
        elif k == "target_id":
            width_fracs.append(0.14)
        elif k in ("price", "currency", "price_outlier"):
            width_fracs.append(0.09)
        else:
            width_fracs.append(0.10)

    total_frac = sum(width_fracs)
    width_fracs = [w / total_frac for w in width_fracs]
    col_widths = [usable_width * f for f in width_fracs]

    body: list[list[Any]] = [[_cell_paragraph(h, header_style) for h in header]]
    for row in raw[1:]:
        pad = row + [""] * (ncols - len(row))
        pad = pad[:ncols]
        body.append([_cell_paragraph(c, styles) for c in pad])

    t = Table(body, colWidths=col_widths, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    return t


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

    usable_w = A4[0] - doc.leftMargin - doc.rightMargin
    cell_style = ParagraphStyle(
        "tblcell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7,
        leading=9,
        alignment=TA_LEFT,
    )
    header_cell_style = ParagraphStyle(
        "tblhdr",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.whitesmoke,
        alignment=TA_LEFT,
    )

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
        story.append(
            _build_snapshot_table(
                products_df_preview,
                float(usable_w),
                cell_style,
                header_cell_style,
            )
        )

    doc.build(story)
    output_path.write_bytes(buf.getvalue())
    return output_path
