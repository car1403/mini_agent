"""요청 Body가 아닌 인증 Header에서 사용자 범위를 얻는 Memory API입니다."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.core.auth import get_authenticated_user_id
from app.memory import postgres_store
from app.memory.service import delete_memory, list_memories, personalize, upsert_memory
from app.schemas import MemoryItem, MemoryListResult, MemoryPersonalizeResult, MemoryStorage, ProviderName


authenticated_memory_router = APIRouter(
    prefix="/api/memory/me",
    tags=["05 · Memory"],
)
AuthenticatedUserId = Annotated[str, Depends(get_authenticated_user_id)]


class AuthenticatedMemorySaveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(min_length=1, max_length=100)
    value: str = Field(min_length=1, max_length=1000)
    storage: MemoryStorage = "postgres"


class AuthenticatedPersonalizeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1, max_length=2000)
    storage: MemoryStorage = "postgres"
    provider: ProviderName = "openai"


@authenticated_memory_router.post("/items", response_model=MemoryItem)
def save_my_memory(
    payload: AuthenticatedMemorySaveRequest,
    user_id: AuthenticatedUserId,
) -> MemoryItem:
    try:
        return upsert_memory(payload.storage, user_id, payload.key, payload.value)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Memory 저장 실패: {error}") from error


@authenticated_memory_router.get("/items", response_model=MemoryListResult)
def get_my_memories(
    user_id: AuthenticatedUserId,
    storage: MemoryStorage = "postgres",
) -> MemoryListResult:
    try:
        return MemoryListResult(
            user_id=user_id,
            storage=storage,
            items=list_memories(storage, user_id),
        )
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Memory 조회 실패: {error}") from error


@authenticated_memory_router.delete("/items/{memory_id}")
def delete_my_memory(
    memory_id: str,
    user_id: AuthenticatedUserId,
    storage: MemoryStorage = "postgres",
) -> dict:
    try:
        return {"user_id": user_id, "deleted": delete_memory(storage, user_id, memory_id)}
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Memory 삭제 실패: {error}") from error


@authenticated_memory_router.post("/personalize", response_model=MemoryPersonalizeResult)
def personalize_for_me(
    payload: AuthenticatedPersonalizeRequest,
    user_id: AuthenticatedUserId,
) -> MemoryPersonalizeResult:
    try:
        return personalize(
            storage=payload.storage,
            user_id=user_id,
            question=payload.question,
            provider=payload.provider,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"개인화 답변 실패: {error}") from error


@authenticated_memory_router.get("/export")
def export_my_memory(
    user_id: AuthenticatedUserId,
    storage: MemoryStorage = "postgres",
) -> dict:
    try:
        return {
            "user_id": user_id,
            "memories": [item.model_dump() for item in list_memories(storage, user_id)],
        }
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Memory 내보내기 실패: {error}") from error


@authenticated_memory_router.delete("")
def delete_all_my_memories(
    user_id: AuthenticatedUserId,
    storage: MemoryStorage = "postgres",
) -> dict:
    try:
        deleted = postgres_store.delete_all_for_user(user_id)
        return {"user_id": user_id, "deleted_memories": deleted}
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Memory 전체 삭제 실패: {error}") from error
