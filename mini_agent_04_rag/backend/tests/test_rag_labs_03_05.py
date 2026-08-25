from fastapi.testclient import TestClient

from app.main import app
from app.schemas import RagIndexResult, RagSearchItem


client = TestClient(app)


def item(title: str, *, category: str = "shoes", price: int = 89000) -> RagSearchItem:
    return RagSearchItem(
        title=title,
        content=f"{title} 상품 설명",
        source="lab-product-catalog.json",
        score=0.9,
        metadata={
            "dataset": "product", "category": category,
            "price": price, "status": "active", "sku": title,
        },
    )


def test_product_search_applies_backend_price_condition(monkeypatch) -> None:
    from app.rag import lab_service

    monkeypatch.setattr(
        lab_service,
        "search",
        lambda *args, **kwargs: [
            item("RUN-100", price=89000),
            item("TRAIL-20", price=129000),
        ],
    )
    response = client.post(
        "/api/rag/labs/products/search",
        json={
            "query": "가벼운 러닝화", "category": "shoes",
            "max_price": 100000, "top_k": 3,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["candidate_count"] == 2
    assert [result["metadata"]["sku"] for result in body["results"]] == ["RUN-100"]


def test_acl_role_is_required_as_header_not_body() -> None:
    response = client.post(
        "/api/rag/labs/policies/search",
        json={"query": "급여 정정", "top_k": 3, "role": "hr"},
    )
    assert response.status_code == 422


def test_acl_passes_authenticated_header_to_service(monkeypatch) -> None:
    from app.routers import rag_lab_router
    from app.schemas import AclSearchResult

    received: list[str] = []

    def search(payload, *, authenticated_role: str) -> AclSearchResult:
        received.append(authenticated_role)
        return AclSearchResult(
            role=authenticated_role,
            results=[],
            termination_reason="no_authorized_evidence",
        )

    monkeypatch.setattr(rag_lab_router, "search_internal_policies", search)
    response = client.post(
        "/api/rag/labs/policies/search",
        headers={"X-Demo-Role": "employee"},
        json={"query": "급여 정정", "top_k": 3},
    )
    assert response.status_code == 200
    assert received == ["employee"]
    assert response.json()["role"] == "employee"


def test_acl_rejects_unknown_header_role() -> None:
    response = client.post(
        "/api/rag/labs/policies/search",
        headers={"X-Demo-Role": "owner"},
        json={"query": "급여 정정", "top_k": 3},
    )
    assert response.status_code == 422


def test_pdf_chunks_keep_source_id_metadata() -> None:
    from app.rag import pdf_ingestion

    # PDF 파싱 자체는 pypdf 영역이므로 Reader만 작은 Fake로 교체합니다.
    class Page:
        def extract_text(self) -> str:
            return "박물관은 화요일에 휴관합니다."

    class Reader:
        def __init__(self, stream) -> None:
            self.pages = [Page()]

    original = pdf_ingestion.PdfReader
    pdf_ingestion.PdfReader = Reader
    try:
        chunks = pdf_ingestion.pdf_to_chunks(
            b"educational-pdf", source="guide.pdf", title="여행 가이드",
        )
    finally:
        pdf_ingestion.PdfReader = original

    assert chunks[0].metadata["source_id"] == "guide.pdf"
    assert chunks[0].metadata["page_number"] == 1


def test_pdf_endpoint_uses_content_hash_source(monkeypatch) -> None:
    from app.routers import rag_router
    from app.schemas import RagChunk

    received: dict[str, str] = {}

    def chunks(content: bytes, *, source: str, title: str):
        received["source"] = source
        return [RagChunk(
            chunk_id=f"{source}:0", text="여행 안내", source=source,
            title=title, chunk_index=0, metadata={"source_id": source},
        )]

    def index(items, *, source: str, replace_source: bool):
        return RagIndexResult(
            collection="mini_agent_travel", indexed_count=len(items),
            embedding_model="embeddinggemma", source=source,
        )

    monkeypatch.setattr(rag_router, "pdf_to_chunks", chunks)
    monkeypatch.setattr(rag_router, "index_chunks", index)
    response = client.post(
        "/api/rag/pdf",
        files={"pdf": ("guide.pdf", b"same-content", "application/pdf")},
        data={"title": "여행 가이드", "replace_source": "true"},
    )

    assert response.status_code == 200
    assert response.json()["source"] == received["source"]
    assert received["source"].startswith("guide.pdf:")
