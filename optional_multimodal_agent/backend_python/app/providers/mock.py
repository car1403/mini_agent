from typing import TypeVar

from pydantic import BaseModel

from app.providers.base import ProviderResult, ToolSelectionResult, timed_call


T = TypeVar("T", bound=BaseModel)


class MockProvider:
    name = "mock"
    model = "deterministic-travel-mock"

    def generate(self, system_prompt: str, message: str) -> ProviderResult:
        content, latency = timed_call(
            lambda: f"[Mock 응답] 요청을 확인했습니다: {message}"
        )
        return ProviderResult(self.name, self.model, content, latency)

    def generate_structured(
        self,
        system_prompt: str,
        message: str,
        response_model: type[T],
    ) -> ProviderResult:
        destination = next(
            (city for city in ("서울", "부산", "제주", "강릉") if city in message),
            "부산",
        )
        value, latency = timed_call(
            lambda: response_model.model_validate(
                {
                    "destination": destination,
                    "summary": f"{destination}의 대표 장소를 둘러보는 교육용 일정입니다.",
                    "recommended_days": 3,
                    "activities": ["지역 명소 방문", "현지 음식 체험"],
                    "cautions": ["실제 예약 전 가격과 운영 시간을 확인하세요."],
                }
            )
        )
        return ProviderResult(self.name, self.model, value.model_dump(), latency)

    def select_tool(
        self,
        system_prompt: str,
        message: str,
        tools: list[dict],
    ) -> ToolSelectionResult:
        started_tool = None
        arguments = {}
        if any(word in message for word in ("날씨", "기온", "우산", "비가 와")):
            started_tool = "get_weather"
            arguments = {"city": "부산", "target_date": "2026-08-10"}
        elif any(word in message for word in ("호텔", "숙소")):
            started_tool = "search_hotels"
            arguments = {
                "city": "부산",
                "check_in": "2026-08-10",
                "check_out": "2026-08-12",
                "guests": 2,
            }
        return ToolSelectionResult(
            self.name,
            self.model,
            started_tool,
            arguments,
            0,
        )
