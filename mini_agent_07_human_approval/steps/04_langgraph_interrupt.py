"""LangGraph interrupt와 구조화된 Command(resume=...) 최소 예제."""

from operator import add
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class ApprovalState(TypedDict, total=False):
    owner_id: str
    reservation: dict
    decision: str
    decision_actor: str
    status: str
    result: str
    trace: Annotated[list[str], add]


def prepare(state: ApprovalState) -> dict:
    return {"status": "waiting_approval", "trace": ["prepare"]}


def request_approval(state: ApprovalState) -> dict:
    response = interrupt(
        {
            "question": "이 Mock 예약 요청을 승인하시겠습니까?",
            "reservation": state["reservation"],
            "allowed_actions": ["approve", "reject"],
        }
    )
    if not isinstance(response, dict) or response.get("decision") not in {"approve", "reject"}:
        raise ValueError("올바른 승인 결정이 아닙니다.")
    if response.get("actor") != state["owner_id"]:
        raise ValueError("실행 소유자만 결정할 수 있습니다.")
    return {
        "decision": response["decision"],
        "decision_actor": response["actor"],
        "trace": ["approval"],
    }


def execute_mock(state: ApprovalState) -> dict:
    if state["decision"] == "reject":
        return {"status": "rejected", "result": "사용자가 요청을 거절했습니다.", "trace": ["reject"]}
    return {"status": "completed", "result": "Mock 예약 요청이 한 번 기록되었습니다.", "trace": ["execute_mock"]}


builder = StateGraph(ApprovalState)
builder.add_node("prepare", prepare)
builder.add_node("request_approval", request_approval)
builder.add_node("execute_mock", execute_mock)
builder.add_edge(START, "prepare")
builder.add_edge("prepare", "request_approval")
builder.add_edge("request_approval", "execute_mock")
builder.add_edge("execute_mock", END)
graph = builder.compile(checkpointer=InMemorySaver())


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "approval-demo-001"}}
    initial: ApprovalState = {
        "owner_id": "user-a",
        "reservation": {"hotel": "바다 호텔", "guests": 2},
        "trace": [],
    }
    paused = graph.invoke(initial, config=config)
    print("중단 정보:", paused.get("__interrupt__"))
    resumed = graph.invoke(
        Command(resume={"decision": "approve", "actor": "user-a", "note": "확인"}),
        config=config,
    )
    print("재개 결과:", resumed)
