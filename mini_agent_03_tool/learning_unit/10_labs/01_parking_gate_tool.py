"""Lab 01 — 가상 차량 DB를 조회하고 승인된 차량에만 주차장 문을 엽니다.

학습 분류:
- 현재 성격: Tool + 승인 Workflow
- Agent 여부: 아니오
- 권장 방향: 안전한 상태 변경 Workflow로 유지
- 판단 근거: 조회 → 서버 승인 → 문 열기 순서와 정책이 고정되어 있습니다. LLM은
  차량 번호 추출을 도울 수 있지만 출입 승인이나 물리 장치 실행을 결정하면 안 됩니다.

Backend 디렉터리 기준 역할:
- `schemas/`: VehicleLookupInput, OpenGateInput이 Tool 입력 계약을 정의합니다.
- `tools/`: lookup_vehicle과 open_gate가 조회·물리 동작 Tool 역할을 합니다.
- `services/`: authorize_entry가 출입 정책을 적용하고 run_parking_entry가 고정 Workflow를 조정합니다.
- `agents/`: 다음 행동을 동적으로 선택하지 않으므로 별도 Agent를 사용하지 않습니다.
- `routers/`: 이 파일에서는 `__main__` 실행부가 사용자 요청 진입점을 대신합니다.
- `providers/`: LLM 호출이 없는 규칙 기반 실습이므로 사용하지 않습니다.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError


# [schemas/] 차량 조회 Tool에 전달할 arguments를 검증하는 입력 Schema입니다.
class VehicleLookupInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    plate_number: str = Field(min_length=4, description="조회할 차량 번호")


# [schemas/] 문 열기 Tool에 전달할 서버 발급 승인 ID를 검증합니다.
class OpenGateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    authorization_id: str = Field(min_length=1, description="서버가 발급한 출입 승인 ID")


# [학습용 저장소] 실제 Backend에서는 DB 또는 repositories/ 계층으로 분리할 상태입니다.
VEHICLE_DATABASE = {
    "12가3456": {"owner": "김민준", "active": True},
    "34나7890": {"owner": "이서연", "active": False},
}
AUTHORIZATIONS: dict[str, str] = {}
GATE_STATE = {"is_open": False}


# [tools/] 차량 번호를 조회하고 실행에 필요한 사실만 Tool Result로 반환합니다.
def lookup_vehicle(arguments: dict[str, Any]) -> dict[str, Any]:
    args = VehicleLookupInput.model_validate(arguments)
    vehicle = VEHICLE_DATABASE.get(args.plate_number)
    return {
        "plate_number": args.plate_number,
        "registered": vehicle is not None,
        "active": bool(vehicle and vehicle["active"]),
    }


# [services/] 조회 결과에 서버 소유의 출입 허용 정책을 적용합니다.
def authorize_entry(lookup_result: dict[str, Any]) -> dict[str, Any]:
    """LLM이 아니라 서버 정책이 출입 가능 여부를 결정합니다."""
    if not lookup_result["registered"]:
        return {"authorized": False, "reason": "등록되지 않은 차량입니다."}
    if not lookup_result["active"]:
        return {"authorized": False, "reason": "출입 권한이 비활성 상태입니다."}
    authorization_id = f"entry:{lookup_result['plate_number']}"
    AUTHORIZATIONS[authorization_id] = lookup_result["plate_number"]
    return {"authorized": True, "authorization_id": authorization_id}


# [tools/] 유효한 일회성 승인 ID가 있을 때만 실제 문 상태를 변경합니다.
def open_gate(arguments: dict[str, Any]) -> dict[str, Any]:
    args = OpenGateInput.model_validate(arguments)
    plate_number = AUTHORIZATIONS.pop(args.authorization_id, None)
    if plate_number is None:
        return {"opened": False, "reason": "유효하지 않거나 이미 사용된 승인 ID입니다."}
    GATE_STATE["is_open"] = True
    return {"opened": True, "plate_number": plate_number}


# [services/] Tool 호출 순서가 정해진 주차장 입장 Workflow를 조정합니다.
def run_parking_entry(user_message: str) -> dict[str, Any]:
    """Mock LLM이 메시지에서 차량 번호만 추출했다고 가정한 전체 흐름입니다."""
    plate_number = next((word for word in user_message.split() if any(char.isdigit() for char in word)), None)
    if plate_number is None:
        return {"final_answer": "차량 번호를 입력해 주세요.", "trace": []}
    trace: list[dict[str, Any]] = []
    try:
        lookup_result = lookup_vehicle({"plate_number": plate_number})
        trace.append({"stage": "lookup_vehicle", "data": lookup_result})
        decision = authorize_entry(lookup_result)
        trace.append({"stage": "backend_policy", "data": decision})
        if not decision["authorized"]:
            return {"final_answer": f"문을 열 수 없습니다. {decision['reason']}", "trace": trace}
        gate_result = open_gate({"authorization_id": decision["authorization_id"]})
        trace.append({"stage": "open_gate", "data": gate_result})
        answer = "등록 차량을 확인하여 주차장 문을 열었습니다." if gate_result["opened"] else gate_result["reason"]
        return {"final_answer": answer, "trace": trace}
    except ValidationError as error:
        return {"final_answer": "차량 번호 형식이 올바르지 않습니다.", "trace": trace, "error": error.errors()}


# [routers/ 대체] API 대신 여러 사용자 요청을 넣어 전체 결과와 Trace를 확인합니다.
if __name__ == "__main__":
    for message in ("차량 12가3456 문 열어줘", "차량 34나7890 문 열어줘", "차량 99다9999 문 열어줘"):
        result = run_parking_entry(message)
        print(f"\n사용자: {message}")
        for item in result["trace"]:
            print(f"- {item['stage']}: {item['data']}")
        print("최종 답변:", result["final_answer"])
