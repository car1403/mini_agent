"""서로 다른 LLM API를 동일한 내부 계약으로 사용할 수 있게 하는 Adapter 패키지입니다.

Provider의 책임:
- OpenAI·Gemini·Ollama·Mock의 요청 형식 차이를 변환합니다.
- 모델 API를 한 번 호출하고 응답을 공통 결과로 정규화합니다.

Provider의 책임이 아닌 것:
- 사용할 Tool 목록과 Agent 실행 순서를 결정하지 않습니다.
- Tool을 직접 실행하거나 Tool Loop를 반복하지 않습니다.
- 누락된 업무 입력, 승인, 재시도 같은 Agent 정책을 소유하지 않습니다.

Stage 01·02의 Router와 Service가 구체 모델 SDK 대신 이 패키지의 공통 계약을 사용합니다.
"""

from app.providers.base import LLMProvider
from app.providers.models import ProviderResult
from app.providers.registry import get_provider, provider_status

__all__ = [
    "LLMProvider",
    "ProviderResult",
    "get_provider",
    "provider_status",
]
