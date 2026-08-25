from fastapi.testclient import TestClient

from app.main import app
from app.schemas import RagSearchRequest


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
            "use_cache": False,
        },
    )
    assert response.status_code == 200
    assert response.json()["grounded"] is True
    assert "baggage.md" in response.json()["sources"]
    assert [item["stage"] for item in response.json()["trace"]] == [
        "cache", "retrieval", "context", "generation",
    ]


def test_rag_answer_uses_redis_cache_when_available(monkeypatch) -> None:
    from app.rag import redis_cache

    cached = {
        "answer": "Cache 답변",
        "grounded": True,
        "provider": "mock",
        "search_mode": "keyword",
        "sources": ["baggage.md"],
    }
    monkeypatch.setattr(redis_cache, "get", lambda key: (cached, 120))

    response = client.post(
        "/api/rag/answer",
        json={"query": "수하물", "mode": "keyword", "provider": "mock", "use_cache": True},
    )
    assert response.status_code == 200
    assert response.json()["cache_hit"] is True
    assert response.json()["cache_ttl_seconds"] == 120
    assert response.json()["trace"][0]["stage"] == "cache"


def test_unknown_question_is_not_answered() -> None:
    response = client.post(
        "/api/rag/answer",
        json={
            "query": "여권을 잃어버리면 어떻게 하나요?",
            "mode": "keyword",
            "top_k": 2,
            "provider": "mock",
            "use_cache": False,
        },
    )
    assert response.status_code == 200
    assert response.json()["grounded"] is False
    assert response.json()["sources"] == []


def test_advanced_search_contract() -> None:
    request = RagSearchRequest.model_validate({
        "query": "반려동물 비용", "mode": "hybrid", "top_k": 5,
        "score_threshold": 0.4,
        "metadata_filter": {"category": "hotel", "status": "active"},
    })
    assert request.mode == "hybrid"
    assert request.metadata_filter["status"] == "active"


def test_pdf_endpoint_rejects_non_pdf() -> None:
    response = client.post(
        "/api/rag/pdf",
        files={"pdf": ("policy.txt", b"not a pdf", "text/plain")},
        data={"title": "잘못된 파일"},
    )
    assert response.status_code == 422


def test_text_index_validates_empty_content() -> None:
    response = client.post(
        "/api/rag/texts",
        json={"title": "빈 문서", "content": "", "source": "empty.md"},
    )
    assert response.status_code == 422


def test_rag_status_reports_embedding_model_availability(monkeypatch) -> None:
    from app.routers import rag_router

    class Response:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"models": [{"name": "llama3.2:latest"}, {"name": "embeddinggemma:latest"}]}

    monkeypatch.setattr(rag_router.httpx, "get", lambda *args, **kwargs: Response())
    monkeypatch.setattr(
        rag_router,
        "connect",
        lambda: (_ for _ in ()).throw(RuntimeError("postgres not required for this assertion")),
    )
    monkeypatch.setattr(rag_router.redis_cache, "ping", lambda: False)

    response = client.get("/api/rag/status")

    assert response.status_code == 200
    assert response.json()["ollama"]["embedding_model_available"] is True
