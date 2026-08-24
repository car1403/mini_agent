"""주차장 출입 순서를 소유하는 Agent-assisted Workflow입니다.

Agent는 차량 번호를 추출할 뿐 출입 허용과 문 열기를 결정하지 않습니다. Service가
차량 조회, 활성 권한 정책, 사용자 확인 순서를 고정하고 마지막에만 상태 변경 Tool을
실행합니다.
"""
from app.agents.parking_entry_agent import extract_parking_request
from app.repositories.lab_repository import lab_repository
from app.schemas.lab import LabRunRequest
from app.tools.lab_tools import lookup_vehicle, parking_entry

def run(payload: LabRunRequest) -> dict:
    """추출 → 조회 → 정책 → 확인 → 실행의 고정된 Workflow를 한 단계 진행합니다."""
    if payload.confirmed:
        # 확인 요청에서는 Agent를 다시 호출하지 않고 검증 당시 저장한 action만 소비합니다.
        action = lab_repository.consume_pending_action(payload.action_id or "", "parking")
        if action is None: return _stopped("유효한 확인 작업을 찾지 못했습니다.", "invalid_action")
        result = parking_entry(**action["arguments"])
        return _done(result, [{"stage": "confirmed_tool_execution", "data": result}], action)
    # 유연한 자연어 해석은 도메인 Agent에 맡기되 그 출력은 Schema로 검증됩니다.
    values, extraction = extract_parking_request(payload.message, payload.arguments)
    if not values.plate_number: return _clarify("차량 번호를 알려주세요.", extraction)
    # 조회 Tool은 사실만 반환하고 출입 가능 여부는 아래 Backend 정책이 판단합니다.
    lookup = lookup_vehicle(values.plate_number)
    trace = [extraction, {"stage": "lookup_vehicle", "data": lookup}]
    if not lookup["registered"]: return _stopped("등록되지 않은 차량입니다.", "policy_rejected", trace)
    if not lookup["active"]: return _stopped("출입 권한이 비활성 상태입니다.", "policy_rejected", trace)
    # 상태 변경 Tool은 즉시 실행하지 않고 검증된 arguments를 짧게 보관합니다.
    action = lab_repository.create_pending_action("parking", "open_gate", {"plate_number": values.plate_number})
    return _confirm(action, trace)

def _clarify(answer, trace): return {"status": "needs_clarification", "answer": answer, "state": {}, "trace": [trace], "reason": "needs_user_input", "calls": []}
def _stopped(answer, reason, trace=None): return {"status": "rejected", "answer": answer, "state": {}, "trace": trace or [], "reason": reason, "calls": []}
def _confirm(action, trace): return {"status": "confirmation_required", "answer": "등록 차량입니다. 주차장 문 열기를 확인해 주세요.", "state": {"pending_action_id": action["action_id"], "expires_at": action["expires_at"].isoformat()}, "trace": trace, "reason": "confirmation_required", "calls": [{"tool": action["tool_name"], "arguments": action["arguments"]}]}
def _done(result, trace, action): return {"status": "completed", "answer": "주차장 문을 열었습니다." if result["opened"] else result["reason"], "state": lab_repository.snapshot("parking"), "trace": trace, "reason": "completed", "calls": [{"tool": action["tool_name"], "arguments": action["arguments"]}]}

