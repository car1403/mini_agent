"""MEMORY 과정의 Pydantic API 계약입니다."""

from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.common import ProviderName


MemoryStorage = Literal["postgres"]


class ConversationMessage(BaseModel):
    role: Literal["user", "assistant", "tool"]
    content: str = Field(min_length=1, max_length=4000)


class ConversationWindowRequest(BaseModel):
    messages: list[ConversationMessage] = Field(default_factory=list, max_length=100)
    max_recent_messages: int = Field(default=4, ge=1, le=20)


class ConversationWindowResult(BaseModel):
    total_count: int
    older_summary: str
    recent_messages: list[ConversationMessage]


class MemorySaveRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=100)
    key: str = Field(min_length=1, max_length=100)
    value: str = Field(min_length=1, max_length=1000)
    storage: MemoryStorage = "postgres"


class MemoryItem(BaseModel):
    id: str
    user_id: str
    key: str
    value: str


class MemoryListResult(BaseModel):
    user_id: str
    storage: MemoryStorage
    items: list[MemoryItem]


class MemoryPersonalizeRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=100)
    question: str = Field(min_length=1, max_length=2000)
    storage: MemoryStorage = "postgres"
    provider: ProviderName = "openai"


class MemoryPersonalizeResult(BaseModel):
    user_id: str
    question: str
    used_memories: list[MemoryItem]
    answer: str
    provider: ProviderName
    trace: list[dict[str, Any]] = Field(default_factory=list)


class SessionSaveRequest(BaseModel):
    user_id: str = Field(default="demo-user", min_length=1, max_length=100)
    session_id: str = Field(min_length=1, max_length=100)
    state: dict[str, Any]


class SessionResult(BaseModel):
    user_id: str = "demo-user"
    session_id: str
    state: dict[str, Any] | None = None
    ttl_seconds: int | None = None


class SessionPatchRequest(BaseModel):
    user_id: str = Field(default="demo-user", min_length=1, max_length=100)
    session_id: str = Field(min_length=1, max_length=100)
    changes: dict[str, Any]
    expected_version: int = Field(ge=0)


class ConversationSaveRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=100)
    session_id: str = Field(min_length=1, max_length=100)
    role: Literal["user", "assistant", "tool"]
    content: str = Field(min_length=1, max_length=4000)


class ConversationHistoryResult(BaseModel):
    user_id: str
    session_id: str
    messages: list[ConversationMessage]


class HybridRestoreResult(BaseModel):
    user_id: str
    session_id: str
    session_state: dict[str, Any] | None = None
    session_ttl_seconds: int | None = None
    long_term_memories: list[MemoryItem] = Field(default_factory=list)
    recent_messages: list[ConversationMessage] = Field(default_factory=list)
    trace: list[dict[str, Any]] = Field(default_factory=list)
