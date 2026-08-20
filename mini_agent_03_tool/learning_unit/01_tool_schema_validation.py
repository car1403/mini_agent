"""Tool arguments를 Pydantic으로 검증하고 오류 위치를 확인합니다."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator


class HotelInput(BaseModel):
    # Schema에 없는 인자를 차단해 LLM이 임의 필드를 추가하지 못하게 합니다.
    model_config = ConfigDict(extra="forbid")

    city: str = Field(min_length=1)
    check_in: date
    check_out: date
    guests: int = Field(ge=1, le=10)

    @model_validator(mode="after")
    def validate_dates(self) -> "HotelInput":
        # 각 필드의 타입뿐 아니라 두 날짜 사이의 업무 규칙도 검증합니다.
        if self.check_out <= self.check_in:
            raise ValueError("체크아웃은 체크인 이후여야 합니다.")
        return self


# 정상 입력과 대표 실패 입력을 같은 코드 경로로 비교합니다.
CASES = {
    "정상": {"city": "부산", "check_in": "2026-08-12", "check_out": "2026-08-14", "guests": 2},
    "필수값 누락": {"city": "부산", "check_in": "2026-08-12", "check_out": "2026-08-14"},
    "잘못된 날짜": {"city": "부산", "check_in": "2026-08-14", "check_out": "2026-08-12", "guests": 2},
    "정의되지 않은 인자": {"city": "부산", "check_in": "2026-08-12", "check_out": "2026-08-14", "guests": 2, "payment": True},
}


if __name__ == "__main__":
    for name, arguments in CASES.items():
        print(f"\n[{name}]")
        try:
            # 문자열 날짜 변환과 범위·필수값·추가 필드 검사를 한 번에 수행합니다.
            print(HotelInput.model_validate(arguments).model_dump(mode="json"))
        except ValidationError as error:
            # API에서 활용할 수 있도록 오류 위치와 종류를 구조화해 출력합니다.
            for item in error.errors():
                print({"field": ".".join(map(str, item["loc"])), "message": item["msg"], "type": item["type"]})
