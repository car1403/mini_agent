"""분류·판단형 Structured Output인 SupportTicket을 검증합니다."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class SupportTicket(BaseModel):
    model_config = ConfigDict(extra="forbid")
    category: Literal["billing", "technical", "account", "other"]
    priority: Literal["low", "medium", "high"]
    summary: str = Field(min_length=1, max_length=300)
    requires_human: bool = Field(strict=True)
    missing_information: list[str] = Field(default_factory=list, max_length=10)


SAMPLES: dict[str, dict[str, Any]] = {
    "결제 문의": {"category": "billing", "priority": "medium", "summary": "중복 결제 확인 요청", "requires_human": True, "missing_information": ["주문 번호"]},
    "기술 문의": {"category": "technical", "priority": "high", "summary": "로그인 후 서버 오류 발생", "requires_human": True, "missing_information": ["오류 발생 시각"]},
    "허용하지 않은 분류": {"category": "refund", "priority": "urgent", "summary": "환불 요청", "requires_human": "yes", "missing_information": []},
}


def validate_support_output(name: str, payload: dict[str, Any]) -> None:
    print(f"\n[{name}]")
    try:
        print(SupportTicket.model_validate(payload).model_dump_json(indent=2))
    except ValidationError as error:
        for item in error.errors():
            print(f"- {'.'.join(map(str, item['loc']))}: {item['msg']}")


if __name__ == "__main__":
    for sample_name, sample_payload in SAMPLES.items():
        validate_support_output(sample_name, sample_payload)
