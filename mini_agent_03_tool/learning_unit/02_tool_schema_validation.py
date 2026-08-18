"""Tool arguments를 Pydantic으로 검증하고 오류 위치를 확인합니다."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator


class HotelInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    city: str = Field(min_length=1)
    check_in: date
    check_out: date
    guests: int = Field(ge=1, le=10)

    @model_validator(mode="after")
    def validate_dates(self) -> "HotelInput":
        if self.check_out <= self.check_in:
            raise ValueError("체크아웃은 체크인 이후여야 합니다.")
        return self


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
            print(HotelInput.model_validate(arguments).model_dump(mode="json"))
        except ValidationError as error:
            for item in error.errors():
                print({"field": ".".join(map(str, item["loc"])), "message": item["msg"], "type": item["type"]})
