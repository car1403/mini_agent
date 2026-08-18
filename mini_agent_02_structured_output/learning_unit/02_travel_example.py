"""LLM이 만들었다고 가정한 여행 JSON을 Pydantic으로 검증합니다."""

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class TravelRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    destination: str = Field(min_length=1)
    start_date: date | None = None
    nights: int | None = Field(default=None, ge=1, le=30)
    adults: int | None = Field(default=None, ge=1, le=20)
    budget: int | None = Field(default=None, gt=0)
    transportation: Literal["public", "car", "flight", "unknown"] = "unknown"
    missing_fields: list[str] = Field(default_factory=list)


SAMPLES: dict[str, dict[str, Any]] = {
    "필수 정보가 있는 요청": {
        "destination": "부산", "start_date": "2026-08-10", "nights": 2,
        "adults": 2, "budget": 500000, "transportation": "public", "missing_fields": [],
    },
    "모르는 값을 누락 목록에 기록": {
        "destination": "제주", "start_date": None, "nights": None,
        "adults": 2, "budget": None, "transportation": "unknown",
        "missing_fields": ["start_date", "nights", "budget"],
    },
    "범위를 벗어난 값": {
        "destination": "강릉", "start_date": "2026-09-01", "nights": 0,
        "adults": "두 명", "budget": -1, "transportation": "train", "missing_fields": [],
    },
}


def validate_travel_output(name: str, payload: dict[str, Any]) -> None:
    print(f"\n[{name}]")
    try:
        print(TravelRequest.model_validate(payload).model_dump_json(indent=2))
    except ValidationError as error:
        for item in error.errors():
            print(f"- {'.'.join(map(str, item['loc']))}: {item['msg']}")


if __name__ == "__main__":
    for sample_name, sample_payload in SAMPLES.items():
        validate_travel_output(sample_name, sample_payload)
