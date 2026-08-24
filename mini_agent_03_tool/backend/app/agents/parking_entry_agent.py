"""Ollama로 주차장 요청의 차량 번호를 추출하는 Agent입니다."""
from typing import Any
from app.providers.registry import get_provider
from app.schemas.lab import ParkingInput

def extract_parking_request(message: str, explicit_arguments: dict[str, Any] | None = None):
    """차량 번호 후보만 반환하며 차량 조회·출입 승인·문 열기는 수행하지 않습니다."""
    response = get_provider("ollama").generate_structured("차량 번호만 추출하세요. 없으면 null입니다.", message, ParkingInput)
    values = dict(response.content); values.update({k: v for k, v in (explicit_arguments or {}).items() if v not in (None, "")})
    validated = ParkingInput.model_validate(values)
    return validated, {"stage": "parking_agent_extraction", "provider": response.provider, "model": response.model, "latency_ms": response.latency_ms, "data": validated.model_dump()}

