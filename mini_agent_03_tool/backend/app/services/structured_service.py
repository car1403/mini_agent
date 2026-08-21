"""여행 계획 Structured Output 유스케이스를 Provider에 위임합니다.

Stage 02 라우터가 공통 TravelPlan 스키마로 결과를 생성할 때 사용합니다.
"""

from app.providers.models import ProviderResult
from app.providers.registry import get_provider
from app.schemas.stage_02 import TravelPlan


def generate_structured(provider: str, system_prompt: str, message: str) -> ProviderResult:
    return get_provider(provider).generate_structured(system_prompt, message, TravelPlan)
