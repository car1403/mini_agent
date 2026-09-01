import httpx
from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.rag.chunking import split_document
from app.rag.documents import TRAVEL_DOCUMENTS
from app.rag.pgvector_store import connect
from app.rag.service import answer, index_documents, search
from app.schemas import (
    ChunkPreviewRequest, RagAnswerRequest, RagAnswerResult, RagIndexRequest,
    RagIndexResult, RagSearchRequest, RagSearchResult,
)


rag_router = APIRouter(prefix="/api/rag", tags=["04 · RAG"])


@rag_router.get("/documents")
def documents() -> dict:
    return {"documents": TRAVEL_DOCUMENTS}


@rag_router.post("/chunks")
def preview_chunks(payload: ChunkPreviewRequest) -> dict:
    chunks = split_document(
        payload.text,
        source=payload.source,
        title=payload.title,
        sentences_per_chunk=payload.sentences_per_chunk,
    )
    return {"count": len(chunks), "chunks": [chunk.model_dump() for chunk in chunks]}


@rag_router.post("/search", response_model=RagSearchResult)
def retrieve(payload: RagSearchRequest) -> RagSearchResult:
    try:
        results = search(payload.query, payload.mode, payload.top_k)
        return RagSearchResult(query=payload.query, mode=payload.mode, results=results)
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"{payload.mode} 검색 실패: {error}") from error


@rag_router.post("/answer", response_model=RagAnswerResult)
def create_grounded_answer(payload: RagAnswerRequest) -> RagAnswerResult:
    try:
        return answer(payload.query, payload.mode, payload.top_k, payload.provider)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"RAG 답변 생성 실패: {error}") from error


@rag_router.post("/index", response_model=RagIndexResult)
def create_index(payload: RagIndexRequest) -> RagIndexResult:
    try:
        return index_documents(payload.reset_collection)
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"문서 색인 실패: {error}") from error


@rag_router.get("/status")
def status() -> dict:
    result = {
        "ollama": {"ok": False, "url": settings.ollama_base_url},
        "postgres": {"ok": False},
        "embedding_model": settings.ollama_embedding_model,
        "collection": settings.rag_collection,
    }
    try:
        response = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=3)
        response.raise_for_status()
        result["ollama"]["ok"] = True
    except Exception as error:
        result["ollama"]["error"] = str(error)
    try:
        with connect() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM documents WHERE collection_name = %s", (settings.rag_collection,))
            result["postgres"] = {"ok": True, "document_count": cursor.fetchone()[0]}
    except Exception as error:
        result["postgres"]["error"] = str(error)
    return result
