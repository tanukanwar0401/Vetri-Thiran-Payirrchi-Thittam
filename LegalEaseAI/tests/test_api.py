
import os

# Make API tests independent of Gemini.
os.environ["DEMO_MODE"] = "true"


from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(
    app
)


def test_root():

    response = client.get(
        "/"
    )

    assert response.status_code == 200

    assert (
        response.json()["status"]
        == "running"
    )


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert (
        response.json()["status"]
        == "ok"
    )


def test_generate_demo_document():

    payload = {
        "document_type": "NDA",
        "parties": (
            "Jane Doe (Disclosing Party), "
            "TechNova Inc. (Receiving Party)"
        ),
        "terms": (
            "Confidentiality; "
            "No unauthorized disclosure; "
            "15 day termination notice"
        ),
        "dates": "2026-04-15",
        "jurisdiction": "India",
    }

    response = client.post(
        "/generate",
        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["document_type"]
        == "NDA"
    )

    assert (
        "Confidentiality"
        in data["content"]
    )

    assert (
        data["demo_mode"]
        is True
    )


def test_generate_validation():

    response = client.post(
        "/generate",
        json={
            "document_type": "",
            "parties": "A",
            "terms": "B",
            "dates": "C",
        },
    )

    assert (
        response.status_code
        == 422
    )