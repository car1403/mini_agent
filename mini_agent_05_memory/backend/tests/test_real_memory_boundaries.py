import pytest

from app.core.config import settings
from app.memory import service
from app.schemas import MemoryPersonalizeRequest, MemorySaveRequest, ProviderCompareRequest


def test_defaults_use_real_provider_and_postgres() -> None:
    assert settings.llm_provider in {"openai", "gemini", "ollama"}
    assert MemorySaveRequest(user_id="user-1", key="transportation", value="대중교통").storage == "postgres"
    request = MemoryPersonalizeRequest(user_id="user-1", question="이동 방법을 추천해 줘")
    assert request.storage == "postgres"
    assert request.provider in {"openai", "gemini", "ollama"}
    assert ProviderCompareRequest(message="안녕").providers == ["openai"]


def test_memory_service_delegates_to_postgres(monkeypatch) -> None:
    calls = []
    monkeypatch.setattr(
        service.postgres_store,
        "upsert",
        lambda user_id, key, value: calls.append((user_id, key, value)) or {"saved": True},
    )
    output = service.upsert_memory("postgres", "user-1", "transportation", "대중교통")
    assert output == {"saved": True}
    assert calls == [("user-1", "transportation", "대중교통")]


def test_unknown_provider_is_rejected() -> None:
    from app.providers.registry import get_provider

    with pytest.raises(ValueError, match="지원하지 않는 Provider"):
        get_provider("unknown")
