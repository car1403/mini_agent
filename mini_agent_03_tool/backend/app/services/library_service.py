"""도서관 Agent의 근거 수집과 확인된 상태 변경을 연결합니다."""

from app.agents.library_loan_agent import run_library_loan_agent
from app.repositories.lab_repository import lab_repository
from app.schemas.lab import LabRunRequest
from app.tools.lab_tools import execute_lab_tool


def run(payload: LabRunRequest) -> dict:
    if payload.confirmed:
        action = lab_repository.consume_pending_action(payload.action_id or "", "library")
        if action is None:
            return _result("rejected", "유효한 확인 작업을 찾지 못했습니다.", "invalid_action")
        execution = execute_lab_tool(action["tool_name"], action["arguments"])
        if not execution["success"]:
            return _result("error", "대출 Tool 실행에 실패했습니다.", "tool_error", trace=[execution], calls=[action])
        decision = execution["data"]
        status = "completed" if decision["allowed"] else "rejected"
        reason = "completed" if decision["allowed"] else "policy_rejected_at_execution"
        return _result(status, decision["reason"], reason, lab_repository.snapshot("library"), [execution], [action])

    outcome = run_library_loan_agent(payload.arguments)
    if outcome["status"] != "ready":
        return outcome
    action = lab_repository.create_pending_action(
        "library", "apply_library_loan",
        {"member_id": outcome["state"]["member_id"], "book_id": outcome["state"]["book_id"]},
    )
    outcome.update({
        "status": "confirmation_required",
        "answer": "대출 정책을 통과했습니다. 실제 대출 실행을 확인해 주세요.",
        "reason": "confirmation_required",
        "state": {
            **outcome["state"],
            "pending_action_id": action["action_id"],
            "expires_at": action["expires_at"].isoformat(),
        },
        "calls": [*outcome["calls"], {"tool": action["tool_name"], "arguments": action["arguments"]}],
    })
    return outcome


def _result(status, answer, reason, state=None, trace=None, calls=None):
    return {
        "status": status, "answer": answer, "state": state or {},
        "trace": trace or [], "reason": reason,
        "calls": [{"tool": item["tool_name"], "arguments": item["arguments"]} for item in (calls or [])],
    }
