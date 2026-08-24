"""Ollama로 택배함 ID와 인증 코드를 추출하는 Agent입니다."""
from typing import Any
from app.providers.registry import get_provider
from app.schemas.lab import ParcelLockerInput

def extract_parcel_locker_request(message: str, explicit_arguments: dict[str, Any] | None = None):
    """입력값만 구조화하며 인증 성공·만료·재사용 여부는 판단하지 않습니다."""
    response = get_provider("ollama").generate_structured("택배함 ID와 인증 코드를 문자열로 추출하세요. 없으면 null입니다.", message, ParcelLockerInput)
    values = dict(response.content); values.update({k: v for k, v in (explicit_arguments or {}).items() if v not in (None, "")})
    validated = ParcelLockerInput.model_validate(values)
    return validated, {"stage": "parcel_locker_agent_extraction", "provider": response.provider, "model": response.model, "latency_ms": response.latency_ms, "data": validated.model_dump()}

