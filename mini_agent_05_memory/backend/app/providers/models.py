"""Provider Adapter가 반환하는 공통 생성·Tool Call 결과 모델입니다."""

from dataclasses import dataclass
from typing import Any

@dataclass
class ProviderResult:
    provider: str
    model: str
    content: str | dict[str, Any]
    latency_ms: int

@dataclass
class ProviderToolCall:
    provider: str
    model: str
    tool_name: str | None
    arguments: dict[str, Any]
    reason: str
    confidence: float
    latency_ms: int
