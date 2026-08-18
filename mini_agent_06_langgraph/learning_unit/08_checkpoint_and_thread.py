"""InMemorySaver와 thread_id로 같은 프로세스 안에서 State를 저장합니다."""

from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class VisitState(TypedDict, total=False):
    visits: int


def count_visit(state: VisitState) -> dict:
    return {"visits": state.get("visits", 0) + 1}


builder = StateGraph(VisitState)
builder.add_node("count_visit", count_visit)
builder.add_edge(START, "count_visit")
builder.add_edge("count_visit", END)
graph = builder.compile(checkpointer=InMemorySaver())


if __name__ == "__main__":
    config_a = {"configurable": {"thread_id": "travel-a"}}
    config_b = {"configurable": {"thread_id": "travel-b"}}
    print("A 첫 실행:", graph.invoke({}, config=config_a))
    print("A 두 번째 실행:", graph.invoke({}, config=config_a))
    print("B 첫 실행:", graph.invoke({}, config=config_b))
    print("A 최신 State:", graph.get_state(config_a).values)
    print("A Checkpoint 수:", len(list(graph.get_state_history(config_a))))
    print("주의: InMemorySaver는 프로세스를 재시작하면 사라집니다.")
