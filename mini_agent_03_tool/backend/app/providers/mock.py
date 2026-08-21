"""외부 API 없이 일반/구조화 생성을 재현하는 학습용 Mock Provider입니다.

`providers.registry`가 생성하며 Stage 01·02 예제와 테스트에서만 사용합니다.
"""

from typing import Any

from pydantic import BaseModel

from app.providers.models import ProviderResult


class MockProvider:
    name = "mock"
    model = "deterministic-travel-mock"

    def generate(self, system_prompt: str, message: str) -> ProviderResult:
        return ProviderResult(self.name, self.model, f"[Mock 응답] 질문을 확인했습니다: {message}", 0)

    def generate_structured(self, system_prompt: str, message: str, response_schema: type[BaseModel]) -> ProviderResult:
        destination = next((city for city in ("서울", "부산", "제주", "강릉") if city in message), "부산")
        result = response_schema(
            destination=destination,
            summary=f"{destination}의 대표 장소를 둘러보는 교육용 일정입니다.",
            recommended_days=3,
            activities=["지역 명소 방문", "현지 음식 체험"],
            cautions=["실제 예약 전 가격과 운영 시간을 확인하세요."],
        )
        return ProviderResult(self.name, self.model, result.model_dump(), 0)

    def status(self) -> dict[str, Any]:
        return {"provider": self.name, "configured": True, "model": self.model, "environment": "local-python"}
