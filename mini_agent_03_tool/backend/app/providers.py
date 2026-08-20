import json
from dataclasses import dataclass, field
from datetime import date, timedelta
from time import perf_counter
from typing import Any

from app.config import settings
from app.schemas import TravelPlan
from app.tools.definitions import get_tool_definitions
from app.tools.travel_tools import select_tool as select_mock_tool


@dataclass
class ProviderResult:
    provider: str
    model: str
    content: str | dict[str, Any]
    latency_ms: int


@dataclass
class ToolDecision:
    provider: str
    model: str
    tool_name: str | None
    arguments: dict[str, Any]
    reason: str
    confidence: float
    latency_ms: int
    missing_arguments: list[str] = field(default_factory=list)
    needs_clarification: bool = False
    follow_up_question: str = ""
    raw_tool_call: dict[str, Any] | None = None


def generate_mock(system_prompt: str, message: str) -> ProviderResult:
    return ProviderResult("mock", "deterministic-travel-mock", f"[Mock 응답] 질문을 확인했습니다: {message}", 0)


def generate_structured_mock(system_prompt: str, message: str) -> ProviderResult:
    destination = next((city for city in ("서울", "부산", "제주", "강릉") if city in message), "부산")
    plan = TravelPlan(destination=destination, summary=f"{destination}의 대표 장소를 둘러보는 교육용 일정입니다.", recommended_days=3, activities=["지역 명소 방문", "현지 음식 체험"], cautions=["실제 예약 전 가격과 운영 시간을 확인하세요."])
    return ProviderResult("mock", "deterministic-travel-mock", plan.model_dump(), 0)


def select_tool_mock(
    message: str, tool_choice: str = "auto"
) -> ToolDecision:
    if tool_choice == "none":
        return ToolDecision("mock", "deterministic-travel-mock", None, {}, "Tool 사용 금지", 1.0, 0)
    decision = select_mock_tool(message)
    if tool_choice == "required" and decision["tool_name"] is None:
        decision = {"tool_name": "get_current_weather", "reason": "Tool 사용 필수 모드", "confidence": 0.5}
    today = date.today()
    arguments: dict[str, Any] = {}
    if decision["tool_name"] == "get_current_weather":
        city = _find_city(message)
        arguments = {"city": city} if city else {}
    elif decision["tool_name"] == "get_weather_forecast":
        city = _find_city(message)
        target_date = (today + timedelta(days=1)).isoformat() if "내일" in message else None
        arguments = {key: value for key, value in {"city": city, "target_date": target_date}.items() if value is not None}
    elif decision["tool_name"] == "search_hotels":
        city = _find_city(message)
        arguments = {"city": city} if city else {}
    elif decision["tool_name"] == "search_attractions":
        city = _find_city(message)
        arguments = {"city": city, "category": "all"} if city else {"category": "all"}
    result = ToolDecision("mock", "deterministic-travel-mock", decision["tool_name"], arguments, decision["reason"], decision["confidence"], 0, raw_tool_call={"name": decision["tool_name"], "arguments": arguments} if decision["tool_name"] else None)
    return _add_clarification(result)


def _find_city(message: str) -> str | None:
    return next((city for city in ("서울", "부산", "제주", "강릉") if city in message), None)


def _add_clarification(decision: ToolDecision) -> ToolDecision:
    required = {
        "get_current_weather": ["city"],
        "get_weather_forecast": ["city", "target_date"],
        "search_hotels": ["city", "check_in", "check_out", "guests"],
        "search_attractions": ["city"],
    }
    missing = [name for name in required.get(decision.tool_name or "", []) if name not in decision.arguments]
    decision.missing_arguments = missing
    decision.needs_clarification = bool(missing)
    if missing:
        decision.follow_up_question = f"Tool 실행 전에 다음 정보를 알려주세요: {', '.join(missing)}"
    return decision


def _openai_client():
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
    from openai import OpenAI
    return OpenAI(api_key=settings.openai_api_key)


