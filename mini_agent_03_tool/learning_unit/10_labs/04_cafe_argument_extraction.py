"""카페 주문 문장에서 Tool arguments를 추출하고 누락값을 재질문합니다."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class CafeOrderInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    menu: Literal["아메리카노", "카페라테", "레몬에이드"]
    size: Literal["small", "medium", "large"]
    quantity: int = Field(ge=1, le=10)


SIZE_WORDS = {"스몰": "small", "미디엄": "medium", "라지": "large"}
QUANTITY_WORDS = {"한": 1, "두": 2, "세": 3}


def mock_extract_arguments(message: str) -> dict[str, Any]:
    """실제 서비스에서는 LLM의 Tool Call이 이 arguments를 생성합니다."""
    arguments: dict[str, Any] = {}
    for menu in ("아메리카노", "카페라테", "레몬에이드"):
        if menu in message:
            arguments["menu"] = menu
            break
    for korean_size, value in SIZE_WORDS.items():
        if korean_size in message:
            arguments["size"] = value
            break
    for word, value in QUANTITY_WORDS.items():
        if f"{word} 잔" in message or f"{word}잔" in message:
            arguments["quantity"] = value
            break
    if "quantity" not in arguments:
        arguments["quantity"] = next(
            (number for number in range(1, 11) if f"{number}잔" in message or f"{number} 잔" in message),
            None,
        )
        if arguments["quantity"] is None:
            arguments.pop("quantity")
    return arguments


def prepare_order(message: str) -> dict[str, Any]:
    arguments = mock_extract_arguments(message)
    missing = [field for field in CafeOrderInput.model_fields if field not in arguments]
    if missing:
        labels = {"menu": "메뉴", "size": "크기", "quantity": "수량"}
        return {
            "status": "needs_clarification",
            "arguments": arguments,
            "missing_arguments": missing,
            "follow_up_question": f"{', '.join(labels[field] for field in missing)}을(를) 알려주세요.",
        }
    try:
        order = CafeOrderInput.model_validate(arguments)
        return {"status": "ready", "arguments": order.model_dump()}
    except ValidationError as error:
        return {"status": "invalid", "arguments": arguments, "errors": error.errors()}


if __name__ == "__main__":
    for text in ("라지 아메리카노 두 잔 주세요", "미디엄 카페라테 2 잔 주세요", "카페라테 주세요", "미디엄 한 잔 주세요"):
        print(f"\n사용자: {text}")
        print(prepare_order(text))
