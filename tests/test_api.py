"""
Basic tests: happy path, sad path (empty query), and that inventory
questions route to the tool call rather than the LLM.

Run: pytest
Note: tests that hit /ask with a document question call the free Groq API,
so GROQ_API_KEY must be set and the Chroma collection must be built first
(python data/generate_data.py && python -m app.ingest).
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_empty_question_returns_400():
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 400


def test_inventory_question_routes_to_tool():
    response = client.post("/ask", json={"question": "How many units of Cotton Fabric are in stock?"})
    assert response.status_code == 200
    body = response.json()
    assert body["route"] == "inventory_tool"
    assert "Cotton Fabric" in body["answer"]


def test_document_question_routes_to_rag():
    response = client.post("/ask", json={"question": "What invoices are overdue?"})
    assert response.status_code == 200
    body = response.json()
    assert body["route"] == "rag"
    assert isinstance(body["sources"], list)
