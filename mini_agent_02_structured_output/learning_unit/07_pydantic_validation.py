"""일반 dict를 Pydantic 모델로 검증하는 최소 예제입니다."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class ReservationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    customer_name: str = Field(min_length=1)
    reservation_date: date
    people: int = Field(ge=1, le=20)


def validate_sample(name: str, payload: dict) -> None:
    print(f"\n[{name}]")
    try:
        request = ReservationRequest.model_validate(payload)
        print("검증 성공:", request.model_dump(mode="json"))
    except ValidationError as error:
        print("검증 실패:")
        for item in error.errors():
            print(f"- {'.'.join(map(str, item['loc']))}: {item['msg']}")


if __name__ == "__main__":
    validate_sample("정상 데이터", {"customer_name": "김여행", "reservation_date": "2026-08-10", "people": 2})
    validate_sample("잘못된 값", {"customer_name": "", "reservation_date": "잘못된 날짜", "people": 0})
    validate_sample("계약에 없는 필드", {"customer_name": "김여행", "reservation_date": "2026-08-10", "people": 2, "password": "보내면 안 되는 값"})
