"""Provider 구현의 생성과 상태 조회를 관리하는 경량 레지스트리입니다."""

from app.providers.base import LLMProvider
from app.providers.gemini import GeminiProvider
from app.providers.ollama import OllamaProvider
from app.providers.openai import OpenAIProvider

_PROVIDERS: dict[str, LLMProvider] = {
    "gemini": GeminiProvider(),
    "openai": OpenAIProvider(),
    "ollama": OllamaProvider(),
}

def get_provider(name:str)->LLMProvider:
    try: return _PROVIDERS[name]
    except KeyError as error: raise ValueError(f"지원하지 않는 Provider입니다: {name}") from error

def provider_status()->list[dict]: return [provider.status() for provider in _PROVIDERS.values()]
