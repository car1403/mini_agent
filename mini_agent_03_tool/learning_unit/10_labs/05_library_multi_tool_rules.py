"""Lab 05 — Agent가 필요한 조회 Tool을 고르고 서버가 대출 정책을 적용합니다.

학습 분류:
- 현재 성격: 여러 Tool을 고정 순서로 호출하던 Workflow
- Agent 여부: 기존에는 아니오, 이 버전에서는 학습용 Agent
- 권장 방향: 동적 Tool 선택 Agent로 확장
- 판단 근거: Agent는 현재 상태에서 부족한 정보에 따라 다음 조회 Tool 또는 종료를
  선택합니다. 단, 대출 승인과 상태 변경은 Agent가 아니라 Backend Service가 담당합니다.

Backend 디렉터리 기준 역할:
- `tools/`: get_member, get_book, get_current_loans가 독립적인 조회 Tool입니다.
- `services/`: evaluate_loan과 apply_loan이 승인 정책과 상태 변경을 담당합니다.
- `agents/`: run_library_agent가 상태를 보고 다음 조회 Tool 또는 종료를 선택합니다.
- `schemas/`: LoanRequest와 LibraryAgentState가 요청·실행 상태 계약을 정의합니다.
- `routers/`: 이 파일에서는 `__main__` 실행부가 대출 요청 Endpoint를 대신합니다.
- `providers/`: 이 파일은 Mock 판단기를 사용하며 실제 환경에서는 LLM 선택으로 교체할 수 있습니다.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# [schemas/] Agent 요청과 반복 실행 상태의 계약입니다.
class LoanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    member_id: str = Field(pattern=r"^M\d+$")
    book_id: str = Field(pattern=r"^B\d+$")


class LibraryAgentState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request: LoanRequest
    tool_results: dict[str, dict[str, Any]] = Field(default_factory=dict)
    trace: list[dict[str, Any]] = Field(default_factory=list)


# [학습용 저장소] 실제 Backend에서는 회원·도서·대출 Repository 또는 DB가 담당합니다.
MEMBERS = {
    "M100": {"name": "김민준", "active": True, "overdue": False},
    "M200": {"name": "이서연", "active": True, "overdue": True},
}
BOOKS = {
    "B101": {"title": "파이썬 첫걸음", "available": True},
    "B102": {"title": "에이전트 설계", "available": False},
}
LOANS = {"M100": ["B201", "B202"], "M200": ["B203"]}
MAX_LOANS = 3


# [tools/] 회원 ID로 회원 상태를 조회하는 읽기 전용 Tool입니다.
def get_member(member_id: str) -> dict[str, Any]:
    return {"member_id": member_id, "member": MEMBERS.get(member_id)}


# [tools/] 도서 ID로 도서와 대출 가능 상태를 조회하는 읽기 전용 Tool입니다.
def get_book(book_id: str) -> dict[str, Any]:
    return {"book_id": book_id, "book": BOOKS.get(book_id)}


# [tools/] 회원의 현재 대출 목록과 권수를 조회하는 읽기 전용 Tool입니다.
def get_current_loans(member_id: str) -> dict[str, Any]:
    loans = LOANS.get(member_id, [])
    return {"member_id": member_id, "book_ids": loans.copy(), "count": len(loans)}


# [tools/] Tool 설명과 실행 함수를 함께 보관하는 학습용 Allowlist입니다.
TOOL_REGISTRY = {
    "get_member": get_member,
    "get_book": get_book,
    "get_current_loans": get_current_loans,
}


# [tools/] Agent의 제안을 신뢰하지 않고 등록된 Tool만 Backend에서 실행합니다.
def execute_allowed_tool(tool_name: str, request: LoanRequest) -> dict[str, Any]:
    tool = TOOL_REGISTRY.get(tool_name)
    if tool is None:
        raise ValueError(f"허용되지 않은 Tool입니다: {tool_name}")
    argument = request.book_id if tool_name == "get_book" else request.member_id
    return tool(argument)


# [services/] 세 Tool Result를 조합해 서버의 대출 허용 규칙을 적용합니다.
def evaluate_loan(member_result: dict, book_result: dict, loans_result: dict) -> dict[str, Any]:
    """LLM 답변이 아니라 백엔드 업무 규칙이 대출 가능 여부를 결정합니다."""
    member = member_result["member"]
    book = book_result["book"]
    if member is None:
        return {"allowed": False, "reason": "회원 정보를 찾을 수 없습니다."}
    if not member["active"]:
        return {"allowed": False, "reason": "비활성 회원입니다."}
    if member["overdue"]:
        return {"allowed": False, "reason": "연체 도서가 있습니다."}
    if book is None:
        return {"allowed": False, "reason": "도서 정보를 찾을 수 없습니다."}
    if not book["available"]:
        return {"allowed": False, "reason": "이미 대출 중인 도서입니다."}
    if loans_result["count"] >= MAX_LOANS:
        return {"allowed": False, "reason": "최대 대출 권수를 초과합니다."}
    return {"allowed": True, "reason": "대출할 수 있습니다."}


# [services/] Agent가 모은 근거를 받은 뒤에만 서버 권한으로 상태를 변경합니다.
def apply_loan(member_id: str, book_id: str, tool_results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    decision = evaluate_loan(tool_results["member"], tool_results["book"], tool_results["loans"])
    if decision["allowed"]:
        LOANS.setdefault(member_id, []).append(book_id)
        BOOKS[book_id]["available"] = False
    return {"tool_results": tool_results, "decision": decision}


# [agents/] 현재 상태에서 부족한 근거를 찾아 다음 Tool 또는 종료를 선택합니다.
def choose_next_action(state: LibraryAgentState) -> str:
    for result_key, tool_name in (
        ("member", "get_member"),
        ("book", "get_book"),
        ("loans", "get_current_loans"),
    ):
        if result_key not in state.tool_results:
            return tool_name
    return "finish"


# [agents/] 최대 반복 횟수와 종료 조건을 가진 작은 학습용 Agent Loop입니다.
def run_library_agent(member_id: str, book_id: str, max_steps: int = 4) -> dict[str, Any]:
    state = LibraryAgentState(request=LoanRequest(member_id=member_id, book_id=book_id))
    result_keys = {"get_member": "member", "get_book": "book", "get_current_loans": "loans"}

    for step in range(1, max_steps + 1):
        action = choose_next_action(state)
        state.trace.append({"step": step, "stage": "agent_decision", "action": action})
        if action == "finish":
            result = apply_loan(member_id, book_id, state.tool_results)
            return {**result, "termination_reason": "completed", "trace": state.trace}

        tool_result = execute_allowed_tool(action, state.request)
        state.tool_results[result_keys[action]] = tool_result
        state.trace.append({"step": step, "stage": "tool_result", "tool": action, "data": tool_result})

    return {
        "tool_results": state.tool_results,
        "decision": {"allowed": False, "reason": "최대 반복 횟수 안에 판단을 완료하지 못했습니다."},
        "termination_reason": "max_steps_exceeded",
        "trace": state.trace,
    }


# [routers/ 대체] API 대신 Agent의 선택 Trace와 서버 정책 결과를 확인합니다.
if __name__ == "__main__":
    for member_id, book_id in (("M100", "B101"), ("M200", "B101"), ("M100", "B102")):
        print(f"\n요청: {member_id} / {book_id}")
        print(run_library_agent(member_id, book_id))
