from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_and_mock_default() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["stage"] == "mini_agent_04_rag"
    assert response.json()["default_provider"] == "mock"


def test_documents_are_available_without_docker() -> None:
    response = client.get("/api/rag/documents")
    assert response.status_code == 200
    assert len(response.json()["documents"]) == 3


def test_chunk_preview_keeps_metadata() -> None:
    response = client.post(
        "/api/rag/chunks",
        json={
            "text": "첫 문장입니다. 두 번째 문장입니다. 세 번째 문장입니다.",
            "source": "lesson.md",
            "title": "수업 문서",
            "sentences_per_chunk": 2,
        },
    )
    assert response.status_code == 200
    assert response.json()["count"] == 2
    assert response.json()["chunks"][0]["source"] == "lesson.md"


def test_keyword_search_finds_refund_document() -> None:
    response = client.post(
        "/api/rag/search",
        json={"query": "호텔 당일 취소 환불", "mode": "keyword", "top_k": 2},
    )
    assert response.status_code == 200
    assert response.json()["results"][0]["source"] == "hotel-refund.md"


def test_mock_answer_includes_source() -> None:
    response = client.post(
        "/api/rag/answer",
        json={
            "query": "수하물은 몇 kg인가요?",
            "mode": "keyword",
            "top_k": 2,
            "provider": "mock",
        },
    )
    assert response.status_code == 200
    assert response.json()["grounded"] is True
    assert "baggage.md" in response.json()["sources"]


def test_unknown_question_is_not_answered() -> None:
    response = client.post(
        "/api/rag/answer",
        json={
            "query": "여권을 잃어버리면 어떻게 하나요?",
            "mode": "keyword",
            "top_k": 2,
            "provider": "mock",
        },
    )
    assert response.status_code == 200
    assert response.json()["grounded"] is False
    assert response.json()["sources"] == []
