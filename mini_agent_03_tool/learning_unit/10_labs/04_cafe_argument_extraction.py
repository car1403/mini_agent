"""Lab 04 — 여러 대화에서 주문 정보를 모으는 단일 Agent Cycle을 실행합니다.

학습 분류:
- 현재 성격: arguments 추출 + 재질문
- Agent 여부: 부분적 Agent
- 권장 방향: 상태를 유지하는 단일 Agent Cycle로 확장
- 판단 근거: Agent는 현재 상태와 새 메시지를 함께 보고 arguments를 갱신한 뒤
  재질문 또는 종료를 선택합니다. 이 Lab은 Tool을 반복 실행하는 Agent Loop가 아니라
  사용자 메시지 한 번마다 한 번 판단하는 Agent Cycle입니다.

Backend 디렉터리 기준 역할:
- `schemas/`: CafeOrderInput이 주문 Tool의 필수 arguments 계약을 정의합니다.
- `agents/`: OrderAgentState를 유지하며 run_agent_cycle이 재질문 또는 종료를 결정합니다.
- `tools/`: 완전한 arguments가 만들어진 뒤 실행될 주문 Tool은 이 실습 범위에서 생략합니다.
- `services/`: 별도의 업무 Service 없이 Agent의 추출·재질문 판단에 집중합니다.
- `routers/`: 이 파일에서는 `__main__` 실행부가 사용자 문장 입력을 대신합니다.
- `providers/`: 실제 Provider 대신 규칙 기반 Mock 추출기를 사용합니다.
"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError


# [schemas/] 주문 Tool이 요구하는 메뉴·크기·수량 arguments 계약입니다.
class CafeOrderInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    menu: Literal["아메리카노", "카페라테", "레몬에이드"]
    size: Literal["small", "medium", "large"]
    quantity: int = Field(ge=1, le=10)


# [agents/] 대화가 이어져도 이미 수집한 arguments와 Trace를 보존하는 Agent 상태입니다.
class OrderAgentState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    arguments: dict[str, Any] = Field(default_factory=dict)
    status: Literal["collecting", "ready", "invalid"] = "collecting"
    trace: list[dict[str, Any]] = Field(default_factory=list)


# [agents/ 보조 규칙] Mock 추출기가 한국어 표현을 Tool arguments 값으로 바꿀 때 사용합니다.
SIZE_WORDS = {"스몰": "small", "미디엄": "medium", "라지": "large"}
QUANTITY_WORDS = {"한": 1, "두": 2, "세": 3}


# [agents/] 실제 Provider의 Tool Call 대신 문장에서 arguments를 추출하는 Mock 판단기입니다.
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


# [agents/] 메시지 한 번마다 상태 갱신 → 검증 → 재질문/종료 중 하나를 선택합니다.
def run_agent_cycle(state: OrderAgentState, message: str) -> dict[str, Any]:
    extracted = mock_extract_arguments(message)
    state.arguments.update(extracted)
    state.trace.append({"stage": "extract_arguments", "data": extracted})

    missing = [field for field in CafeOrderInput.model_fields if field not in state.arguments]
    if missing:
        labels = {"menu": "메뉴", "size": "크기", "quantity": "수량"}
        state.status = "collecting"
        question = f"{', '.join(labels[field] for field in missing)}을(를) 알려주세요."
        state.trace.append({"stage": "ask_clarification", "data": {"missing": missing}})
        return {
            "status": "needs_clarification",
            "arguments": state.arguments.copy(),
            "missing_arguments": missing,
            "follow_up_question": question,
            "trace": state.trace.copy(),
        }
    try:
        order = CafeOrderInput.model_validate(state.arguments)
        state.status = "ready"
        state.trace.append({"stage": "finish", "data": order.model_dump()})
        return {"status": "ready", "arguments": order.model_dump(), "trace": state.trace.copy()}
    except ValidationError as error:
        state.status = "invalid"
        state.trace.append({"stage": "validation_error", "data": error.errors()})
        return {
            "status": "invalid",
            "arguments": state.arguments.copy(),
            "errors": error.errors(),
            "trace": state.trace.copy(),
        }


# [routers/ 대체] 두 번의 사용자 입력 사이에서 arguments가 유지되는지 확인합니다.
if __name__ == "__main__":
    agent_state = OrderAgentState()
    for text in ("카페라테 주세요", "라지 두 잔 주세요"):
        print(f"\n사용자: {text}")
        print(run_agent_cycle(agent_state, text))
