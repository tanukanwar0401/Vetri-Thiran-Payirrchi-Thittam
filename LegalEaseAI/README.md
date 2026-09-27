# LegalEase

AI-Powered Legal Document Generator

LegalEase is a Generative AI application for creating editable
legal-document drafts using a Streamlit frontend, FastAPI backend,
and Google Gemini.

---

# Features

- AI-powered legal document generation
- Employment contracts
- NDA documents
- Lease agreements
- Employment offer letters
- Service agreements
- Freelance contracts
- General agreements
- Custom document types
- Editable generated documents
- HTML preview
- TXT export
- DOCX export
- PDF export
- Logo branding
- Terms table
- Footer
- FastAPI Swagger documentation
- Gemini integration
- Demo mode
- Automated tests
- Docker support

---

# Project Structure

```text
LegalEase/
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   ├── config.py
│   │
│   ├── ai_core/
│   │   ├── __init__.py
│   │   └── gemini_generator.py
│   │
│   ├── formatters/
│   │   ├── __init__.py
│   │   ├── common.py
│   │   ├── docx_formatter.py
│   │   ├── pdf_formatter.py
│   │   └── txt_formatter.py
│   │
│   └── models/
│       ├── __init__.py
│       └── schemas.py
│
├── frontend/
│   ├── __init__.py
│   └── app.py
│
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   └── test_formatting.py
│
├── assets/
│   └── logo.png
│
├── .streamlit/
│   └── config.toml
│
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── Procfile
├── requirements.txt
└── README.md