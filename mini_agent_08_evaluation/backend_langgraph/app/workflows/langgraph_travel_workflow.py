from datetime import date
from operator import add
from typing import Annotated, Any, Literal, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from app.rag.policies import search as search_policies
from app.repositories.store import store
from app.services.travel_service import extract_travel_request


class TravelAgentState(TypedDict, total=False):
    user_id: str
    message: str
    destination: str | None
    start_date: str | None
    nights: int | None
    adults: int | None
    budget: int | None
    request: dict[str, Any]
    memories: list[dict]
    policy_docs: list[dict]
    result: dict[str, Any]
    status: str
    current_node: str
    message_to_user: str
    requires_approval: bool
    trace: Annotated[list[dict], add]
    decision: str
    decision_actor: str
    decision_note: str


def extract_request_node(state: TravelAgentState) -> dict:
    request = extract_travel_request(state["message"], date(2026, 7, 27))
    for key in ("destination", "start_date", "nights", "adults", "budget"):
        if state.get(key) is not None:
            request[key] = state[key]
    request["missing_fields"] = [
        key
        for key in ("destination", "start_date", "nights", "adults", "budget")
        if not request.get(key)
    ]
    return {
        "request": request,
        "current_node": "extract_request",
        "trace": [{"node": "extract_request", "status": "completed"}],
    }


def route_after_validation(state: TravelAgentState) -> Literal["needs_input", "load_context"]:
    return "needs_input" if state["request"]["missing_fields"] else "load_context"


def needs_input_node(state: TravelAgentState) -> dict:
    missing = ", ".join(state["request"]["missing_fields"])
    return {
        "status": "needs_input",
        "current_node": "validate_request",
        "message_to_user": f"다음 정보를 알려주세요: {missing}",
        "requires_approval": False,
        "trace": [
            {"node": "validate_request", "status": "needs_input"},
        ],
    }


def load_context_node(state: TravelAgentState) -> dict:
    memories = store.list_memories(state["user_id"])
    policy_docs = search_policies("숙소 취소 환불", 1)
    return {
        "memories": memories,
        "policy_docs": policy_docs,
        "current_node": "load_context",
        "trace": [
            {"node": "validate_request", "status": "completed"},
            {"node": "load_memory", "status": "completed", "count": len(memories)},
            {"node": "search_policy", "status": "completed", "count": len(policy_docs)},
        ],
    }


def create_plan_node(state: TravelAgentState) -> dict:
    request = state["request"]
    nights = int(request["nights"])
    estimated_budget = min((nights + 1) * 110000, int(request["budget"]))
    warnings = []
    if (nights + 1) * 110000 > int(request["budget"]):
        warnings.append("예상 비용이 입력 예산을 초과해 활동 수를 줄였습니다.")
    return {
        "result": {
            "destination": request["destination"],
            "days": nights + 1,
            "estimated_budget": estimated_budget,
            "warnings": warnings,
            "memory_used": state["memories"],
            "sources": state["policy_docs"],
            "reservation_draft": {
                "type": "mock",
                "confirmation_required": True,
            },
        },
        "current_node": "create_plan",
        "trace": [
            {"node": "create_plan", "status": "completed"},
            {"node": "validate_plan", "status": "completed"},
        ],
    }


def approval_node(state: TravelAgentState) -> dict:
    decision = interrupt(
        {
            "question": "교육용 Mock 예약 초안을 승인하시겠습니까?",
            "reservation_draft": state["result"]["reservation_draft"],
        }
    )
    if not isinstance(decision, dict):
        raise ValueError("승인 결정은 구조화된 데이터여야 합니다.")
    if decision.get("decision") not in {"approve", "reject"}:
        raise ValueError("decision은 approve 또는 reject여야 합니다.")
    if decision.get("actor") != state["user_id"]:
        raise ValueError("실행 소유자만 승인하거나 거절할 수 있습니다.")

    approved = decision["decision"] == "approve"
    status = "completed" if approved else "rejected"
    return {
        "decision": decision["decision"],
        "decision_actor": decision.get("actor", "demo-user"),
        "decision_note": decision.get("note", ""),
        "status": status,
        "current_node": "end",
        "requires_approval": False,
        "message_to_user": (
            "Mock 예약 요청이 기록되었습니다."
            if approved
            else "요청이 거절되었습니다."
        ),
        "trace": [
            {
                "node": "approval",
                "status": status,
                "actor": decision.get("actor", "demo-user"),
                "note": decision.get("note", ""),
            },
        ],
    }


builder = StateGraph(TravelAgentState)
builder.add_node("extract_request", extract_request_node)
builder.add_node("needs_input", needs_input_node)
builder.add_node("load_context", load_context_node)
builder.add_node("create_plan", create_plan_node)
builder.add_node("approval", approval_node)
builder.add_edge(START, "extract_request")
builder.add_conditional_edges("extract_request", route_after_validation)
builder.add_edge("needs_input", END)
builder.add_edge("load_context", "create_plan")
builder.add_edge("create_plan", "approval")
builder.add_edge("approval", END)

# 교육 단계에서는 메모리 Checkpointer를 사용합니다.
# 운영/다중 프로세스 단계에서는 PostgreSQL 또는 Redis Checkpointer로 교체합니다.
graph = builder.compile(checkpointer=InMemorySaver())


def _config(run_id: str) -> dict:
    return {"configurable": {"thread_id": run_id}}


def _public_state(run_id: str, state: dict) -> dict:
    waiting = bool(state.get("__interrupt__"))
    return {
        "run_id": run_id,
        "user_id": state["user_id"],
        "status": "waiting_approval" if waiting else state.get("status", "completed"),
        "current_node": "approval" if waiting else state.get("current_node", "end"),
        "request": state.get("request", {}),
        "result": state.get("result"),
        "message": (
            "여행 일정과 Mock 예약 요청서가 준비되었습니다."
            if waiting
            else state.get("message_to_user", "")
        ),
        "requires_approval": waiting,
        "trace": (
            [
                *state.get("trace", []),
                {"node": "approval", "status": "waiting_approval"},
            ]
            if waiting
            else state.get("trace", [])
        ),
    }


def start_langgraph_run(payload: dict) -> dict:
    placeholder = store.create_run(
        {
            "user_id": payload["user_id"],
            "status": "running",
            "current_node": "start",
            "request": {},
            "result": None,
            "message": "",
            "requires_approval": False,
            "trace": [],
        }
    )
    run_id = placeholder["run_id"]
    state = graph.invoke(payload, config=_config(run_id))
    public = _public_state(run_id, state)
    return store.update_run(run_id, public) or public


def resume_langgraph_run(
    run_id: str,
    decision: str,
    actor: str,
    note: str,
) -> dict | None:
    saved = store.get_run(run_id)
    if saved is None:
        return None
    if saved["status"] != "waiting_approval":
        raise ValueError("승인 대기 상태의 실행만 처리할 수 있습니다.")
    if decision not in {"approve", "reject"}:
        raise ValueError("decision은 approve 또는 reject여야 합니다.")
    if actor != saved["user_id"]:
        raise ValueError("실행 소유자만 승인하거나 거절할 수 있습니다.")
    state = graph.invoke(
        Command(resume={"decision": decision, "actor": actor, "note": note}),
        config=_config(run_id),
    )
    public = _public_state(run_id, state)
    return store.update_run(run_id, public) or public
