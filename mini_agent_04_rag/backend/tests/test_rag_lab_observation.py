from fastapi.testclient import TestClient

from app.main import app
from app.schemas import RagSearchItem


client = TestClient(app)


def test_indexed_source_endpoint_exposes_replacement_state(monkeypatch) -> None:
    from app.routers import rag_router

    monkeypatch.setattr(
        rag_router,
        "source_documents",
        lambda source: [
            RagSearchItem(
                title="호텔 환불 정책 v2",
                content="당일 취소는 환불되지 않습니다.",
                source=source,
                chunk_index=0,
                metadata={"document_version": 2},
                score=0,
            )
        ],
    )
    response = client.get("/api/rag/indexed", params={"source": "lab-policy.md"})
    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "lab-policy.md"
    assert body["count"] == 1
    assert body["chunks"][0]["metadata"]["document_version"] == 2
