"""검증 실패 시 수정하되 max_iterations에서 반드시 종료합니다."""

from operator import add
from typing import Annotated, Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class BudgetState(TypedDict, total=False):
    budget: int
    estimated_budget: int
    iteration: int
    max_iterations: int
    status: str
    trace: Annotated[list[str], add]


def create_plan(state: BudgetState) -> dict:
    daily_budget = 170000 if state["iteration"] == 0 else 110000
    return {"estimated_budget": daily_budget * 3, "trace": [f"create_plan:{state['iteration']}"]}


def route_after_validation(state: BudgetState) -> Literal["finish", "revise", "fail"]:
    if state["estimated_budget"] <= state["budget"]:
        return "finish"
    if state["iteration"] < state["max_iterations"]:
        return "revise"
    return "fail"


def revise(state: BudgetState) -> dict:
    return {"iteration": state["iteration"] + 1, "trace": ["revise"]}


def finish(state: BudgetState) -> dict:
    return {"status": "completed", "trace": ["finish"]}


def fail(state: BudgetState) -> dict:
    return {"status": "failed", "trace": ["fail"]}


builder = StateGraph(BudgetState)
for name, node in {"create_plan": create_plan, "revise": revise, "finish": finish, "fail": fail}.items():
    builder.add_node(name, node)
builder.add_edge(START, "create_plan")
builder.add_conditional_edges("create_plan", route_after_validation)
builder.add_edge("revise", "create_plan")
builder.add_edge("finish", END)
builder.add_edge("fail", END)
graph = builder.compile()


if __name__ == "__main__":
    for budget in (400000, 200000):
        initial: BudgetState = {"budget": budget, "iteration": 0, "max_iterations": 1, "trace": []}
        print(f"budget={budget} →", graph.invoke(initial))
