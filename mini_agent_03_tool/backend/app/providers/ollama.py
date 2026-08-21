"""Ollama HTTP API를 공통 Provider 계약으로 변환하는 어댑터입니다.

`providers.registry`가 생성하며 Stage 01·02의 generation/structured services가 사용합니다.
"""

from time import perf_counter
from typing import Any

from pydantic import BaseModel

from app.core.config import settings
from app.providers.models import ProviderResult


class OllamaProvider:
    name = "ollama"

    def _chat(self, system_prompt: str, message: str, format_: dict | None = None) -> dict:
        import httpx

        payload: dict[str, Any] = {"model": settings.ollama_model, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": message}], "stream": False}
        if format_ is not None:
            payload["format"] = format_
        response = httpx.post(f"{settings.ollama_base_url}/api/chat", json=payload, timeout=settings.request_timeout_seconds)
        response.raise_for_status()
        return response.json()

    def generate(self, system_prompt: str, message: str) -> ProviderResult:
        started = perf_counter()
        body = self._chat(system_prompt, message)
        return ProviderResult(self.name, settings.ollama_model, body["message"]["content"], round((perf_counter() - started) * 1000))

    def generate_structured(self, system_prompt: str, message: str, response_schema: type[BaseModel]) -> ProviderResult:
        started = perf_counter()
        body = self._chat(system_prompt, message, response_schema.model_json_schema())
        parsed = response_schema.model_validate_json(body["message"]["content"])
        return ProviderResult(self.name, settings.ollama_model, parsed.model_dump(), round((perf_counter() - started) * 1000))

    def status(self) -> dict[str, Any]:
        return {"provider": self.name, "configured": True, "model": settings.ollama_model, "base_url": settings.ollama_base_url, "environment": "local-docker"}
