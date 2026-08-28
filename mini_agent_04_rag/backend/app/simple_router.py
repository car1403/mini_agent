"""초보자용 RAG 화면에서 사용하는 최소 API입니다."""

from hashlib import sha256

import httpx
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import settings
from app.rag.chunking import split_document
from app.rag.documents import TRAVEL_DOCUMENTS
from app.rag.pdf_ingestion import pdf_to_chunks
from app.rag.pgvector_store import connect
from app.rag import redis_cache
from app.schemas import AnswerRequest, ChunkRequest, SearchRequest, SearchResult
from app.simple_service import (
    answer_question,
    index_custom_chunks,
    index_example_documents,
    search_documents,
)


router = APIRouter(prefix="/api/rag", tags=["RAG"])


@router.get("/documents")
def documents() -> dict:
    return {"documents": TRAVEL_DOCUMENTS}


@router.post("/chunks")
def chunks(payload: ChunkRequest) -> dict:
    result = split_document(
        payload.text,
        source=payload.source,
        title=payload.title,
        sentences_per_chunk=payload.sentences_per_chunk,
    )
    return {"count": len(result), "chunks": result}


@router.post("/index")
def index_documents():
    try:
        return index_example_documents()
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"문서 색인 실패: {error}") from error


@router.post("/search", response_model=SearchResult)
def search(payload: SearchRequest) -> SearchResult:
    try:
        results = search_documents(
            payload.question,
            payload.mode,
            payload.top_k,
            payload.score_threshold,
            payload.metadata_filter,
        )
        return SearchResult(
            question=payload.question,
            mode=payload.mode,
            results=results,
        )
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"검색 실패: {error}") from error


@router.post("/answer")
def answer(payload: AnswerRequest):
    try:
        return answer_question(
            payload.question,
            payload.mode,
            payload.top_k,
            payload.use_ollama,
            payload.use_cache,
            payload.score_threshold,
            payload.metadata_filter,
        )
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"RAG 답변 실패: {error}") from error


@router.post("/pdf")
async def index_pdf(pdf: UploadFile = File(...)):
    filename = pdf.filename or "document.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=422, detail="PDF 파일만 업로드할 수 있습니다.")

    content = await pdf.read()
    max_bytes = settings.max_pdf_size_mb * 1024 * 1024
    if not content:
        raise HTTPException(status_code=422, detail="빈 PDF 파일입니다.")
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"PDF는 {settings.max_pdf_size_mb}MB 이하만 업로드할 수 있습니다.",
        )
    try:
        source = filename
        chunks = pdf_to_chunks(content, source=source, title=filename)
        chunks = [
            chunk.model_copy(update={
                "metadata": {
                    **chunk.metadata,
                    "file_sha256": sha256(content).hexdigest(),
                }
            })
            for chunk in chunks
        ]
        return index_custom_chunks(chunks, source)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"PDF 색인 실패: {error}") from error


@router.get("/status")
def status() -> dict:
    result = {
        "ollama": False,
        "postgres": False,
        "redis": False,
        "embedding_model": settings.ollama_embedding_model,
    }
    try:
        response = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=3)
        response.raise_for_status()
        result["ollama"] = True
    except Exception:
        pass
    try:
        with connect() as connection:
            connection.execute("SELECT 1")
        result["postgres"] = True
    except Exception:
        pass
    try:
        result["redis"] = bool(redis_cache.client().ping())
    except Exception:
        pass
    return result
