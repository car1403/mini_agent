from dataclasses import asdict
from hashlib import sha256

import httpx
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.config import settings
from app.rag.chunking import split_document
from app.rag.documents import TRAVEL_DOCUMENTS
from app.rag.pgvector_store import connect, source_documents
from app.rag.pdf_ingestion import pdf_to_chunks
from app.rag import redis_cache
from app.rag.service import answer, index_chunks, index_documents, search
from app.services.generation_service import generate
from app.agents.tool_selector import select_tool
from app.tools.executor import execute_tool_safely
from app.schemas import (
    ChunkPreviewRequest, RagAnswerRequest, RagAnswerResult, RagIndexRequest,
    RagAgentRequest, RagAgentResult, RagIndexResult, RagSearchRequest,
    RagSearchItem, RagSearchResult, RagTextIndexRequest, ToolSelectionResult,
)


rag_router = APIRouter(prefix="/api/rag", tags=["04 · RAG"])


@rag_router.get("/documents")
def documents() -> dict:
    return {"documents": TRAVEL_DOCUMENTS}


@rag_router.get("/indexed")
def indexed_source(source: str) -> dict:
    """Source 교체 Lab에서 실제 저장된 Chunk 수와 내용을 확인합니다."""
    try:
        results = source_documents(source)
        return {"source": source, "count": len(results), "chunks": [item.model_dump() for item in results]}
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"색인 문서 조회 실패: {error}") from error


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
        results = search(
            payload.query, payload.mode, payload.top_k,
            payload.score_threshold, payload.metadata_filter,
        )
        return RagSearchResult(query=payload.query, mode=payload.mode, results=results)
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"{payload.mode} 검색 실패: {error}") from error


@rag_router.post("/answer", response_model=RagAnswerResult)
def create_grounded_answer(payload: RagAnswerRequest) -> RagAnswerResult:
    try:
        return answer(
            payload.query, payload.mode, payload.top_k, payload.provider,
            payload.use_cache, payload.score_threshold, payload.metadata_filter,
        )
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


@rag_router.post("/texts", response_model=RagIndexResult)
def create_text_index(payload: RagTextIndexRequest) -> RagIndexResult:
    try:
        chunks = split_document(
            payload.content, source=payload.source, title=payload.title,
            sentences_per_chunk=payload.sentences_per_chunk,
        )
        chunks = [
            chunk.model_copy(update={"metadata": {"input_type": "text", **payload.metadata}})
            for chunk in chunks
        ]
        return index_chunks(chunks, source=payload.source, replace_source=payload.replace_source)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"텍스트 색인 실패: {error}") from error


@rag_router.post("/pdf", response_model=RagIndexResult)
async def create_pdf_index(
    pdf: UploadFile = File(...),
    title: str = Form("PDF 문서"),
    replace_source: bool = Form(True),
) -> RagIndexResult:
    filename = pdf.filename or "document.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=422, detail=".pdf 파일만 업로드할 수 있습니다.")
    content = await pdf.read()
    maximum = settings.max_pdf_size_mb * 1024 * 1024
    if not content or len(content) > maximum:
        raise HTTPException(status_code=422, detail=f"PDF는 1 byte 이상 {settings.max_pdf_size_mb}MB 이하여야 합니다.")
    try:
        source = f"{filename}:{sha256(content).hexdigest()[:16]}"
        chunks = pdf_to_chunks(content, source=source, title=title)
        return index_chunks(chunks, source=source, replace_source=replace_source)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"PDF 색인 실패: {error}") from error


