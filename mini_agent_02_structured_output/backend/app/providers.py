from dataclasses import dataclass
from time import perf_counter
from typing import Any

from app.config import settings
from app.schemas import StructuredSchemaName, SupportTicket, TravelPlan


@dataclass
class ProviderResult:
    provider: str
    model: str
    content: str | dict[str, Any]
    latency_ms: int


def generate_mock(system_prompt: str, message: str) -> ProviderResult:
    return ProviderResult(
        "mock", "deterministic-travel-mock", f"[Mock 응답] 질문을 확인했습니다: {message}", 0
    )


def get_structured_model(
    schema_type: StructuredSchemaName,
) -> type[TravelPlan] | type[SupportTicket]:
    return {"travel_plan": TravelPlan, "support_ticket": SupportTicket}[schema_type]


def generate_structured_mock(
    system_prompt: str, message: str, schema_type: StructuredSchemaName
) -> ProviderResult:
    if schema_type == "support_ticket":
        category = (
            "billing"
            if any(word in message for word in ("결제", "환불", "청구"))
            else "technical"
        )
        ticket = SupportTicket(
            category=category,
            priority="medium",
            summary="담당 팀의 확인이 필요한 고객 문의입니다.",
            requires_human=True,
            missing_information=(
                ["주문 번호"] if category == "billing" else ["오류 발생 시각"]
            ),
        )
        return ProviderResult(
            "mock", "deterministic-support-mock", ticket.model_dump(), 0
        )
    destination = next(
        (city for city in ("서울", "부산", "제주", "강릉") if city in message),
        "부산",
    )
    plan = TravelPlan(
        destination=destination,
        summary=f"{destination}의 대표 장소를 둘러보는 교육용 일정입니다.",
        recommended_days=3,
        activities=["지역 명소 방문", "현지 음식 체험"],
        cautions=["실제 예약 전 가격과 운영 시간을 확인하세요."],
    )
    return ProviderResult("mock", "deterministic-travel-mock", plan.model_dump(), 0)


def generate_openai(system_prompt: str, message: str) -> ProviderResult:
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    started = perf_counter()
    response = client.responses.create(
        model=settings.openai_model, instructions=system_prompt, input=message
    )
    return ProviderResult(
        "openai", settings.openai_model, response.output_text,
        round((perf_counter() - started) * 1000),
    )


def generate_structured_openai(
    system_prompt: str, message: str, schema_type: StructuredSchemaName
) -> ProviderResult:
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    started = perf_counter()
    response = client.responses.parse(
        model=settings.openai_model,
        instructions=system_prompt,
        input=message,
        text_format=get_structured_model(schema_type),
    )
    parsed = response.output_parsed
    if parsed is None:
        raise RuntimeError("OpenAI가 구조화된 결과를 반환하지 않았습니다.")
    return ProviderResult(
        "openai", settings.openai_model, parsed.model_dump(),
        round((perf_counter() - started) * 1000),
    )


def generate_gemini(system_prompt: str, message: str) -> ProviderResult:
    client, types = _gemini_client()
    started = perf_counter()
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=message,
        config=types.GenerateContentConfig(system_instruction=system_prompt),
    )
    return ProviderResult(
        "gemini", settings.gemini_model, response.text or "",
        round((perf_counter() - started) * 1000),
    )


def generate_structured_gemini(
    system_prompt: str, message: str, schema_type: StructuredSchemaName
) -> ProviderResult:
    client, types = _gemini_client()
    started = perf_counter()
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=message,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            response_schema=get_structured_model(schema_type),
        ),
    )
    parsed = get_structured_model(schema_type).model_validate_json(response.text or "{}")
    return ProviderResult(
        "gemini", settings.gemini_model, parsed.model_dump(),
        round((perf_counter() - started) * 1000),
    )


def _gemini_client() -> tuple[Any, Any]:
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")
    if not settings.gemini_model:
        raise ValueError("GEMINI_MODEL이 설정되지 않았습니다.")
    from google import genai
    from google.genai import types

    return genai.Client(api_key=settings.gemini_api_key), types


def _ollama_chat(system_prompt: str, message: str, format_: dict | None = None) -> dict:
    import httpx

    payload: dict[str, Any] = {
        "model": settings.ollama_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ],
        "stream": False,
    }
    if format_ is not None:
        payload["format"] = format_
    response = httpx.post(
        f"{settings.ollama_base_url}/api/chat",
        json=payload,
        timeout=settings.request_timeout_seconds,
    )
    response.raise_for_status()
    return response.json()


def generate_ollama(system_prompt: str, message: str) -> ProviderResult:
    started = perf_counter()
    body = _ollama_chat(system_prompt, message)
    return ProviderResult(
        "ollama", settings.ollama_model, body["message"]["content"],
        round((perf_counter() - started) * 1000),
    )


def generate_structured_ollama(
    system_prompt: str, message: str, schema_type: StructuredSchemaName
) -> ProviderResult:
    started = perf_counter()
    model_class = get_structured_model(schema_type)
    body = _ollama_chat(system_prompt, message, model_class.model_json_schema())
    parsed = model_class.model_validate_json(body["message"]["content"])
    return ProviderResult(
        "ollama", settings.ollama_model, parsed.model_dump(),
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


def generate_structured(
    provider: str,
    system_prompt: str,
    message: str,
    schema_type: StructuredSchemaName = "travel_plan",
) -> ProviderResult:
    handlers = {
        "mock": generate_structured_mock,
        "gemini": generate_structured_gemini,
        "openai": generate_structured_openai,
        "ollama": generate_structured_ollama,
    }
    if provider not in handlers:
        raise ValueError(f"지원하지 않는 Provider입니다: {provider}")
    return handlers[provider](system_prompt, message, schema_type)


def provider_status() -> list[dict]:
    return [
        {"provider": "mock", "configured": True, "model": "deterministic-structured-mock", "environment": "local-python"},
        {"provider": "gemini", "configured": bool(settings.gemini_api_key and settings.gemini_model), "model": settings.gemini_model or "(GEMINI_MODEL 미설정)", "environment": "cloud"},
        {"provider": "openai", "configured": bool(settings.openai_api_key), "model": settings.openai_model, "environment": "cloud"},
        {"provider": "ollama", "configured": True, "model": settings.ollama_model, "base_url": settings.ollama_base_url, "environment": "local-docker"},
    ]
