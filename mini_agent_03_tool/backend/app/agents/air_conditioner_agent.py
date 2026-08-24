"""Ollama로 에어컨 요청의 현재 온도를 추출하는 Agent입니다."""
from typing import Any
from app.providers.registry import get_provider
from app.schemas.lab import AirConditionerInput

def extract_air_conditioner_request(message: str, explicit_arguments: dict[str, Any] | None = None):
    """온도만 구조화하며 전원 동작은 히스테리시스 Workflow가 결정합니다."""
    response = get_provider("ollama").generate_structured("사용자가 말한 현재 섭씨 온도를 추출하세요. 없으면 null입니다.", message, AirConditionerInput)
    values = dict(response.content); values.update({k: v for k, v in (explicit_arguments or {}).items() if v not in (None, "")})
    validated = AirConditionerInput.model_validate(values)
    return validated, {"stage": "air_conditioner_agent_extraction", "provider": response.provider, "model": response.model, "latency_ms": response.latency_ms, "data": validated.model_dump()}

