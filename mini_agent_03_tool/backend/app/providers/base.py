"""모든 LLM Provider가 따라야 하는 공통 어댑터 계약입니다.

`providers.registry.get_provider()`가 이 계약을 만족하는 구현을 services와 agents에 제공합니다.
"""

from typing import Any, Protocol

from pydantic import BaseModel

from app.providers.models import ProviderResult


class LLMProvider(Protocol):
    name: str

    def generate(self, system_prompt: str, message: str) -> ProviderResult: ...

    def generate_structured(
        self, system_prompt: str, message: str, response_schema: type[BaseModel]
    ) -> ProviderResult: ...

    def status(self) -> dict[str, Any]: ...
