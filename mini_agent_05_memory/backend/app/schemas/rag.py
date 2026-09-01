"""RAG 과정의 Pydantic API 계약입니다."""

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.common import MessageRequest, ProviderName

class ChunkPreviewRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10000)
    source: str = Field(default="student-document.md", min_length=1, max_length=200)
    title: str = Field(default="학생 문서", min_length=1, max_length=200)
    sentences_per_chunk: int = Field(default=2, ge=1, le=10)


class RagChunk(BaseModel):
    chunk_id: str
    text: str
    source: str
    title: str
    chunk_index: int


class RagSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    mode: Literal["keyword", "pgvector"] = "keyword"
    top_k: int = Field(default=3, ge=1, le=10)


class RagSearchItem(BaseModel):
    title: str
    content: str
    source: str
    score: float
    chunk_index: int = 0


class RagSearchResult(BaseModel):
    query: str
    mode: Literal["keyword", "pgvector"]
    results: list[RagSearchItem]


class RagAnswerRequest(RagSearchRequest):
    provider: ProviderName = "openai"


class RagAnswerResult(BaseModel):
    answer: str
    grounded: bool
    provider: ProviderName
    search_mode: Literal["keyword", "pgvector"]
    context: str = ""
    sources: list[str] = Field(default_factory=list)
    results: list[RagSearchItem] = Field(default_factory=list)


class RagIndexRequest(BaseModel):
    reset_collection: bool = True


class RagIndexResult(BaseModel):
    collection: str
    indexed_count: int
    embedding_model: str
