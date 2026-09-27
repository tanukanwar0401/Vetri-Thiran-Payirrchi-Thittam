from __future__ import annotations

from io import BytesIO
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from backend.formatters.common import sanitize_text


def format_pdf(
    text: str,
    doc_type: str = "Legal Document",
    logo_path: Path | None = None,
    terms: list[str] | None = None,
) -> bytes:

    output = BytesIO()

    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title=doc_type,
        author="LegalEase",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "LegalTitle",
        parent=styles["Title"],
        fontName="Times-Bold",
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        spaceAfter=14,
    )

    heading_style = ParagraphStyle(
        "LegalHeading",
        parent=styles["Heading1"],
        fontName="Times-Bold",
        fontSize=13,
        leading=17,
        spaceBefore=10,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "LegalBody",
        parent=styles["BodyText"],
        fontName="Times-Roman",
        fontSize=10.5,
        leading=15,
        spaceAfter=7,
    )

    bullet_style = ParagraphStyle(
        "LegalBullet",
        parent=body_style,
        leftIndent=16,
        firstLineIndent=-9,
    )

    footer_style = ParagraphStyle(
        "LegalFooter",
        parent=body_style,
        fontName="Times-Roman",
        fontSize=7.5,
        textColor=colors.grey,
        alignment=TA_CENTER,
    )

    story = []

    # --------------------------------------------------
    # LOGO
    # --------------------------------------------------

    if (
        logo_path
        and Path(logo_path).exists()
    ):

        try:

            logo = Image(
                str(logo_path),
                width=1.05 * inch,
                height=1.05 * inch,
            )

            story.append(
                logo
            )

            story.append(
                Spacer(1, 4)
            )

        except Exception:
            pass

    # --------------------------------------------------
    # TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            doc_type,
            title_style
        )
    )

    # --------------------------------------------------
    # BODY
    # --------------------------------------------------

    clean_text = sanitize_text(
        text
    )

    for raw_line in clean_text.splitlines():

        line = raw_line.strip()

        if not line:
            continue

        safe = (
            line
            .replace(
                "&",
                "&amp;"
            )
            .replace(
                "<",
                "&lt;"
            )
            .replace(
                ">",
                "&gt;"
            )
        )

        safe = re.sub(
            r"\*\*(.+?)\*\*",
            r"<b>\1</b>",
            safe
        )

        if line.startswith(
            "### "
        ):

            story.append(
                Paragraph(
                    safe[4:],
                    heading_style
                )
            )

        elif line.startswith(
            "## "
        ):

            story.append(
                Paragraph(
                    safe[3:],
                    heading_style
                )
            )

        elif line.startswith(
            "# "
        ):

            story.append(
                Paragraph(
                    safe[2:],
                    title_style
                )
            )

        elif re.match(
            r"^\d+\.\s+",
            line
        ):

            content = re.sub(
                r"^\d+\.\s+",
                "",
                safe
            )

            story.append(
                Paragraph(
                    content,
                    body_style
                )
            )

        elif line.startswith(
            "- "
        ):

            story.append(
                Paragraph(
                    f"• {safe[2:]}",
                    bullet_style
                )
            )

        else:

            story.append(
                Paragraph(
                    safe,
                    body_style
                )
            )

    # --------------------------------------------------
    # TERMS TABLE
    # --------------------------------------------------

    if terms:

        story.append(
            Spacer(1, 8)
        )

        story.append(
            Paragraph(
                "Key Terms Table",
                heading_style
            )
        )

        data = [
            ["No.", "Term"]
        ]

        for index, term in enumerate(
            terms,
            start=1
        ):

            data.append(
                [
                    str(index),
                    term
                ]
            )

        table = Table(
            data,
            colWidths=[
                0.45 * inch,
                5.9 * inch
            ],
            repeatRows=1,
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, -1),
                        "Times-Roman",
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Times-Bold",
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        9,
                    ),
                    (
                        "LEADING",
                        (0, 0),
                        (-1, -1),
                        12,
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.whitesmoke,
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                ]
            )
        )

        story.append(
            table
        )

    # --------------------------------------------------
    # FOOTER NOTICE
    # --------------------------------------------------

    story.append(
        Spacer(1, 12)
    )

    story.append(
        Paragraph(
            "LegalEase — AI-generated draft. "
            "Review with a qualified legal professional.",
            footer_style,
        )
    )

    # --------------------------------------------------
    # PAGE FOOTER
    # --------------------------------------------------

    def draw_page_footer(
        canvas,
        doc
    ):

        canvas.saveState()

        canvas.setFont(
            "Times-Roman",
            7.5
        )

        canvas.setFillColor(
            colors.grey
        )

        canvas.drawCentredString(
            A4[0] / 2,
            0.35 * inch,
            f"LegalEase • Page {doc.page}",
        )

        canvas.restoreState()

    document.build(
        story,
        onFirstPage=draw_page_footer,
        onLaterPages=draw_page_footer,
    )

    return output.getvalue()