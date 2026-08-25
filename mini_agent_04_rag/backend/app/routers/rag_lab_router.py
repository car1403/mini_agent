"""RAG Lab 03~04의 실제 pgvector API입니다."""

from typing import Literal

from fastapi import APIRouter, Header, HTTPException

from app.rag.lab_service import (
    evaluate_retrieval, run_multi_tool_agent, search_internal_policies,
    search_products, seed_evaluation_documents, seed_internal_policies,
    seed_multi_tool_documents, seed_products,
)
from app.rag import redis_cache
from app.schemas import (
    AclSearchRequest, AclSearchResult, ProductSearchRequest,
    ProductSearchResult, RagIndexResult, RetrievalEvaluationRequest,
    RetrievalEvaluationResult, MultiToolRagRequest, MultiToolRagResult,
)


rag_lab_router = APIRouter(prefix="/api/rag/labs", tags=["04 · RAG Labs"])


@rag_lab_router.post("/products/seed", response_model=RagIndexResult)
def create_product_catalog() -> RagIndexResult:
    try:
        return seed_products()
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"상품 Catalog 색인 실패: {error}") from error


@rag_lab_router.post("/products/search", response_model=ProductSearchResult)
def retrieve_products(payload: ProductSearchRequest) -> ProductSearchResult:
    try:
        return search_products(payload)
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"상품 검색 실패: {error}") from error


@rag_lab_router.post("/policies/seed", response_model=RagIndexResult)
def create_internal_policies() -> RagIndexResult:
    try:
        return seed_internal_policies()
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"사내 규정 색인 실패: {error}") from error


@rag_lab_router.post("/policies/search", response_model=AclSearchResult)
def retrieve_internal_policies(
    payload: AclSearchRequest,
    x_demo_role: Literal["employee", "manager", "hr"] = Header(alias="X-Demo-Role"),
) -> AclSearchResult:
    try:
        return search_internal_policies(payload, authenticated_role=x_demo_role)
    except ValueError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"사내 규정 검색 실패: {error}") from error


@rag_lab_router.post("/evaluation/seed", response_model=RagIndexResult)
def create_evaluation_documents() -> RagIndexResult:
    try:
        return seed_evaluation_documents()
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"평가 문서 색인 실패: {error}") from error


@rag_lab_router.post("/evaluation/run", response_model=RetrievalEvaluationResult)
def run_retrieval_evaluation(
    payload: RetrievalEvaluationRequest,
) -> RetrievalEvaluationResult:
    try:
        return evaluate_retrieval(payload)
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"검색 평가 실패: {error}") from error


@rag_lab_router.post("/multi-agent/seed", response_model=RagIndexResult)
def create_multi_tool_documents() -> RagIndexResult:
    try:
        return seed_multi_tool_documents()
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Multi-Tool 문서 색인 실패: {error}") from error


@rag_lab_router.post("/multi-agent/run", response_model=MultiToolRagResult)
def run_multi_agent(payload: MultiToolRagRequest) -> MultiToolRagResult:
    try:
        return run_multi_tool_agent(payload)
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Multi-Tool Agent 실행 실패: {error}") from error


@rag_lab_router.delete("/multi-agent/state")
def reset_multi_agent_state(session_id: str) -> dict:
    try:
        return {"session_id": session_id, "deleted": redis_cache.delete_agent_state(session_id)}
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Agent 상태 초기화 실패: {error}") from error
