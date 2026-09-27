from pathlib import Path

from docx import Document

from backend.formatters.common import (
    sanitize_text,
    text_to_html,
)
from backend.formatters.docx_formatter import (
    format_docx,
)
from backend.formatters.pdf_formatter import (
    format_pdf,
)
from backend.formatters.txt_formatter import (
    format_txt,
)


SAMPLE_DOCUMENT = """
# Freelance Work Contract

**Effective Date:** April 15, 2026

## 1. Parties

Jane Doe (Service Provider), TechNova Inc. (Client)

## 2. Terms

1. Payment within 30 days
2. Confidentiality must be maintained
- Either party may terminate with 15 days notice
"""


def test_sanitize_text():

    result = sanitize_text(
        "Hello\u2014world\u2019s\u00a0test"
    )

    assert result == (
        "Hello-world's test"
    )


def test_html_preview_escapes_html():

    result = text_to_html(
        "<script>alert('x')</script>"
    )

    assert "<script>" not in result

    assert (
        "&lt;script&gt;"
        in result
    )


def test_txt_export():

    result = format_txt(
        SAMPLE_DOCUMENT
    )

    assert isinstance(
        result,
        bytes
    )

    assert (
        b"Freelance Work Contract"
        in result
    )


def test_docx_export():

    result = format_docx(
        SAMPLE_DOCUMENT,
        "Freelance Work Contract",
        terms=[
            "Payment within 30 days",
            "Confidentiality must be maintained",
        ],
    )

    assert result[:2] == b"PK"

    path = Path(
        "test-output.docx"
    )

    path.write_bytes(
        result
    )

    try:

        document = Document(
            path
        )

        paragraphs = "\n".join(
            paragraph.text
            for paragraph
            in document.paragraphs
        )

        assert (
            "Freelance Work Contract"
            in paragraphs
        )

    finally:

        path.unlink(
            missing_ok=True
        )


def test_pdf_export():

    result = format_pdf(
        SAMPLE_DOCUMENT,
        "Freelance Work Contract",
        terms=[
            "Payment within 30 days"
        ],
    )

    assert result.startswith(
        b"%PDF"
    )