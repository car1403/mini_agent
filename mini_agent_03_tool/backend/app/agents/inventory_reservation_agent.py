"""Ollama로 재고 예약 요청의 SKU·수량·Version을 추출하는 Agent입니다."""
from typing import Any
from app.providers.registry import get_provider
from app.schemas.lab import InventoryInput

def extract_inventory_request(message: str, explicit_arguments: dict[str, Any] | None = None):
    """예약 인자만 구조화하며 재고·Version 정책과 성공 여부는 결정하지 않습니다."""
    response = get_provider("ollama").generate_structured("SKU, 예약 수량, 조회 version을 추출하세요. 없으면 null입니다.", message, InventoryInput)
    values = dict(response.content); values.update({k: v for k, v in (explicit_arguments or {}).items() if v not in (None, "")})
    validated = InventoryInput.model_validate(values)
    return validated, {"stage": "inventory_agent_extraction", "provider": response.provider, "model": response.model, "latency_ms": response.latency_ms, "data": validated.model_dump()}

