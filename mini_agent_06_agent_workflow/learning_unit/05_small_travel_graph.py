"""앞에서 배운 State, Node, Edge, 조건 분기를 실제 LangGraph로 연결합니다."""

from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class TravelState(TypedDict, total=False):
    message: str
    destination: str | None
    status: str
    answer: str
    trace: list[str]


def extract(state: TravelState) -> dict:
    destination = "부산" if "부산" in state["message"] else None
    return {"destination": destination, "trace": ["extract"]}


def route(state: TravelState) -> Literal["ask_user", "create_plan"]:
    return "create_plan" if state.get("destination") else "ask_user"


def ask_user(state: TravelState) -> dict:
    return {"status": "needs_input", "answer": "어느 도시로 여행할까요?", "trace": [*state["trace"], "ask_user"]}


def create_plan(state: TravelState) -> dict:
    return {"status": "completed", "answer": f"{state['destination']} 2박 3일 Mock 일정을 만들었습니다.", "trace": [*state["trace"], "create_plan"]}


builder = StateGraph(TravelState)
builder.add_node("extract", extract)
builder.add_node("ask_user", ask_user)
builder.add_node("create_plan", create_plan)
builder.add_edge(START, "extract")
builder.add_conditional_edges("extract", route)
builder.add_edge("ask_user", END)
builder.add_edge("create_plan", END)
graph = builder.compile()


if __name__ == "__main__":
    print("Graph 구조 (Mermaid):")
    print(graph.get_graph().draw_mermaid())
    for message in ("부산 여행을 준비해줘", "여행을 준비해줘"):
        print(message, "→", graph.invoke({"message": message, "trace": []}))
