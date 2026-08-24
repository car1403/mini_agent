"""부족한 근거에 따라 다음 조회 Tool을 선택하는 도서 대출 Agent입니다."""

from typing import Any

from app.tools.lab_tools import evaluate_loan, execute_lab_tool


MAX_STEPS = 4


def _next_tool(facts: dict[str, Any]) -> str | None:
    if "member" not in facts:
        return "get_member"
    if "book" not in facts:
        return "get_book"
    if "loans" not in facts:
        return "get_current_loans"
    return None


def run_library_loan_agent(arguments: dict[str, Any]) -> dict[str, Any]:
    """현재 상태에서 부족한 근거를 하나씩 조회하고 정책 평가 시 종료합니다."""
    member_id, book_id = arguments.get("member_id"), arguments.get("book_id")
    missing = [key for key, value in (("member_id", member_id), ("book_id", book_id)) if not value]
    if missing:
        return {
            "status": "needs_clarification",
            "answer": f"다음 정보를 알려주세요: {', '.join(missing)}",
            "state": {}, "trace": [], "reason": "needs_user_input", "calls": [],
        }

    facts: dict[str, Any] = {}
    calls: list[dict[str, Any]] = []
    trace: list[dict[str, Any]] = []
    tool_arguments = {
        "get_member": {"member_id": member_id},
        "get_book": {"book_id": book_id},
        "get_current_loans": {"member_id": member_id},
    }
    result_keys = {"get_member": "member", "get_book": "book", "get_current_loans": "loans"}

    for step in range(1, MAX_STEPS + 1):
        tool_name = _next_tool(facts)
        trace.append({"step": step, "stage": "agent_decision", "action": tool_name or "finish"})
        if tool_name is None:
            decision = evaluate_loan(facts)
            trace.append({"step": step, "stage": "backend_policy", "data": decision})
            return {
                "status": "ready" if decision["allowed"] else "rejected",
                "answer": decision["reason"],
                "state": {"member_id": member_id, "book_id": book_id, "facts": facts},
                "trace": trace, "reason": "ready_for_confirmation" if decision["allowed"] else "policy_rejected",
                "calls": calls,
            }

        call = {"tool": tool_name, "arguments": tool_arguments[tool_name]}
        calls.append(call)
        execution = execute_lab_tool(tool_name, call["arguments"])
        trace.append({"step": step, "stage": "tool_execution", "data": execution})
        if not execution["success"]:
            return {
                "status": "error", "answer": "조회 Tool 실행에 실패했습니다.",
                "state": facts, "trace": trace, "reason": "tool_error", "calls": calls,
            }
        facts[result_keys[tool_name]] = execution["data"][result_keys[tool_name]]

    return {
        "status": "error", "answer": "최대 실행 횟수 안에 근거 수집을 완료하지 못했습니다.",
        "state": facts, "trace": trace, "reason": "max_steps_exceeded", "calls": calls,
    }
