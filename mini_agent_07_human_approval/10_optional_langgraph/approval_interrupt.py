"""LangGraph의 interrupt/resume을 보여주는 선택 학습 예제입니다."""

from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class State(TypedDict, total=False):
    actor_id: str
    approval_target: dict
    status: str
    result: dict


def approval_node(state: State):
    decision = interrupt(
        {
            "question": "이 주문을 생성할까요?",
            "approval_target": state["approval_target"],
            "allowed_decisions": ["approve", "reject"],
        }
    )
    if decision.get("actor_id") != state["actor_id"]:
        return {"status": "blocked"}
    if decision.get("approval_target") != state["approval_target"]:
        return {"status": "blocked"}
    if decision.get("decision") == "reject":
        return {"status": "rejected"}
    if decision.get("decision") != "approve":
        return {"status": "blocked"}
    return {"status": "completed", "result": {"saved": True, **state["approval_target"]}}


builder = StateGraph(State)
builder.add_node("approval", approval_node)
builder.add_edge(START, "approval")
builder.add_edge("approval", END)
graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "approval-demo-001"}}
target = {"tool": "place_order", "arguments": {"product_id": "P-KEYBOARD", "quantity": 2}}
paused = graph.invoke({"actor_id": "user-01", "approval_target": target}, config=config)
print("중단:", paused["__interrupt__"])

resumed = graph.invoke(
    Command(resume={"decision": "approve", "actor_id": "user-01", "approval_target": target}),
    config=config,
)
print("재개:", resumed)
