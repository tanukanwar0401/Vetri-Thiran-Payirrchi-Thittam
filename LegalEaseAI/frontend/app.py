from __future__ import annotations

import os
from datetime import date

import requests
import streamlit as st

from backend.formatters.common import (
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


# ==========================================================
# CONFIGURATION
# ==========================================================

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


LOGO_PATH = os.path.join(
    PROJECT_ROOT,
    "assets",
    "logo.png"
)


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)


# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown(
    """
    <style>

    .hero {
        padding: 1.5rem;
        border-radius: 18px;
        background:
            linear-gradient(
                135deg,
                #111827,
                #1e1b4b
            );
        border: 1px solid #374151;
        margin-bottom: 1rem;
    }

    .hero h1 {
        margin: 0;
    }

    .hero p {
        color: #cbd5e1;
        margin-bottom: 0;
    }

    .preview {
        background: #0b1120;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 1.25rem;
        max-height: 650px;
        overflow-y: auto;
        color: #e5e7eb;
    }

    .preview h1,
    .preview h2,
    .preview h3 {
        color: #f8fafc;
    }

    .notice {
        padding: 0.8rem 1rem;
        border-left: 4px solid #7c3aed;
        background: #111827;
        border-radius: 6px;
        margin-bottom: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# HEADER
# ==========================================================

st.markdown(
    """
    <div class="hero">

        <h1>⚖️ LegalEase</h1>

        <p>
            AI-powered legal document drafting,
            editing, preview and export.
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="notice">

    <b>Important:</b>
    LegalEase produces drafts for informational purposes.
    Review the final document with a qualified legal
    professional before signing or relying on it.

    </div>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# SESSION STATE
# ==========================================================

if "document" not in st.session_state:

    st.session_state.document = ""


if "model" not in st.session_state:

    st.session_state.model = ""


if "demo_mode" not in st.session_state:

    st.session_state.demo_mode = False


# ==========================================================
# MAIN LAYOUT
# ==========================================================

left_column, right_column = st.columns(
    [0.9, 1.1],
    gap="large"
)


# ==========================================================
# LEFT SIDE
# ==========================================================

with left_column:

    st.subheader(
        "Document Details"
    )

    document_type = st.selectbox(
        "Document Type",
        [
            "Employment Contract",
            "NDA (Non-Disclosure Agreement)",
            "Lease Agreement",
            "Employment Offer Letter",
            "Service Agreement",
            "Freelance Work Contract",
            "General Agreement",
            "Custom",
        ],
    )

    if document_type == "Custom":

        document_type = st.text_input(
            "Custom document type",
            placeholder=(
                "e.g. Consulting Agreement"
            ),
        )

    parties = st.text_area(
        "Parties Involved",
        placeholder=(
            "Jane Doe (Service Provider), "
            "TechNova Inc. (Client)"
        ),
        height=120,
    )

    terms = st.text_area(
        "Terms & Conditions",
        placeholder=(
            "Payment within 30 days; "
            "Confidentiality must be maintained; "
            "Work must be delivered by the deadline; "
            "Either party may terminate with 15 days notice"
        ),
        height=180,
        help=(
            "Separate individual terms with semicolons (;)."
        ),
    )

    effective_date = st.date_input(
        "Effective Date",
        value=date.today()
    )

    jurisdiction = st.text_input(
        "Jurisdiction (optional)",
        placeholder="e.g. India, Tamil Nadu",
    )

    # ------------------------------------------------------
    # GENERATE BUTTON
    # ------------------------------------------------------

    generate_button = st.button(
        "✨ Generate Document",
        type="primary",
        use_container_width=True,
    )

    if generate_button:

        if not document_type.strip():

            st.error(
                "Enter a document type."
            )

        elif not parties.strip():

            st.error(
                "Enter the parties involved."
            )

        elif not terms.strip():

            st.error(
                "Enter at least one term."
            )

        else:

            payload = {
                "document_type": document_type,
                "parties": parties,
                "terms": terms,
                "dates": effective_date.isoformat(),
                "jurisdiction": jurisdiction,
            }

            try:

                with st.spinner(
                    "Generating document..."
                ):

                    response = requests.post(
                        f"{BACKEND_URL}/generate",
                        json=payload,
                        timeout=120,
                    )

                response.raise_for_status()

                data = response.json()

                st.session_state.document = (
                    data["content"]
                )

                st.session_state.model = (
                    data["model"]
                )

                st.session_state.demo_mode = (
                    data["demo_mode"]
                )

                st.success(
                    "Document generated successfully."
                )

            except requests.RequestException as exc:

                st.error(
                    "Could not connect to the FastAPI backend."
                )

                st.caption(
                    str(exc)
                )

            except Exception as exc:

                st.error(
                    f"Generation failed: {exc}"
                )


# ==========================================================
# RIGHT SIDE
# ==========================================================

with right_column:

    st.subheader(
        "Preview & Edit"
    )

    if st.session_state.document:

        display_mode = st.radio(
            "View Mode",
            [
                "Preview",
                "Edit",
            ],
            horizontal=True,
        )

        # --------------------------------------------------
        # PREVIEW
        # --------------------------------------------------

        if display_mode == "Preview":

            rendered_html = text_to_html(
                st.session_state.document
            )

            st.markdown(
                f"""
                <div class="preview">
                    {rendered_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

        # --------------------------------------------------
        # EDITOR
        # --------------------------------------------------

        else:

            st.session_state.document = (
                st.text_area(
                    "Editable Document",
                    value=st.session_state.document,
                    height=620,
                    label_visibility="collapsed",
                )
            )

        # --------------------------------------------------
        # MODEL INFORMATION
        # --------------------------------------------------

        model_text = (
            f"Model: {st.session_state.model}"
        )

        if st.session_state.demo_mode:

            model_text += (
                " • Demo mode"
            )

        st.caption(
            model_text
        )

        # --------------------------------------------------
        # EXPORT
        # --------------------------------------------------

        terms_list = [
            item.strip()
            for item in terms.split(";")
            if item.strip()
        ]

        docx_bytes = format_docx(
            text=st.session_state.document,
            doc_type=document_type
            or "Legal Document",
            logo_path=LOGO_PATH,
            terms=terms_list,
        )

        pdf_bytes = format_pdf(
            text=st.session_state.document,
            doc_type=document_type
            or "Legal Document",
            logo_path=LOGO_PATH,
            terms=terms_list,
        )

        txt_bytes = format_txt(
            st.session_state.document
        )

        st.subheader(
            "Download"
        )

        download_1, download_2, download_3 = (
            st.columns(3)
        )

        with download_1:

            st.download_button(
                "⬇️ TXT",
                data=txt_bytes,
                file_name="legalease.txt",
                mime="text/plain",
                use_container_width=True,
            )

        with download_2:

            st.download_button(
                "⬇️ DOCX",
                data=docx_bytes,
                file_name="legalease.docx",
                mime=(
                    "application/"
                    "vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
                use_container_width=True,
            )

        with download_3:

            st.download_button(
                "⬇️ PDF",
                data=pdf_bytes,
                file_name="legalease.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

    else:

        st.info(
            "Your generated document will appear here."
        )