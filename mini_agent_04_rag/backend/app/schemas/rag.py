"""RAG 과정의 Pydantic API 계약입니다."""

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.common import MessageRequest, ProviderName
from app.schemas.stage_03 import ToolSelectionResult, ToolRunResult

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
    metadata: dict[str, Any] = Field(default_factory=dict)


class RagSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    mode: Literal["keyword", "pgvector", "hybrid"] = "keyword"
    top_k: int = Field(default=3, ge=1, le=10)
    score_threshold: float | None = Field(default=None, ge=-1, le=1)
    metadata_filter: dict[str, Any] = Field(default_factory=dict)


class RagSearchItem(BaseModel):
    title: str
    content: str
    source: str
    score: float
    chunk_index: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
    keyword_rank: int | None = None
    vector_rank: int | None = None
    matched_by: list[str] = Field(default_factory=list)


class RagSearchResult(BaseModel):
    query: str
    mode: Literal["keyword", "pgvector", "hybrid"]
    results: list[RagSearchItem]


class RagAnswerRequest(RagSearchRequest):
    provider: ProviderName = "mock"
    use_cache: bool = True


class RagAnswerResult(BaseModel):
    answer: str
    grounded: bool
    provider: ProviderName
    search_mode: Literal["keyword", "pgvector", "hybrid"]
    context: str = ""
    sources: list[str] = Field(default_factory=list)
    results: list[RagSearchItem] = Field(default_factory=list)
    cache_hit: bool = False
    cache_ttl_seconds: int = 0
    trace: list[dict[str, Any]] = Field(default_factory=list)


class RagIndexRequest(BaseModel):
    reset_collection: bool = True


class RagIndexResult(BaseModel):
    collection: str
    indexed_count: int
    embedding_model: str
    source: str | None = None
    source: str | None = None


class RagTextIndexRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=100000)
    source: str = Field(min_length=1, max_length=200)
    metadata: dict[str, Any] = Field(default_factory=dict)
    sentences_per_chunk: int = Field(default=2, ge=1, le=20)
    replace_source: bool = True


class RagAgentRequest(RagSearchRequest):
    provider: ProviderName = "mock"


class RagAgentResult(BaseModel):
    question: str
    provider: ProviderName
    decision: ToolSelectionResult
    tool_call: dict[str, Any] | None = None
    execution: ToolRunResult | None = None
    tool_result: list[RagSearchItem]
    final_answer: str
    sources: list[str] = Field(default_factory=list)
    termination_reason: Literal[
        "grounded_answer", "no_evidence", "tool_not_selected",
        "clarification_required", "tool_error",
    ]
    trace: list[dict[str, Any]] = Field(default_factory=list)


class SearchKnowledgeArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=2, max_length=2000)
    mode: Literal["keyword", "pgvector", "hybrid"] = "hybrid"
    top_k: int = Field(default=3, ge=1, le=10)
    score_threshold: float | None = Field(default=None, ge=-1, le=1)
    metadata_filter: dict[str, Any] = Field(default_factory=dict)
