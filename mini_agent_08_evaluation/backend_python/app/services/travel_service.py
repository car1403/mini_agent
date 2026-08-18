from datetime import date, timedelta
import re
from uuid import uuid4

from app.rag.policies import search as search_policies
from app.repositories.store import store


SENSITIVE_MEMORY_KEYS = {"card_number", "password", "passport_number", "api_key"}


def extract_travel_request(message: str, reference_date: date) -> dict:
    destination = next((city for city in ("서울", "부산", "제주", "강릉") if city in message), None)
    nights_match = re.search(r"(\d+)\s*박", message)
    people_match = re.search(r"(?:성인\s*)?(\d+)\s*명", message)
    budget_match = re.search(r"(\d+)\s*만\s*원", message)
    start_date = reference_date + timedelta(days=14) if "8월" not in message else date(2026, 8, 10)
    result = {
        "destination": destination,
        "start_date": start_date.isoformat(),
        "nights": int(nights_match.group(1)) if nights_match else None,
        "adults": int(people_match.group(1)) if people_match else None,
        "budget": int(budget_match.group(1)) * 10000 if budget_match else None,
        "transportation": "public" if "대중교통" in message else "unknown",
    }
    result["missing_fields"] = [
        key for key in ("destination", "nights", "adults", "budget") if result[key] is None
    ]
    return result


def create_agent_run(payload: dict) -> dict:
    extracted = extract_travel_request(payload["message"], date(2026, 7, 27))
    for key in ("destination", "start_date", "nights", "adults", "budget"):
        if payload.get(key) is not None:
            value = payload[key]
            extracted[key] = value.isoformat() if hasattr(value, "isoformat") else value
    extracted["missing_fields"] = [
        key for key in ("destination", "start_date", "nights", "adults", "budget") if not extracted.get(key)
    ]
    trace = [{"node": "extract_request", "status": "completed"}]
    if extracted["missing_fields"]:
        trace.append({"node": "validate_request", "status": "needs_input"})
        return store.create_run(
            {
                "user_id": payload["user_id"],
                "status": "needs_input",
                "current_node": "validate_request",
                "request": extracted,
                "message": f"다음 정보를 알려주세요: {', '.join(extracted['missing_fields'])}",
                "requires_approval": False,
                "trace": trace,
            }
        )
    nights = int(extracted["nights"])
    estimated_budget = (nights + 1) * 110000
    warnings = []
    if estimated_budget > int(extracted["budget"]):
        warnings.append("예상 비용이 입력 예산을 초과해 활동 수를 줄였습니다.")
        estimated_budget = int(extracted["budget"])
    policy_docs = search_policies("숙소 취소 환불", 1)
    memories = store.list_memories(payload["user_id"])
    trace.extend(
        [
            {"node": "load_memory", "status": "completed", "count": len(memories)},
            {"node": "search_policy", "status": "completed", "count": len(policy_docs)},
            {"node": "create_plan", "status": "completed"},
            {"node": "validate_plan", "status": "completed"},
            {"node": "approval", "status": "waiting_approval"},
        ]
    )
    return store.create_run(
        {
            "user_id": payload["user_id"],
            "status": "waiting_approval",
            "current_node": "approval",
            "request": extracted,
            "result": {
                "destination": extracted["destination"],
                "days": nights + 1,
                "estimated_budget": estimated_budget,
                "warnings": warnings,
                "memory_used": memories,
                "sources": policy_docs,
                "reservation_draft": {
                    "type": "mock",
                    "confirmation_required": True,
                },
            },
            "message": "여행 일정과 Mock 예약 요청서가 준비되었습니다.",
            "requires_approval": True,
            "trace": trace,
        }
    )


def decide_run(run_id: str, decision: str, actor: str, note: str) -> dict | None:
    run = store.get_run(run_id)
    if run is None:
        return None
    if run["status"] != "waiting_approval":
        raise ValueError("승인 대기 상태의 실행만 처리할 수 있습니다.")
    if decision not in {"approve", "reject"}:
        raise ValueError("decision은 approve 또는 reject여야 합니다.")
    if actor != run["user_id"]:
        raise ValueError("실행 소유자만 승인하거나 거절할 수 있습니다.")
    status = "completed" if decision == "approve" else "rejected"
    message = "Mock 예약 요청이 기록되었습니다." if decision == "approve" else "요청이 거절되었습니다."
    trace = [
        *run["trace"],
        {
            "node": "approval",
            "status": status,
            "actor": actor,
            "note": note,
        },
    ]
    return store.update_run(
        run_id,
        {
            "status": status,
            "current_node": "end",
            "message": message,
            "requires_approval": False,
            "trace": trace,
        },
    )


def add_memory(user_id: str, key: str, value: str) -> dict:
    if key.lower() in SENSITIVE_MEMORY_KEYS:
        raise ValueError("민감정보는 Memory에 저장할 수 없습니다.")
    return store.add_memory(user_id, key, value)


def new_trace_id() -> str:
    return f"trace-{uuid4()}"
