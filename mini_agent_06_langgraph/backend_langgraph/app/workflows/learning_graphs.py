from operator import add
from typing import Annotated, Literal, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class BranchState(TypedDict, total=False):
    message: str
    destination: str | None
    status: str
    answer: str
    trace: Annotated[list[str], add]


def extract(state: BranchState) -> dict:
    destination = next((city for city in ("서울", "부산", "제주") if city in state["message"]), None)
    return {"destination": destination, "trace": ["extract"]}


def branch_route(state: BranchState) -> Literal["ask_user", "create_plan"]:
    return "create_plan" if state.get("destination") else "ask_user"


def ask_user(state: BranchState) -> dict:
    return {"status": "needs_input", "answer": "어느 도시로 여행할까요?", "trace": ["ask_user"]}


def create_plan(state: BranchState) -> dict:
    return {"status": "completed", "answer": f"{state['destination']} 2박 3일 Mock 일정을 만들었습니다.", "trace": ["create_plan"]}


branch_builder = StateGraph(BranchState)
branch_builder.add_node("extract", extract)
branch_builder.add_node("ask_user", ask_user)
branch_builder.add_node("create_plan", create_plan)
branch_builder.add_edge(START, "extract")
branch_builder.add_conditional_edges("extract", branch_route)
branch_builder.add_edge("ask_user", END)
branch_builder.add_edge("create_plan", END)
branch_graph = branch_builder.compile()


class LoopState(TypedDict, total=False):
    budget: int
    estimated_budget: int
    iteration: int
    max_iterations: int
    status: str
    trace: Annotated[list[str], add]


def make_draft(state: LoopState) -> dict:
    daily_budget = 170000 if state["iteration"] == 0 else 110000
    return {"estimated_budget": daily_budget * 3, "trace": [f"create_plan:{state['iteration']}"]}


def loop_route(state: LoopState) -> Literal["finish", "revise", "fail"]:
    if state["estimated_budget"] <= state["budget"]:
        return "finish"
    return "revise" if state["iteration"] < state["max_iterations"] else "fail"


def revise(state: LoopState) -> dict:
    return {"iteration": state["iteration"] + 1, "trace": ["revise"]}


def finish(state: LoopState) -> dict:
    return {"status": "completed", "trace": ["finish"]}


def fail(state: LoopState) -> dict:
    return {"status": "failed", "trace": ["fail"]}


loop_builder = StateGraph(LoopState)
for name, node in {"create_plan": make_draft, "revise": revise, "finish": finish, "fail": fail}.items():
    loop_builder.add_node(name, node)
loop_builder.add_edge(START, "create_plan")
loop_builder.add_conditional_edges("create_plan", loop_route)
loop_builder.add_edge("revise", "create_plan")
loop_builder.add_edge("finish", END)
loop_builder.add_edge("fail", END)
loop_graph = loop_builder.compile()


class VisitState(TypedDict, total=False):
    visits: int


def count_visit(state: VisitState) -> dict:
    return {"visits": state.get("visits", 0) + 1}


checkpoint_builder = StateGraph(VisitState)
checkpoint_builder.add_node("count_visit", count_visit)
checkpoint_builder.add_edge(START, "count_visit")
checkpoint_builder.add_edge("count_visit", END)
checkpoint_graph = checkpoint_builder.compile(checkpointer=InMemorySaver())


def graph_components() -> dict:
    return {
        "state": "Node들이 함께 사용하는 데이터",
        "node": "State를 받고 변경할 값을 반환하는 함수",
        "edge": "다음 Node를 연결하는 선",
        "conditional_edge": "State를 보고 다음 경로를 선택하는 분기",
        "reducer": "여러 Node가 반환한 값을 교체할지 누적할지 정하는 규칙",
        "flow": "START → extract → ask_user 또는 create_plan → END",
        "mermaid": branch_graph.get_graph().draw_mermaid(),
    }


def run_branch(message: str) -> dict:
    return branch_graph.invoke({"message": message, "trace": []})


def run_loop(budget: int, max_iterations: int) -> dict:
    return loop_graph.invoke({"budget": budget, "iteration": 0, "max_iterations": max_iterations, "trace": []})


def run_checkpoint(thread_id: str) -> dict:
    config = {"configurable": {"thread_id": thread_id}}
    current = checkpoint_graph.get_state(config).values
    result = checkpoint_graph.invoke({} if current else {"visits": 0}, config=config)
    history = list(checkpoint_graph.get_state_history(config))
    return {"thread_id": thread_id, "state": result, "checkpoint_count": len(history), "storage": "InMemorySaver"}


def python_workflow(message: str) -> dict:
    destination = next((city for city in ("서울", "부산", "제주") if city in message), None)
    if destination is None:
        return {"status": "needs_input", "answer": "어느 도시로 여행할까요?"}
    return {"status": "completed", "answer": f"{destination} 2박 3일 Mock 일정을 만들었습니다."}


def compare_workflows(message: str) -> dict:
    graph_result = run_branch(message)
    return {
        "python": python_workflow(message),
        "langgraph": {"status": graph_result["status"], "answer": graph_result["answer"], "trace": graph_result["trace"]},
        "note": "결과는 같고 LangGraph는 State와 실행 경로를 확인하기 쉽습니다.",
    }
