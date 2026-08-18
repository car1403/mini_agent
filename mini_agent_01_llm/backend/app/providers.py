from dataclasses import dataclass
from time import perf_counter

import httpx

from app.config import settings


@dataclass
class ProviderResult:
    provider: str
    model: str
    content: str
    latency_ms: int


def generate_mock(system_prompt: str, message: str) -> ProviderResult:
    return ProviderResult(
        "mock",
        "deterministic-travel-mock",
        f"[Mock 응답] 질문을 확인했습니다: {message}",
        0,
    )


def generate_openai(system_prompt: str, message: str) -> ProviderResult:
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    started = perf_counter()
    response = client.responses.create(
        model=settings.openai_model,
        instructions=system_prompt,
        input=message,
    )
    return ProviderResult(
        "openai",
        settings.openai_model,
        response.output_text,
        round((perf_counter() - started) * 1000),
    )


def generate_gemini(system_prompt: str, message: str) -> ProviderResult:
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")
    if not settings.gemini_model:
        raise ValueError("GEMINI_MODEL이 설정되지 않았습니다.")
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.gemini_api_key)
    started = perf_counter()
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=message,
        config=types.GenerateContentConfig(system_instruction=system_prompt),
    )
    return ProviderResult(
        "gemini",
        settings.gemini_model,
        response.text or "",
        round((perf_counter() - started) * 1000),
    )


def generate_ollama(system_prompt: str, message: str) -> ProviderResult:
    started = perf_counter()
    response = httpx.post(
        f"{settings.ollama_base_url}/api/chat",
        json={
            "model": settings.ollama_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            "stream": False,
        },
        timeout=settings.request_timeout_seconds,
    )
    response.raise_for_status()
    return ProviderResult(
        "ollama",
        settings.ollama_model,
        response.json()["message"]["content"],
        round((perf_counter() - started) * 1000),
    )


def generate(provider: str, system_prompt: str, message: str) -> ProviderResult:
    handlers = {
        "mock": generate_mock,
        "gemini": generate_gemini,
        "openai": generate_openai,
        "ollama": generate_ollama,
    }
    if provider not in handlers:
        raise ValueError(f"지원하지 않는 Provider입니다: {provider}")
    return handlers[provider](system_prompt, message)


def provider_status() -> list[dict]:
    return [
        {
            "provider": "mock",
            "configured": True,
            "model": "deterministic-travel-mock",
            "environment": "local-python",
        },
        {
            "provider": "gemini",
            "configured": bool(settings.gemini_api_key and settings.gemini_model),
            "model": settings.gemini_model or "(GEMINI_MODEL 미설정)",
            "environment": "cloud",
        },
        {
            "provider": "openai",
            "configured": bool(settings.openai_api_key),
            "model": settings.openai_model,
            "environment": "cloud",
        },
        {
            "provider": "ollama",
            "configured": True,
            "model": settings.ollama_model,
            "base_url": settings.ollama_base_url,
            "environment": "local-docker",
        },
    ]
