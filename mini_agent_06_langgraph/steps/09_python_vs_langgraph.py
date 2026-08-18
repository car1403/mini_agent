"""같은 분기 흐름을 일반 Python과 LangGraph로 각각 구현해 비교합니다."""

from operator import add
from typing import Annotated, Literal, TypedDict

from langgraph.graph import END, START, StateGraph


def find_destination(message: str) -> str | None:
    return next((city for city in ("서울", "부산", "제주") if city in message), None)


def python_workflow(message: str) -> dict:
    destination = find_destination(message)
    trace = ["extract"]
    if destination is None:
        return {"status": "needs_input", "answer": "어느 도시로 여행할까요?", "trace": [*trace, "ask_user"]}
    return {
        "status": "completed",
        "answer": f"{destination} Mock 일정을 만들었습니다.",
        "trace": [*trace, "create_plan"],
    }


class TravelState(TypedDict, total=False):
    message: str
    destination: str | None
    status: str
    answer: str
    trace: Annotated[list[str], add]


def extract(state: TravelState) -> dict:
    return {"destination": find_destination(state["message"]), "trace": ["extract"]}


def route(state: TravelState) -> Literal["ask_user", "create_plan"]:
    return "create_plan" if state.get("destination") else "ask_user"


def ask_user(state: TravelState) -> dict:
    return {"status": "needs_input", "answer": "어느 도시로 여행할까요?", "trace": ["ask_user"]}


def create_plan(state: TravelState) -> dict:
    return {
        "status": "completed",
        "answer": f"{state['destination']} Mock 일정을 만들었습니다.",
        "trace": ["create_plan"],
    }


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
    for message in ("부산 여행을 준비해줘", "여행을 준비해줘"):
        python_result = python_workflow(message)
        graph_result = graph.invoke({"message": message, "trace": []})
        graph_summary = {key: graph_result[key] for key in ("status", "answer", "trace")}
        print("입력:", message)
        print("일반 Python:", python_result)
        print("LangGraph:", graph_summary)
        print("같은 결과인가?", python_result == graph_summary)