@rag_router.post("/agent", response_model=RagAgentResult)
def rag_agent(payload: RagAgentRequest) -> RagAgentResult:
    try:
        decision = ToolSelectionResult.model_validate(asdict(select_tool(
            payload.provider,
            payload.query,
            tool_names=["search_knowledge_base"],
            mock_arguments={
                "query": payload.query,
                "mode": payload.mode,
                "top_k": payload.top_k,
                "score_threshold": payload.score_threshold,
                "metadata_filter": payload.metadata_filter,
            },
        )))
        trace = [{"stage": "1_tool_selection", "data": decision.model_dump(mode="json")}]
        tool_call = (
            {"name": decision.tool_name, "arguments": decision.arguments}
            if decision.tool_name else None
        )
        if decision.needs_clarification:
            return RagAgentResult(
                question=payload.query, provider=payload.provider, decision=decision,
                tool_call=tool_call, tool_result=[], final_answer=decision.follow_up_question,
                termination_reason="clarification_required", trace=trace,
            )
        if decision.tool_name is None:
            return RagAgentResult(
                question=payload.query, provider=payload.provider, decision=decision,
                tool_result=[], final_answer="검색 Tool이 선택되지 않아 정책 답변을 생성하지 않았습니다.",
                termination_reason="tool_not_selected", trace=trace,
            )

        execution = execute_tool_safely(decision.tool_name, decision.arguments)
        trace.append({"stage": "2_tool_execution", "data": execution.model_dump(mode="json")})
        if not execution.success:
            return RagAgentResult(
                question=payload.query, provider=payload.provider, decision=decision,
                tool_call=tool_call, execution=execution, tool_result=[],
                final_answer="검색 Tool을 안전하게 실행하지 못했습니다.",
                termination_reason="tool_error", trace=trace,
            )

        results = [RagSearchItem.model_validate(item) for item in execution.data["results"]]
        sources = sorted({item.source for item in results})
        if not results:
            final_answer = "등록된 지식 문서에서 근거를 찾지 못했습니다."
            termination_reason = "no_evidence"
        elif payload.provider == "mock":
            final_answer = f"{results[0].content} (출처: {results[0].source})"
            termination_reason = "grounded_answer"
        else:
            context = "\n".join(f"[{item.source}] {item.content}" for item in results)
            final_answer = str(generate(
                payload.provider,
                "Tool Result만 근거로 한국어로 답하고 출처를 표시하세요.",
                f"질문: {payload.query}\n\nTool Result:\n{context}",
            ).content)
            termination_reason = "grounded_answer"
        trace.append({"stage": "3_final_answer", "data": {"termination_reason": termination_reason}})
        return RagAgentResult(
            question=payload.query, provider=payload.provider, decision=decision,
            tool_call=tool_call, execution=execution, tool_result=results,
            final_answer=final_answer, sources=sources,
            termination_reason=termination_reason, trace=trace,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"RAG Agent 실행 실패: {error}") from error


@rag_router.get("/status")
def status() -> dict:
    result = {
        "ollama": {"ok": False, "url": settings.ollama_base_url},
        "postgres": {"ok": False},
        "redis": {"ok": False, "url": settings.redis_url},
        "embedding_model": settings.ollama_embedding_model,
        "collection": settings.rag_collection,
    }
    try:
        response = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=3)
        response.raise_for_status()
        model_names = [item.get("name", "") for item in response.json().get("models", [])]
        embedding_model_available = any(
            name == settings.ollama_embedding_model
            or name.startswith(f"{settings.ollama_embedding_model}:")
            for name in model_names
        )
        result["ollama"].update({
            "ok": True,
            "models": model_names,
            "embedding_model_available": embedding_model_available,
        })
    except Exception as error:
        result["ollama"]["error"] = str(error)
    try:
        with connect() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM documents WHERE collection_name = %s", (settings.rag_collection,))
            result["postgres"] = {"ok": True, "document_count": cursor.fetchone()[0]}
    except Exception as error:
        result["postgres"]["error"] = str(error)
    try:
        result["redis"]["ok"] = redis_cache.ping()
        result["redis"]["cache_ttl_seconds"] = settings.rag_cache_ttl_seconds
    except Exception as error:
        result["redis"]["error"] = str(error)
    return result
