"""LLM이 만들었다고 가정한 TravelPlan JSON을 검증합니다."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class TravelPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    destination: str = Field(min_length=1)
    summary: str = Field(min_length=1, max_length=500)
    recommended_days: int = Field(ge=1, le=30)
    activities: list[str] = Field(min_length=1, max_length=10)
    cautions: list[str] = Field(default_factory=list, max_length=10)


SAMPLES: dict[str, dict[str, Any]] = {
    "정상 여행 계획": {"destination": "부산", "summary": "대중교통 중심 여행", "recommended_days": 3, "activities": ["해운대", "시장 방문"], "cautions": ["운영 시간 확인"]},
    "필수 필드 누락": {"destination": "제주", "summary": "자연 명소 중심 일정", "recommended_days": 2, "cautions": []},
    "범위를 벗어난 값": {"destination": "강릉", "summary": "여행", "recommended_days": 0, "activities": [], "cautions": []},
    "계약에 없는 필드": {"destination": "서울", "summary": "도심 명소 일정", "recommended_days": 2, "activities": ["박물관 방문"], "cautions": [], "password": "Schema 밖의 값"},
}


def validate_travel_output(name: str, payload: dict[str, Any]) -> None:
    print(f"\n[{name}]")
    try:
        print(TravelPlan.model_validate(payload).model_dump_json(indent=2))
    except ValidationError as error:
        for item in error.errors():
            print(f"- {'.'.join(map(str, item['loc']))}: {item['msg']}")


if __name__ == "__main__":
    for sample_name, sample_payload in SAMPLES.items():
        validate_travel_output(sample_name, sample_payload)
