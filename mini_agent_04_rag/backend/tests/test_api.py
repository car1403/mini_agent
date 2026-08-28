from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_make_chunks() -> None:
    response = client.post("/api/rag/chunks", json={
        "text": "첫 문장입니다. 두 번째 문장입니다. 세 번째 문장입니다.",
        "sentences_per_chunk": 2,
    })
    assert response.status_code == 200
    assert response.json()["count"] == 2


def test_keyword_search_without_docker() -> None:
    response = client.post("/api/rag/search", json={
        "question": "호텔 당일 취소 환불",
        "mode": "keyword",
        "top_k": 2,
    })
    assert response.status_code == 200
    assert response.json()["results"][0]["source"] == "hotel-refund.md"


def test_grounded_mock_answer_without_docker() -> None:
    response = client.post("/api/rag/answer", json={
        "question": "수하물은 몇 kg인가요?",
        "mode": "keyword",
        "use_ollama": False,
        "use_cache": False,
    })
    assert response.status_code == 200
    assert response.json()["grounded"] is True
    assert "baggage.md" in response.json()["sources"]
