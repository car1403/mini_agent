"""승인 후 Mock 변경 작업을 run_id별로 한 번만 실행합니다."""


PROCESSED_RUNS: set[str] = set()
AUDIT_LOG: list[dict] = []


def execute_once(run_id: str, owner_id: str, decision: dict) -> dict:
    if decision.get("actor") != owner_id:
        return {"status": "blocked", "reason": "실행 소유자가 아님"}
    if decision.get("decision") != "approve":
        return {"status": "rejected", "reason": "승인되지 않음"}
    if run_id in PROCESSED_RUNS:
        return {"status": "already_processed", "run_id": run_id}

    # 실제 변경 작업은 모든 검사와 승인 이후에 둡니다.
    PROCESSED_RUNS.add(run_id)
    event = {"run_id": run_id, "actor": decision["actor"], "action": "create_mock_reservation"}
    AUDIT_LOG.append(event)
    return {"status": "completed", "event": event}


if __name__ == "__main__":
    approved = {"decision": "approve", "actor": "user-a"}
    print("첫 실행:", execute_once("run-001", "user-a", approved))
    print("중복 실행:", execute_once("run-001", "user-a", approved))
    print("다른 사용자:", execute_once("run-002", "user-a", {"decision": "approve", "actor": "user-b"}))
    print("감사 로그:", AUDIT_LOG)
