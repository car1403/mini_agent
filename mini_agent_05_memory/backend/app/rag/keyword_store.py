import re

from app.rag.chunking import split_document
from app.rag.documents import TRAVEL_DOCUMENTS
from app.schemas import RagSearchItem


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[가-힣A-Za-z0-9]+", text.lower()))


def all_chunks():
    return [
        chunk
        for document in TRAVEL_DOCUMENTS
        for chunk in split_document(
            document["content"],
            source=document["source"],
            title=document["title"],
            sentences_per_chunk=1,
        )
    ]


def keyword_search(query: str, top_k: int = 3) -> list[RagSearchItem]:
    query_tokens = tokenize(query)
    results = []
    for chunk in all_chunks():
        common = query_tokens & tokenize(f"{chunk.title} {chunk.text}")
        score = len(common) / max(len(query_tokens), 1)
        if score > 0:
            results.append(
                RagSearchItem(
                    title=chunk.title,
                    content=chunk.text,
                    source=chunk.source,
                    score=round(score, 3),
                    chunk_index=chunk.chunk_index,
                )
            )
    return sorted(results, key=lambda item: item.score, reverse=True)[:top_k]
