"""Provider 구현의 생성과 조회를 한곳에서 관리하는 레지스트리입니다.

services와 agents는 구현 클래스를 직접 import하지 않고 `get_provider()`를 사용합니다.
"""

from app.providers.base import LLMProvider
from app.providers.gemini import GeminiProvider
from app.providers.mock import MockProvider
from app.providers.ollama import OllamaProvider
from app.providers.openai import OpenAIProvider


_PROVIDERS: dict[str, LLMProvider] = {
    "mock": MockProvider(),
    "gemini": GeminiProvider(),
    "openai": OpenAIProvider(),
    "ollama": OllamaProvider(),
}


def get_provider(name: str) -> LLMProvider:
    try:
        return _PROVIDERS[name]
    except KeyError as error:
        raise ValueError(f"지원하지 않는 Provider입니다: {name}") from error


def provider_status() -> list[dict]:
    return [provider.status() for provider in _PROVIDERS.values()]
