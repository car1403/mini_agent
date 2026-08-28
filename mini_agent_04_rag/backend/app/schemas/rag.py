"""초보자용 RAG API에서 사용하는 데이터 모양입니다."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class ChunkRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10000)
    source: str = "student-document.md"
    title: str = "학생 문서"
    sentences_per_chunk: int = Field(default=2, ge=1, le=10)


class RagChunk(BaseModel):
    chunk_id: str
    text: str
    source: str
    title: str
    chunk_index: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class SearchRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    mode: Literal["keyword", "pgvector", "hybrid"] = "keyword"
    top_k: int = Field(default=3, ge=1, le=10)
    score_threshold: float | None = Field(default=None, ge=-1, le=1)
    metadata_filter: dict[str, Any] = Field(default_factory=dict)


class SearchItem(BaseModel):
    title: str
    content: str
    source: str
    score: float
    chunk_index: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
    keyword_rank: int | None = None
    vector_rank: int | None = None
    matched_by: list[str] = Field(default_factory=list)


class SearchResult(BaseModel):
    question: str
    mode: str
    results: list[SearchItem]


class AnswerRequest(SearchRequest):
    use_ollama: bool = False
    use_cache: bool = False


class AnswerResult(BaseModel):
    answer: str
    grounded: bool
    mode: str
    context: str = ""
    sources: list[str] = Field(default_factory=list)
    results: list[SearchItem] = Field(default_factory=list)
    cache_hit: bool = False
    cache_ttl_seconds: int = 0
    trace: list[dict[str, Any]] = Field(default_factory=list)


class IndexResult(BaseModel):
    collection: str
    indexed_count: int
    embedding_model: str
    source: str | None = None


class TextIndexRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=100000)
    source: str = Field(min_length=1, max_length=200)
    metadata: dict[str, Any] = Field(default_factory=dict)
