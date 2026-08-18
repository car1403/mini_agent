"""일반 Python으로 중단, 상태 저장, 재개를 구분합니다."""


ALLOWED_DECISIONS = {"approve", "reject"}


def pause(run_id: str, owner_id: str, draft: dict) -> dict:
    return {
        "run_id": run_id,
        "owner_id": owner_id,
        "status": "waiting_approval",
        "current_node": "approval",
        "draft": draft,
    }


def resume(saved_state: dict, command: dict) -> dict:
    if saved_state["status"] != "waiting_approval":
        raise ValueError("승인 대기 상태만 재개할 수 있습니다.")
    if command.get("decision") not in ALLOWED_DECISIONS:
        raise ValueError("decision은 approve 또는 reject여야 합니다.")
    if command.get("actor") != saved_state["owner_id"]:
        raise ValueError("실행 소유자만 결정할 수 있습니다.")
    approved = command["decision"] == "approve"
    return {
        **saved_state,
        "status": "completed" if approved else "rejected",
        "current_node": "end",
        "decision": command["decision"],
        "decision_actor": command["actor"],
    }


if __name__ == "__main__":
    saved = pause("run-001", "user-a", {"action": "create_mock_reservation"})
    print("저장된 상태:", saved)
    print("승인 재개:", resume(saved, {"decision": "approve", "actor": "user-a"}))
    print("거절 재개:", resume(saved, {"decision": "reject", "actor": "user-a"}))
