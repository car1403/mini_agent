"""대화 상태를 보고 재질문 또는 종료를 선택하는 카페 주문 Agent입니다.

정해진 한 번의 Workflow가 아니라 메시지마다 부족한 값을 판단하므로 Agent 패턴으로
분류합니다. 실제 결제나 외부 주문은 수행하지 않고 Mock 주문 Tool 결과만 만듭니다.
"""
import re
from typing import Any
from app.repositories.lab_repository import lab_repository
from app.tools.lab_tools import execute_lab_tool

def run_cafe_order_agent(session_id: str, message: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """이전 arguments와 새 입력을 병합하고 누락값이 있으면 재질문합니다."""
    state = lab_repository.session(session_id, "cafe")
    for menu in ("아메리카노", "카페라테"):
        if menu in message: state["menu"] = menu
    for size in ("스몰", "미디엄", "라지"):
        if size in message: state["size"] = size
    match = re.search(r"(\d+)\s*잔", message)
    if match: state["quantity"] = int(match.group(1))
    else:
        for word, value in {"한": 1, "두": 2, "세": 3}.items():
            if f"{word} 잔" in message or f"{word}잔" in message: state["quantity"] = value
    state.update({key: value for key, value in arguments.items() if key in {"menu", "size", "quantity"}})
    missing = [key for key in ("menu", "size", "quantity") if not state.get(key)]
    trace = [{"stage": "cafe_agent_extraction", "data": state.copy()}, {"stage": "agent_decision", "action": "ask_clarification" if missing else "finish"}]
    # Agent가 값을 임의로 채우지 않고 다음 사용자 Cycle을 요청합니다.
    if missing:
        return {"status": "needs_clarification", "answer": f"다음 정보를 알려주세요: {', '.join(missing)}", "state": state.copy(), "trace": trace, "reason": "needs_user_input", "calls": []}
    # 모든 필수값이 모였을 때만 허용된 Mock Tool 호출을 제안하고 종료합니다.
    call = {"tool": "create_mock_order", "arguments": state.copy()}
    execution = execute_lab_tool(call["tool"], call["arguments"])
    if not execution["success"]:
        return {"status": "error", "answer": "주문 Tool 실행에 실패했습니다.", "state": state.copy(), "trace": trace + [{"stage": "tool_execution", "data": execution}], "reason": "tool_error", "calls": [call]}
    return {"status": "completed", "answer": f"{state['size']} {state['menu']} {state['quantity']}잔 주문을 확인했습니다.", "state": state.copy(), "trace": trace + [{"stage": "tool_execution", "data": execution}], "reason": "completed", "calls": [call]}
