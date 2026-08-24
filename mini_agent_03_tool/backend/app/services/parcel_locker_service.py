"""택배함 인증과 일회성 실행을 보호하는 Agent-assisted Workflow입니다.

Agent는 택배함 ID와 인증 코드를 추출하지만 인증 성공을 판단하지 않습니다. 만료,
코드 일치, 재사용 여부는 Backend 정책이 검사하고 확인된 action만 문 열기 Tool로
전달합니다.
"""
from app.agents.parcel_locker_agent import extract_parcel_locker_request
from app.repositories.lab_repository import lab_repository
from app.schemas.lab import LabRunRequest
from app.tools.lab_tools import inspect_locker, open_locker

def run(payload: LabRunRequest) -> dict:
    """인자 추출 → 인증 사전 검사 → 확인 → 일회성 Tool 실행을 조정합니다."""
    if payload.confirmed:
        # consume은 action을 한 번만 반환하므로 같은 확인 요청의 중복 실행을 막습니다.
        action = lab_repository.consume_pending_action(payload.action_id or "", "parcel_locker")
        if action is None: return result("rejected", "유효한 확인 작업을 찾지 못했습니다.", "invalid_action")
        opened = open_locker(**action["arguments"])
        return result("completed", "택배함을 열었습니다." if opened["opened"] else opened["reason"], "completed", lab_repository.snapshot("parcel_locker"), [{"stage": "confirmed_tool_execution", "data": opened}], [action])
    # Agent 출력은 선택적인 값이며 누락값은 추측하지 않고 사용자에게 다시 묻습니다.
    values, extraction = extract_parcel_locker_request(payload.message, payload.arguments)
    missing = [name for name in ("locker_id", "code") if not getattr(values, name)]
    if missing: return result("needs_clarification", f"다음 정보를 알려주세요: {', '.join(missing)}", "needs_user_input", trace=[extraction])
    # 인증 결과는 확률적인 Agent 판단이 아니라 결정적인 Backend 검사 결과입니다.
    inspection = inspect_locker(values.locker_id, values.code)
    trace = [extraction, {"stage": "backend_authentication_policy", "data": inspection}]
    if not inspection["valid"]: return result("rejected", inspection["reason"], "policy_rejected", trace=trace)
    action = lab_repository.create_pending_action("parcel_locker", "open_locker", {"locker_id": values.locker_id, "code": values.code})
    return result("confirmation_required", "인증에 성공했습니다. 택배함 열기를 확인해 주세요.", "confirmation_required", {"pending_action_id": action["action_id"], "expires_at": action["expires_at"].isoformat()}, trace, [action])

def result(status, answer, reason, state=None, trace=None, actions=None):
    return {"status": status, "answer": answer, "state": state or {}, "trace": trace or [], "reason": reason, "calls": [{"tool": item["tool_name"], "arguments": item["arguments"]} for item in (actions or [])]}