def generate_openai(system_prompt: str, message: str) -> ProviderResult:
    started = perf_counter()
    response = _openai_client().responses.create(model=settings.openai_model, instructions=system_prompt, input=message)
    return ProviderResult("openai", settings.openai_model, response.output_text, round((perf_counter() - started) * 1000))


def generate_structured_openai(system_prompt: str, message: str) -> ProviderResult:
    started = perf_counter()
    response = _openai_client().responses.parse(model=settings.openai_model, instructions=system_prompt, input=message, text_format=TravelPlan)
    if response.output_parsed is None:
        raise RuntimeError("OpenAI가 구조화된 결과를 반환하지 않았습니다.")
    return ProviderResult("openai", settings.openai_model, response.output_parsed.model_dump(), round((perf_counter() - started) * 1000))


def select_tool_openai(message: str, tool_choice: str = "auto") -> ToolDecision:
    definitions = get_tool_definitions()
    tools = [{"type": "function", "name": tool["name"], "description": tool["description"], "parameters": tool["input_schema"]} for tool in definitions]
    started = perf_counter()
    response = _openai_client().responses.create(model=settings.openai_model, instructions="필요한 경우에만 여행 조회 Tool 하나를 선택하세요.", input=message, tools=tools, tool_choice=tool_choice)
    call = next((item for item in response.output if item.type == "function_call"), None)
    arguments = json.loads(call.arguments) if call else {}
    return _add_clarification(ToolDecision("openai", settings.openai_model, call.name if call else None, arguments, "OpenAI Tool Calling 결과", 0.9 if call else 0.4, round((perf_counter() - started) * 1000), raw_tool_call={"name": call.name, "arguments": call.arguments} if call else None))


def _gemini_client() -> tuple[Any, Any]:
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")
    if not settings.gemini_model:
        raise ValueError("GEMINI_MODEL이 설정되지 않았습니다.")
    from google import genai
    from google.genai import types
    return genai.Client(api_key=settings.gemini_api_key), types


def generate_gemini(system_prompt: str, message: str) -> ProviderResult:
    client, types = _gemini_client()
    started = perf_counter()
    response = client.models.generate_content(model=settings.gemini_model, contents=message, config=types.GenerateContentConfig(system_instruction=system_prompt))
    return ProviderResult("gemini", settings.gemini_model, response.text or "", round((perf_counter() - started) * 1000))


def generate_structured_gemini(system_prompt: str, message: str) -> ProviderResult:
    client, types = _gemini_client()
    started = perf_counter()
    response = client.models.generate_content(model=settings.gemini_model, contents=message, config=types.GenerateContentConfig(system_instruction=system_prompt, response_mime_type="application/json", response_schema=TravelPlan))
    parsed = TravelPlan.model_validate_json(response.text or "{}")
    return ProviderResult("gemini", settings.gemini_model, parsed.model_dump(), round((perf_counter() - started) * 1000))


def select_tool_gemini(message: str, tool_choice: str = "auto") -> ToolDecision:
    client, types = _gemini_client()
    definitions = get_tool_definitions()
    declarations = [types.FunctionDeclaration(name=tool["name"], description=tool["description"], parameters_json_schema=tool["input_schema"]) for tool in definitions]
    started = perf_counter()
    instruction = "반드시 여행 조회 Tool 하나를 선택하세요. " if tool_choice == "required" else ""
    response = client.models.generate_content(model=settings.gemini_model, contents=instruction + message, config=types.GenerateContentConfig(tools=[types.Tool(function_declarations=declarations)]))
    calls = response.function_calls or []
    call = calls[0] if calls else None
    arguments = dict(call.args) if call else {}
    return _add_clarification(ToolDecision("gemini", settings.gemini_model, call.name if call else None, arguments, "Gemini Function Calling 결과", 0.9 if call else 0.4, round((perf_counter() - started) * 1000), raw_tool_call={"name": call.name, "arguments": arguments} if call else None))


