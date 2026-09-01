from app.core.config import settings
from app.services.generation_service import generate
from app.rag.documents import TRAVEL_DOCUMENTS
from app.rag.embedding import embed
from app.rag.keyword_store import all_chunks, keyword_search
from app.rag.pgvector_store import add_chunk, reset_collection, vector_search
from app.schemas import RagAnswerResult, RagIndexResult, RagSearchItem


def search(query: str, mode: str, top_k: int) -> list[RagSearchItem]:
    if mode == "keyword":
        return keyword_search(query, top_k)
    return vector_search(embed(query), top_k)


def index_documents(reset: bool = True) -> RagIndexResult:
    if reset:
        reset_collection()
    chunks = all_chunks()
    for chunk in chunks:
        add_chunk(chunk, embed(chunk.text))
    return RagIndexResult(
        collection=settings.rag_collection,
        indexed_count=len(chunks),
        embedding_model=settings.ollama_embedding_model,
    )


def answer(query: str, mode: str, top_k: int, provider: str) -> RagAnswerResult:
    results = search(query, mode, top_k)
    if not results:
        return RagAnswerResult(
            answer="제공된 여행 정책 문서에서 근거를 찾지 못했습니다.",
            grounded=False,
            provider=provider,
            search_mode=mode,
        )

    context = "\n".join(
        f"[{item.source}] {item.content}" for item in results
    )
    sources = sorted({item.source for item in results})
    prompt = f"질문: {query}\n\nContext:\n{context}"
    system_prompt = (
        "Context에 있는 내용만 사용해 한국어로 답하세요. "
        "Context에 근거가 없으면 모른다고 답하세요."
    )
    answer_text = str(generate(provider, system_prompt, prompt).content)

    return RagAnswerResult(
        answer=answer_text,
        grounded=True,
        provider=provider,
        search_mode=mode,
        context=context,
        sources=sources,
        results=results,
    )
