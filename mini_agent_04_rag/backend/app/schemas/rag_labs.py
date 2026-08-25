"""RAG Lab 03~05의 신뢰 경계에서 사용하는 API 계약입니다."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.rag import RagIndexResult, RagSearchItem


class ProductSearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=2, max_length=500)
    category: Literal["shoes", "bag"] | None = None
    max_price: int | None = Field(default=None, ge=0, le=10_000_000)
    top_k: int = Field(default=3, ge=1, le=10)


class ProductSearchResult(BaseModel):
    query: str
    category: str | None
    max_price: int | None
    results: list[RagSearchItem]
    candidate_count: int


class AclSearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=2, max_length=500)
    top_k: int = Field(default=3, ge=1, le=5)


class AclSearchResult(BaseModel):
    role: Literal["employee", "manager", "hr"]
    results: list[RagSearchItem]
    termination_reason: Literal["authorized_evidence", "no_authorized_evidence"]


class RetrievalEvaluationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    top_k: int = Field(default=3, ge=1, le=4)


class RetrievalEvaluationCase(BaseModel):
    question: str
    expected_id: str
    ranked_ids: list[str]
    rank: int | None


class RetrievalEvaluationReport(BaseModel):
    mode: Literal["keyword", "pgvector", "hybrid"]
    top_k: int
    hit_at_k: float
    mrr: float
    cases: list[RetrievalEvaluationCase]


class RetrievalEvaluationResult(BaseModel):
    reports: list[RetrievalEvaluationReport]


class TopicSearchArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=2, max_length=500)
    top_k: int = Field(default=2, ge=1, le=3)


class MultiToolRagRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=1000)
    provider: Literal["mock", "ollama", "openai", "gemini"] = "mock"


class MultiToolRagResult(BaseModel):
    status: Literal["needs_clarification", "completed", "stopped"]
    final_answer: str
    topics: list[Literal["hotel", "flight", "attraction"]] = Field(default_factory=list)
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    tool_results: dict[str, list[RagSearchItem]] = Field(default_factory=dict)
    step_count: int
    max_steps: int
    termination_reason: Literal[
        "clarification_required", "grounded_answer", "no_evidence",
        "max_steps_exceeded", "tool_error",
    ]
    trace: list[dict[str, Any]] = Field(default_factory=list)