def _ollama_chat(system_prompt: str, message: str, format_: dict | None = None, tools: list[dict] | None = None) -> dict:
    import httpx
    payload: dict[str, Any] = {"model": settings.ollama_model, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": message}], "stream": False}
    if format_ is not None:
        payload["format"] = format_
    if tools is not None:
        payload["tools"] = tools
    response = httpx.post(f"{settings.ollama_base_url}/api/chat", json=payload, timeout=settings.request_timeout_seconds)
    response.raise_for_status()
    return response.json()


def generate_ollama(system_prompt: str, message: str) -> ProviderResult:
    started = perf_counter(); body = _ollama_chat(system_prompt, message)
    return ProviderResult("ollama", settings.ollama_model, body["message"]["content"], round((perf_counter() - started) * 1000))


def generate_structured_ollama(system_prompt: str, message: str) -> ProviderResult:
    started = perf_counter(); body = _ollama_chat(system_prompt, message, TravelPlan.model_json_schema())
    parsed = TravelPlan.model_validate_json(body["message"]["content"])
    return ProviderResult("ollama", settings.ollama_model, parsed.model_dump(), round((perf_counter() - started) * 1000))


def select_tool_ollama(message: str, tool_choice: str = "auto") -> ToolDecision:
    definitions = get_tool_definitions()
    tools = [{"type": "function", "function": {"name": tool["name"], "description": tool["description"], "parameters": tool["input_schema"]}} for tool in definitions]
    instruction = "반드시 여행 조회 Tool 하나를 선택하세요." if tool_choice == "required" else "필요한 경우에만 여행 조회 Tool 하나를 선택하세요."
    started = perf_counter(); body = _ollama_chat(instruction, message, tools=tools)
    calls = body.get("message", {}).get("tool_calls", [])
    call = calls[0].get("function", {}) if calls else {}
    arguments = call.get("arguments", {})
    return _add_clarification(ToolDecision("ollama", settings.ollama_model, call.get("name"), arguments, "Ollama Tool Calling 결과", 0.85 if call else 0.4, round((perf_counter() - started) * 1000), raw_tool_call=call or None))


def generate(provider: str, system_prompt: str, message: str) -> ProviderResult:
    handlers = {"mock": generate_mock, "gemini": generate_gemini, "openai": generate_openai, "ollama": generate_ollama}
    if provider not in handlers: raise ValueError(f"지원하지 않는 Provider입니다: {provider}")
    return handlers[provider](system_prompt, message)


def generate_structured(provider: str, system_prompt: str, message: str) -> ProviderResult:
    handlers = {"mock": generate_structured_mock, "gemini": generate_structured_gemini, "openai": generate_structured_openai, "ollama": generate_structured_ollama}
    if provider not in handlers: raise ValueError(f"지원하지 않는 Provider입니다: {provider}")
    return handlers[provider](system_prompt, message)


def select_tool(provider: str, message: str, tool_choice: str = "auto") -> ToolDecision:
    if tool_choice == "none":
        return ToolDecision(provider, "tool-choice-none", None, {}, "Tool 사용 금지", 1.0, 0)
    handlers = {"mock": select_tool_mock, "gemini": select_tool_gemini, "openai": select_tool_openai, "ollama": select_tool_ollama}
    if provider not in handlers: raise ValueError(f"지원하지 않는 Provider입니다: {provider}")
    return handlers[provider](message, tool_choice)


def provider_status() -> list[dict]:
    return [
        {"provider": "mock", "configured": True, "model": "deterministic-travel-mock", "environment": "local-python"},
        {"provider": "gemini", "configured": bool(settings.gemini_api_key and settings.gemini_model), "model": settings.gemini_model or "(GEMINI_MODEL 미설정)", "environment": "cloud"},
        {"provider": "openai", "configured": bool(settings.openai_api_key), "model": settings.openai_model, "environment": "cloud"},
        {"provider": "ollama", "configured": True, "model": settings.ollama_model, "base_url": settings.ollama_base_url, "environment": "local-docker"},
    ]
