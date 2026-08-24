"""자연어 해석과 결정적 제어 규칙을 분리한 Agent-assisted Workflow입니다.

Agent는 현재 온도를 구조화합니다. 전원을 켜거나 끄는 판단은 LLM이 아니라 테스트
가능한 히스테리시스 규칙이 담당하며, 실제 상태 변경은 사용자 확인 뒤 Tool이 수행합니다.
"""
from app.agents.air_conditioner_agent import extract_air_conditioner_request
from app.repositories.lab_repository import lab_repository
from app.schemas.lab import LabRunRequest
from app.tools.lab_tools import control_air_conditioner

def run(payload: LabRunRequest) -> dict:
    """온도 추출 → 규칙 판단 → 필요 시 확인 → 장치 Tool 실행 순서를 제어합니다."""
    if payload.confirmed:
        # 확인된 pending action만 실행하여 Agent가 장치를 직접 제어하지 못하게 합니다.
        action = lab_repository.consume_pending_action(payload.action_id or "", "air_conditioner")
        if action is None: return _result("rejected", "유효한 확인 작업을 찾지 못했습니다.", "invalid_action")
        result = control_air_conditioner(**action["arguments"])
        return _result("completed", "에어컨 Workflow를 실행했습니다.", "completed", lab_repository.snapshot("air_conditioner"), [{"stage": "confirmed_tool_execution", "data": result}], [action])
    # Agent의 역할은 자연어에서 센서값을 읽을 수 있는 형태로 바꾸는 데 한정됩니다.
    values, extraction = extract_air_conditioner_request(payload.message, payload.arguments)
    if values.temperature_c is None: return _result("needs_clarification", "현재 온도를 알려주세요.", "needs_user_input", trace=[extraction])
    power = lab_repository.air_conditioner["power"]
    # 안전하고 반복 가능한 업무 판단은 명시적인 Backend 규칙으로 유지합니다.
    action_name = "turn_on" if values.temperature_c >= 27 and power == "off" else "turn_off" if values.temperature_c <= 23 and power == "on" else "keep"
    trace = [extraction, {"stage": "backend_hysteresis_policy", "data": {"current_power": power, "action": action_name}}]
    if action_name == "keep": return _result("completed", "현재 상태를 유지합니다.", "completed", lab_repository.snapshot("air_conditioner"), trace)
    # 상태가 실제로 바뀌는 경우에만 사용자 확인을 요구합니다.
    action = lab_repository.create_pending_action("air_conditioner", "control_air_conditioner", {"temperature_c": values.temperature_c})
    return _result("confirmation_required", f"에어컨을 {('켜기' if action_name == 'turn_on' else '끄기')} 전에 확인해 주세요.", "confirmation_required", {"pending_action_id": action["action_id"], "expires_at": action["expires_at"].isoformat()}, trace, [action])

def _result(status, answer, reason, state=None, trace=None, actions=None):
    return {"status": status, "answer": answer, "state": state or {}, "trace": trace or [], "reason": reason, "calls": [{"tool": item["tool_name"], "arguments": item["arguments"]} for item in (actions or [])]}

