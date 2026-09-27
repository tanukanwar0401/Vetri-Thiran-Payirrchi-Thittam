from __future__ import annotations

from io import BytesIO
from pathlib import Path
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.shared import Inches, Pt

from backend.formatters.common import sanitize_text


def _add_footer(
    document: Document
) -> None:

    section = document.sections[-1]

    footer = section.footer

    paragraph = footer.paragraphs[0]

    paragraph.alignment = (
        WD_ALIGN_PARAGRAPH.CENTER
    )

    run = paragraph.add_run(
        "LegalEase — AI-generated draft. "
        "Review with a qualified legal professional."
    )

    run.font.name = "Times New Roman"

    run.font.size = Pt(8)


def _add_terms_table(
    document: Document,
    terms: list[str]
) -> None:

    if not terms:
        return

    table = document.add_table(
        rows=1,
        cols=2
    )

    table.alignment = (
        WD_TABLE_ALIGNMENT.CENTER
    )

    table.style = "Table Grid"

    header_cells = table.rows[0].cells

    header_cells[0].text = "No."
    header_cells[1].text = "Term"

    for index, term in enumerate(
        terms,
        start=1
    ):

        cells = table.add_row().cells

        cells[0].text = str(index)
        cells[1].text = term


def format_docx(
    text: str,
    doc_type: str = "Legal Document",
    logo_path: Path | None = None,
    terms: list[str] | None = None,
) -> bytes:

    document = Document()

    # --------------------------------------------------
    # PAGE MARGINS
    # --------------------------------------------------

    section = document.sections[0]

    section.top_margin = Inches(
        0.75
    )

    section.bottom_margin = Inches(
        0.75
    )

    section.left_margin = Inches(
        0.9
    )

    section.right_margin = Inches(
        0.9
    )

    # --------------------------------------------------
    # DEFAULT FONT
    # --------------------------------------------------

    normal_style = document.styles[
        "Normal"
    ]

    normal_style.font.name = (
        "Times New Roman"
    )

    normal_style.font.size = Pt(
        11
    )

    # --------------------------------------------------
    # LOGO
    # --------------------------------------------------

    if (
        logo_path
        and Path(logo_path).exists()
    ):

        try:

            paragraph = document.add_paragraph()

            paragraph.alignment = (
                WD_ALIGN_PARAGRAPH.CENTER
            )

            paragraph.add_run().add_picture(
                str(logo_path),
                width=Inches(1.2)
            )

        except Exception:
            pass

    # --------------------------------------------------
    # DOCUMENT TITLE
    # --------------------------------------------------

    title = document.add_paragraph()

    title.alignment = (
        WD_ALIGN_PARAGRAPH.CENTER
    )

    run = title.add_run(
        doc_type
    )

    run.bold = True

    run.font.name = (
        "Times New Roman"
    )

    run.font.size = Pt(
        16
    )

    # --------------------------------------------------
    # DOCUMENT BODY
    # --------------------------------------------------

    clean_text = sanitize_text(
        text
    )

    for raw_line in clean_text.splitlines():

        line = raw_line.strip()

        if not line:
            continue

        if line.startswith("### "):

            paragraph = document.add_paragraph()

            run = paragraph.add_run(
                line[4:]
            )

            run.bold = True
            run.font.size = Pt(12)

        elif line.startswith("## "):

            paragraph = document.add_paragraph()

            run = paragraph.add_run(
                line[3:]
            )

            run.bold = True
            run.font.size = Pt(13)

        elif line.startswith("# "):

            paragraph = document.add_paragraph()

            run = paragraph.add_run(
                line[2:]
            )

            run.bold = True
            run.font.size = Pt(15)

        elif re.match(
            r"^\d+\.\s+",
            line
        ):

            paragraph = document.add_paragraph(
                style="List Number"
            )

            paragraph.paragraph_format.space_after = Pt(
                4
            )

            paragraph.add_run(
                re.sub(
                    r"^\d+\.\s+",
                    "",
                    line
                )
            )

        elif line.startswith("- "):

            paragraph = document.add_paragraph(
                style="List Bullet"
            )

            paragraph.add_run(
                line[2:]
            )

        else:

            paragraph = document.add_paragraph()

            paragraph.paragraph_format.space_after = Pt(
                6
            )

            parts = re.split(
                r"(\*\*.*?\*\*)",
                line
            )

            for part in parts:

                if (
                    part.startswith("**")
                    and part.endswith("**")
                ):

                    run = paragraph.add_run(
                        part[2:-2]
                    )

                    run.bold = True

                else:

                    paragraph.add_run(
                        part
                    )

    # --------------------------------------------------
    # TERMS TABLE
    # --------------------------------------------------

    if terms:

        heading = document.add_paragraph()

        heading_run = heading.add_run(
            "Key Terms Table"
        )

        heading_run.bold = True
        heading_run.font.size = Pt(13)

        _add_terms_table(
            document,
            terms
        )

    # --------------------------------------------------
    # FOOTER
    # --------------------------------------------------

    _add_footer(
        document
    )

    output = BytesIO()

    document.save(
        output
    )

    return output.getvalue()