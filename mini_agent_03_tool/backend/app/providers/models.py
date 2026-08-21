"""Provider 어댑터가 반환하는 공통 결과 모델입니다.

각 Provider 구현과 Stage 01·02 Service 사이에서 SDK별 응답 형식이 새어 나오지 않도록 사용합니다.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ProviderResult:
    provider: str
    model: str
    content: str | dict[str, Any]
    latency_ms: int
