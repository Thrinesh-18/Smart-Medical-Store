from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_search():
    response = client.post("/search", json={"query": "fever medicine", "top_k": 5, "use_hybrid": True})
    assert response.status_code == 200
    body = response.json()
    assert "results" in body
