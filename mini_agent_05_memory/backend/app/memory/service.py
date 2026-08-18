from app.providers import generate
from app.memory import postgres_store
from app.memory.mock_store import mock_memory_store
from app.memory.relevance import relevant_memories
from app.schemas import MemoryItem, MemoryPersonalizeResult


def upsert_memory(storage: str, user_id: str, key: str, value: str) -> MemoryItem:
    if storage == "mock":
        return mock_memory_store.upsert(user_id, key, value)
    return postgres_store.upsert(user_id, key, value)


def list_memories(storage: str, user_id: str) -> list[MemoryItem]:
    if storage == "mock":
        return mock_memory_store.list(user_id)
    return postgres_store.list_for_user(user_id)


def delete_memory(storage: str, user_id: str, memory_id: str) -> bool:
    if storage == "mock":
        return mock_memory_store.delete(user_id, memory_id)
    return postgres_store.delete(user_id, memory_id)


def personalize(
    *,
    storage: str,
    user_id: str,
    question: str,
    provider: str,
) -> MemoryPersonalizeResult:
    selected = relevant_memories(list_memories(storage, user_id), question)
    if not selected:
        return MemoryPersonalizeResult(
            user_id=user_id,
            question=question,
            used_memories=[],
            answer="이 질문에 사용할 사용자 Memory가 없습니다.",
            provider=provider,
        )

    memory_text = "\n".join(f"- {item.key}: {item.value}" for item in selected)
    if provider == "mock":
        answer = f"다음 사용자 선호를 반영합니다.\n{memory_text}\n질문: {question}"
    else:
        prompt = f"사용자 질문: {question}\n\n관련 Memory:\n{memory_text}"
        system_prompt = (
            "제공된 Memory 중 질문에 관련된 내용만 사용해 한국어로 답하세요. "
            "민감정보를 추측하거나 새 Memory를 만들지 마세요."
        )
        answer = str(generate(provider, system_prompt, prompt).content)

    return MemoryPersonalizeResult(
        user_id=user_id,
        question=question,
        used_memories=selected,
        answer=answer,
        provider=provider,
    )
