from __future__ import annotations

from dataclasses import dataclass

from backend.config import Settings


@dataclass
class GenerationResult:
    """
    Result returned by the document generator.
    """

    content: str
    model: str
    demo_mode: bool


class GeminiDocumentGenerator:
    """
    Gemini-powered legal document generator.

    Demo mode is included so the application can be tested
    without a Gemini API key.
    """

    def __init__(
        self,
        settings: Settings
    ):
        self.settings = settings

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
        jurisdiction: str = "",
    ) -> GenerationResult:

        # --------------------------------------------------
        # DEMO MODE
        # --------------------------------------------------

        if self.settings.demo_mode:

            return GenerationResult(
                content=self._demo_document(
                    document_type=document_type,
                    parties=parties,
                    terms=terms,
                    dates=dates,
                    jurisdiction=jurisdiction,
                ),
                model="demo",
                demo_mode=True,
            )

        # --------------------------------------------------
        # API KEY CHECK
        # --------------------------------------------------

        if not self.settings.gemini_api_key:

            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Add it to .env or set DEMO_MODE=true."
            )

        # --------------------------------------------------
        # GOOGLE GEN AI SDK
        # --------------------------------------------------

        try:
            from google import genai

        except ImportError as exc:

            raise RuntimeError(
                "The Google Gen AI SDK is not installed. "
                "Run: pip install google-genai"
            ) from exc

        # --------------------------------------------------
        # CREATE CLIENT
        # --------------------------------------------------

        client = genai.Client(
            api_key=self.settings.gemini_api_key
        )

        prompt = self._build_prompt(
            document_type=document_type,
            parties=parties,
            terms=terms,
            dates=dates,
            jurisdiction=jurisdiction,
        )

        # --------------------------------------------------
        # GENERATE
        # --------------------------------------------------

        response = client.models.generate_content(
            model=self.settings.gemini_model,
            contents=prompt,
        )

        generated_text = getattr(
            response,
            "text",
            None
        )

        if not generated_text:

            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return GenerationResult(
            content=generated_text.strip(),
            model=self.settings.gemini_model,
            demo_mode=False,
        )

    @staticmethod
    def _build_prompt(
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
        jurisdiction: str,
    ) -> str:

        jurisdiction_value = (
            jurisdiction
            if jurisdiction
            else "Not specified."
        )

        prompt = f"""
You are the legal-document drafting engine for LegalEase.

Create a professional DRAFT of the requested legal document.

The user has provided factual information. Use that information
to create a structured document.

IMPORTANT RULES:

1. Do not invent facts.
2. Do not invent names.
3. Do not invent dates.
4. Do not invent addresses.
5. Do not invent financial amounts.
6. Do not invent legal citations.
7. Do not invent jurisdiction-specific requirements.
8. If information is missing, use [NOT PROVIDED].
9. Preserve the user's stated terms.
10. Do not claim the document was reviewed by a lawyer.
11. Do not claim that the document is legally valid or enforceable.
12. This is an AI-generated draft for informational purposes.
13. Use professional formal language.
14. Create clear numbered sections.
15. Include signature blocks where appropriate.
16. Include an informational disclaimer at the end.

Return only the document.

DOCUMENT TYPE:
{document_type}

PARTIES:
{parties}

TERMS AND CONDITIONS:
{terms}

EFFECTIVE DATE:
{dates}

JURISDICTION:
{jurisdiction_value}
"""

        return prompt.strip()

    @staticmethod
    def _demo_document(
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
        jurisdiction: str,
    ) -> str:

        term_items = [
            item.strip()
            for item in terms.split(";")
            if item.strip()
        ]

        if term_items:

            terms_block = "\n".join(
                f"{index}. {term}"
                for index, term
                in enumerate(term_items, start=1)
            )

        else:

            terms_block = (
                "1. [NOT PROVIDED]"
            )

        jurisdiction_text = (
            jurisdiction
            if jurisdiction
            else "[NOT PROVIDED]"
        )

        return f"""
# {document_type}

**Effective Date:** {dates}

**Jurisdiction:** {jurisdiction_text}

## 1. Parties

{parties}

## 2. Purpose

The parties intend to enter into this
{document_type} on the effective date specified above,
subject to the terms contained in this document.

## 3. Terms and Conditions

{terms_block}

## 4. General Provisions

The parties should review all provisions for accuracy,
completeness, and consistency with applicable law before
signing this document.

## 5. Signatures

**Party 1**

Signature: ______________________________

Name: ___________________________________

Date: ___________________________________


**Party 2**

Signature: ______________________________

Name: ___________________________________

Date: ___________________________________

## Important Notice

This demo document is generated for software testing only.
It is not legal advice and should not be relied upon as a
substitute for review by a qualified legal professional.
""".strip()