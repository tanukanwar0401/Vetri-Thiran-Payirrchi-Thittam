from __future__ import annotations

from fastapi import (
    APIRouter,
    HTTPException,
)
from fastapi.responses import Response

from backend.ai_core.gemini_generator import (
    GeminiDocumentGenerator,
)
from backend.config import get_settings
from backend.formatters.docx_formatter import (
    format_docx,
)
from backend.formatters.pdf_formatter import (
    format_pdf,
)
from backend.formatters.txt_formatter import (
    format_txt,
)
from backend.models.schemas import (
    DocumentRequest,
    DocumentResponse,
)


router = APIRouter()

settings = get_settings()

generator = GeminiDocumentGenerator(
    settings
)


def _terms_list(
    terms: str
) -> list[str]:

    return [
        item.strip()
        for item in terms.split(";")
        if item.strip()
    ]


@router.post(
    "/generate",
    response_model=DocumentResponse
)
def generate_document(
    request: DocumentRequest
) -> DocumentResponse:

    try:

        result = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            dates=request.dates,
            jurisdiction=request.jurisdiction,
        )

        return DocumentResponse(
            document_type=request.document_type,
            content=result.content,
            model=result.model,
            demo_mode=result.demo_mode,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc


@router.post(
    "/export/txt"
)
def export_txt(
    request: DocumentRequest
) -> Response:

    content = format_txt(
        request.terms
    )

    return Response(
        content=content,
        media_type="text/plain; charset=utf-8",
        headers={
            "Content-Disposition":
                'attachment; filename="legalease.txt"'
        },
    )


@router.post(
    "/export/docx"
)
def export_docx(
    request: DocumentRequest
) -> Response:

    try:

        content = format_docx(
            text=request.terms,
            doc_type=request.document_type,
            logo_path=settings.logo_path,
            terms=_terms_list(
                request.terms
            ),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"DOCX export failed: {exc}",
        ) from exc

    return Response(
        content=content,
        media_type=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
        headers={
            "Content-Disposition":
                'attachment; filename="legalease.docx"'
        },
    )


@router.post(
    "/export/pdf"
)
def export_pdf(
    request: DocumentRequest
) -> Response:

    try:

        content = format_pdf(
            text=request.terms,
            doc_type=request.document_type,
            logo_path=settings.logo_path,
            terms=_terms_list(
                request.terms
            ),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"PDF export failed: {exc}",
        ) from exc

    return Response(
        content=content,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                'attachment; filename="legalease.pdf"'
        },
    )