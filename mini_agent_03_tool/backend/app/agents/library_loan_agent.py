"""도서 대출 판단에 필요한 조회 Tool을 선택하는 Agent입니다.

Agent는 회원·도서·대출 목록이라는 근거를 수집합니다. 대출 허용 여부와 상태 변경은
Agent가 아니라 `apply_loan`의 Backend 업무 규칙이 최종 결정합니다.
"""
from typing import Any
from app.tools.lab_tools import apply_loan, library_facts

def run_library_loan_agent(arguments: dict[str, Any]) -> dict[str, Any]:
    """필요한 세 조회 Tool의 결과를 모은 뒤 서버 정책으로 넘깁니다."""
    member_id, book_id = arguments.get("member_id"), arguments.get("book_id")
    missing = [key for key, value in (("member_id", member_id), ("book_id", book_id)) if not value]
    if missing: return {"status": "needs_clarification", "answer": f"다음 정보를 알려주세요: {', '.join(missing)}", "state": {}, "trace": [], "reason": "needs_user_input", "calls": []}
    facts = library_facts(member_id, book_id)
    calls = [{"tool": "get_member", "arguments": {"member_id": member_id}}, {"tool": "get_book", "arguments": {"book_id": book_id}}, {"tool": "get_current_loans", "arguments": {"member_id": member_id}}]
    trace = [{"step": index, "stage": "tool_result", "tool": call["tool"], "data": value} for index, (call, value) in enumerate(zip(calls, facts.values()), 1)]
    # 수집한 사실을 LLM 답변으로 확정하지 않고 결정적인 서버 정책에 전달합니다.
    decision = apply_loan(member_id, book_id, facts)
    trace.append({"stage": "backend_policy", "data": decision})
    return {"status": "completed", "answer": decision["reason"], "state": facts, "trace": trace, "reason": "completed", "calls": calls}
