from __future__ import annotations

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class DocumentRequest(BaseModel):
    """
    Request payload used to generate a legal document.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True
    )

    document_type: str = Field(
        ...,
        min_length=2,
        max_length=120
    )

    parties: str = Field(
        ...,
        min_length=2,
        max_length=5000
    )

    terms: str = Field(
        ...,
        min_length=2,
        max_length=12000
    )

    dates: str = Field(
        ...,
        min_length=2,
        max_length=200
    )

    jurisdiction: str = Field(
        default="",
        max_length=200
    )

    @field_validator(
        "document_type",
        "parties",
        "terms",
        "dates"
    )
    @classmethod
    def reject_empty(
        cls,
        value: str
    ) -> str:

        if not value.strip():
            raise ValueError(
                "This field cannot be empty."
            )

        return value.strip()


class DocumentResponse(BaseModel):
    """
    Response returned after document generation.
    """

    document_type: str
    content: str
    model: str
    demo_mode: bool