"""가상 차량 DB를 조회하고, 서버 정책을 통과한 차량에만 주차장 문을 엽니다."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class VehicleLookupInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    plate_number: str = Field(min_length=4, description="조회할 차량 번호")


class OpenGateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    authorization_id: str = Field(min_length=1, description="서버가 발급한 출입 승인 ID")


VEHICLE_DATABASE = {
    "12가3456": {"owner": "김민준", "active": True},
    "34나7890": {"owner": "이서연", "active": False},
}
AUTHORIZATIONS: dict[str, str] = {}
GATE_STATE = {"is_open": False}


def lookup_vehicle(arguments: dict[str, Any]) -> dict[str, Any]:
    args = VehicleLookupInput.model_validate(arguments)
    vehicle = VEHICLE_DATABASE.get(args.plate_number)
    return {
        "plate_number": args.plate_number,
        "registered": vehicle is not None,
        "active": bool(vehicle and vehicle["active"]),
    }


def authorize_entry(lookup_result: dict[str, Any]) -> dict[str, Any]:
    """LLM이 아니라 서버 정책이 출입 가능 여부를 결정합니다."""
    if not lookup_result["registered"]:
        return {"authorized": False, "reason": "등록되지 않은 차량입니다."}
    if not lookup_result["active"]:
        return {"authorized": False, "reason": "출입 권한이 비활성 상태입니다."}
    authorization_id = f"entry:{lookup_result['plate_number']}"
    AUTHORIZATIONS[authorization_id] = lookup_result["plate_number"]
    return {"authorized": True, "authorization_id": authorization_id}


def open_gate(arguments: dict[str, Any]) -> dict[str, Any]:
    args = OpenGateInput.model_validate(arguments)
    plate_number = AUTHORIZATIONS.pop(args.authorization_id, None)
    if plate_number is None:
        return {"opened": False, "reason": "유효하지 않거나 이미 사용된 승인 ID입니다."}
    GATE_STATE["is_open"] = True
    return {"opened": True, "plate_number": plate_number}


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


if __name__ == "__main__":
    for message in ("차량 12가3456 문 열어줘", "차량 34나7890 문 열어줘", "차량 99다9999 문 열어줘"):
        result = run_parking_entry(message)
        print(f"\n사용자: {message}")
        for item in result["trace"]:
            print(f"- {item['stage']}: {item['data']}")
        print("최종 답변:", result["final_answer"])
