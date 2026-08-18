"""승인, 거절, 잘못된 결정값을 같은 검증 함수로 처리합니다."""


def validate_decision(payload: object, owner_id: str) -> dict:
    if not isinstance(payload, dict):
        return {"valid": False, "reason": "결정은 dict여야 합니다."}
    if payload.get("decision") not in {"approve", "reject"}:
        return {"valid": False, "reason": "허용되지 않은 decision"}
    if payload.get("actor") != owner_id:
        return {"valid": False, "reason": "실행 소유자가 아님"}
    return {"valid": True, "decision": payload["decision"], "actor": payload["actor"]}


if __name__ == "__main__":
    cases = [
        {"decision": "approve", "actor": "user-a"},
        {"decision": "reject", "actor": "user-a"},
        {"decision": "edit", "actor": "user-a"},
        {"decision": "approve", "actor": "user-b"},
        "approve",
    ]
    for case in cases:
        print(case, "→", validate_decision(case, owner_id="user-a"))
