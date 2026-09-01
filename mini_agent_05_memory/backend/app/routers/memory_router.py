from typing import Literal

from fastapi import APIRouter, HTTPException

from app.memory.conversation import make_window
from app.memory.policy import ALLOWED_MEMORY_KEYS, SENSITIVE_MEMORY_KEYS
from app.memory import conversation_store, postgres_store, redis_store
from app.memory.postgres_store import connect
from app.memory.service import delete_memory, list_memories, personalize, upsert_memory
from app.schemas import (
    ConversationWindowRequest, ConversationWindowResult, MemoryItem,
    MemoryListResult, MemoryPersonalizeRequest, MemoryPersonalizeResult,
    ConversationHistoryResult, ConversationSaveRequest, HybridRestoreResult,
    MemorySaveRequest, MemoryStorage, SessionPatchRequest, SessionResult, SessionSaveRequest,
)


memory_router = APIRouter(prefix="/api/memory", tags=["05 · Memory"])


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
def get_memories(user_id: str, storage: MemoryStorage = "postgres") -> MemoryListResult:
    try:
        return MemoryListResult(user_id=user_id, storage=storage, items=list_memories(storage, user_id))
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Memory 조회 실패: {error}") from error


@memory_router.delete("/items/{user_id}/{memory_id}")
def remove_memory(user_id: str, memory_id: str, storage: MemoryStorage = "postgres") -> dict:
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
        # 클라이언트가 보낸 version을 신뢰하지 않고 새 Session은 항상 0에서 시작합니다.
        state = {**payload.state, "version": 0}
        ttl = redis_store.save(payload.user_id, payload.session_id, state)
        return SessionResult(user_id=payload.user_id, session_id=payload.session_id, state=state, ttl_seconds=ttl)
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Redis 저장 실패: {error}") from error


@memory_router.get("/sessions/{session_id}", response_model=SessionResult)
def get_session(session_id: str, user_id: str = "demo-user", refresh_ttl: bool = False) -> SessionResult:
    try:
        state, ttl = redis_store.get(user_id, session_id, refresh_ttl)
        return SessionResult(user_id=user_id, session_id=session_id, state=state, ttl_seconds=ttl)
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Redis 조회 실패: {error}") from error


@memory_router.delete("/sessions/{session_id}")
def remove_session(session_id: str, user_id: str = "demo-user") -> dict:
    try:
        return {"deleted": redis_store.delete(user_id, session_id)}
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Redis 삭제 실패: {error}") from error


@memory_router.patch("/sessions", response_model=SessionResult)
def patch_session(payload: SessionPatchRequest) -> SessionResult:
    try:
        state, ttl = redis_store.patch(
            payload.user_id, payload.session_id, payload.changes, payload.expected_version,
        )
        return SessionResult(user_id=payload.user_id, session_id=payload.session_id, state=state, ttl_seconds=ttl)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Redis 갱신 실패: {error}") from error


@memory_router.post("/conversations", response_model=ConversationHistoryResult)
def append_conversation(payload: ConversationSaveRequest) -> ConversationHistoryResult:
    try:
        conversation_store.append(payload.user_id, payload.session_id, payload.role, payload.content)
        messages = conversation_store.recent(payload.user_id, payload.session_id, 20)
        return ConversationHistoryResult(user_id=payload.user_id, session_id=payload.session_id, messages=messages)
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"대화 저장 실패: {error}") from error


@memory_router.get("/conversations/{user_id}/{session_id}", response_model=ConversationHistoryResult)
def get_conversation(user_id: str, session_id: str, limit: int = 10) -> ConversationHistoryResult:
    try:
        return ConversationHistoryResult(
            user_id=user_id,
            session_id=session_id,
            messages=conversation_store.recent(user_id, session_id, min(max(limit, 1), 50)),
        )
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"대화 조회 실패: {error}") from error


@memory_router.get("/restore/{user_id}/{session_id}", response_model=HybridRestoreResult)
def restore_memory(user_id: str, session_id: str) -> HybridRestoreResult:
    trace: list[dict] = []
    try:
        state, ttl = redis_store.get(user_id, session_id)
        trace.append({"stage": "redis_session", "data": {"found": state is not None, "ttl": ttl}})
    except Exception as error:
        state, ttl = None, None
        trace.append({"stage": "redis_session", "data": {"error": str(error)}})
    try:
        memories = postgres_store.list_for_user(user_id)
        messages = conversation_store.recent(user_id, session_id, 10)
        trace.append({"stage": "postgres", "data": {"memories": len(memories), "messages": len(messages)}})
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"PostgreSQL 복원 실패: {error}") from error
    return HybridRestoreResult(
        user_id=user_id, session_id=session_id, session_state=state,
        session_ttl_seconds=ttl, long_term_memories=memories,
        recent_messages=messages, trace=trace,
    )


@memory_router.get("/export/{user_id}")
def export_memory(user_id: str) -> dict:
    try:
        return {
            "user_id": user_id,
            "memories": [item.model_dump() for item in postgres_store.list_for_user(user_id)],
        }
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Memory 내보내기 실패: {error}") from error


@memory_router.delete("/users/{user_id}")
def delete_user_memory(user_id: str) -> dict:
    try:
        return {
            "user_id": user_id,
            "deleted_sessions": redis_store.delete_for_user(user_id),
            "deleted_memories": postgres_store.delete_all_for_user(user_id),
            "deleted_messages": conversation_store.delete_for_user(user_id),
        }
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"사용자 Memory 삭제 실패: {error}") from error


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
