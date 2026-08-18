"""Reducer는 여러 Node가 반환한 값을 교체할지 누적할지 정합니다."""

from operator import add
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


class TraceState(TypedDict, total=False):
    message: str
    trace: Annotated[list[str], add]


def extract(state: TraceState) -> dict:
    return {"trace": ["extract"]}


def create_plan(state: TraceState) -> dict:
    return {"trace": ["create_plan"]}


builder = StateGraph(TraceState)
builder.add_node("extract", extract)
builder.add_node("create_plan", create_plan)
builder.add_edge(START, "extract")
builder.add_edge("extract", "create_plan")
builder.add_edge("create_plan", END)
graph = builder.compile()


if __name__ == "__main__":
    replaced = {"trace": ["extract"]}
    replaced.update({"trace": ["create_plan"]})
    print("일반 dict.update 결과:", replaced["trace"])

    result = graph.invoke({"message": "부산 여행", "trace": []})
    print("Reducer로 누적한 결과:", result["trace"])
    print("Node는 새 항목만 반환하고 Reducer가 기존 목록에 더합니다.")
