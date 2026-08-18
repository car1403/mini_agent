from typing import Literal

from fastapi import APIRouter, HTTPException

from app.memory.conversation import make_window
from app.memory.policy import ALLOWED_MEMORY_KEYS, SENSITIVE_MEMORY_KEYS
from app.memory import redis_store
from app.memory.postgres_store import connect
from app.memory.service import delete_memory, list_memories, personalize, upsert_memory
from app.schemas import (
    ConversationWindowRequest, ConversationWindowResult, MemoryItem,
    MemoryListResult, MemoryPersonalizeRequest, MemoryPersonalizeResult,
    MemorySaveRequest, MemoryStorage, SessionResult, SessionSaveRequest,
)


memory_router = APIRouter(prefix="/api/memory", tags=["Memory"])


@memory_router.get("/types")
def memory_types() -> dict:
    return {
        "types": [
            {"name": "conversation_history", "storage": "memory/postgres", "lifetime": "현재 대화 또는 정책 기간"},
            {"name": "short_term_state", "storage": "redis", "lifetime": "TTL까지"},
            {"name": "long_term_memory", "storage": "postgres", "lifetime": "삭제 요청까지"},
            {"name": "rag_document", "storage": "postgres/pgvector", "lifetime": "문서 갱신까지"},
        ],
        "allowed_keys": sorted(ALLOWED_MEMORY_KEYS),
        "blocked_examples": sorted(SENSITIVE_MEMORY_KEYS),
    }


@memory_router.post("/conversation-window", response_model=ConversationWindowResult)
def conversation_window(payload: ConversationWindowRequest) -> ConversationWindowResult:
    return make_window(payload.messages, payload.max_recent_messages)


@memory_router.post("/items", response_model=MemoryItem)
def save_memory(payload: MemorySaveRequest) -> MemoryItem:
    try:
        return upsert_memory(payload.storage, payload.user_id, payload.key, payload.value)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Memory 저장 실패: {error}") from error


@memory_router.get("/items/{user_id}", response_model=MemoryListResult)
def get_memories(user_id: str, storage: MemoryStorage = "mock") -> MemoryListResult:
    try:
        return MemoryListResult(user_id=user_id, storage=storage, items=list_memories(storage, user_id))
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Memory 조회 실패: {error}") from error


@memory_router.delete("/items/{user_id}/{memory_id}")
def remove_memory(user_id: str, memory_id: str, storage: MemoryStorage = "mock") -> dict:
    try:
        return {"deleted": delete_memory(storage, user_id, memory_id)}
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Memory 삭제 실패: {error}") from error


@memory_router.post("/personalize", response_model=MemoryPersonalizeResult)
def create_personalized_answer(payload: MemoryPersonalizeRequest) -> MemoryPersonalizeResult:
    try:
        return personalize(
            storage=payload.storage,
            user_id=payload.user_id,
            question=payload.question,
            provider=payload.provider,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"개인화 답변 실패: {error}") from error


@memory_router.post("/sessions", response_model=SessionResult)
def save_session(payload: SessionSaveRequest) -> SessionResult:
    try:
        ttl = redis_store.save(payload.session_id, payload.state)
        return SessionResult(session_id=payload.session_id, state=payload.state, ttl_seconds=ttl)
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Redis 저장 실패: {error}") from error


@memory_router.get("/sessions/{session_id}", response_model=SessionResult)
def get_session(session_id: str) -> SessionResult:
    try:
        state, ttl = redis_store.get(session_id)
        return SessionResult(session_id=session_id, state=state, ttl_seconds=ttl)
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Redis 조회 실패: {error}") from error


@memory_router.delete("/sessions/{session_id}")
def remove_session(session_id: str) -> dict:
    try:
        return {"deleted": redis_store.delete(session_id)}
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Redis 삭제 실패: {error}") from error


@memory_router.get("/status")
def status() -> dict:
    result = {"redis": {"ok": False}, "postgres": {"ok": False}}
    try:
        result["redis"]["ok"] = redis_store.ping()
    except Exception as error:
        result["redis"]["error"] = str(error)
    try:
        with connect() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM user_memories")
            result["postgres"] = {"ok": True, "memory_count": cursor.fetchone()[0]}
    except Exception as error:
        result["postgres"]["error"] = str(error)
    return result
