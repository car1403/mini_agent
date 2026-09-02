from core.api_client import request
from core.config import LANGGRAPH_AGENT_API_URL


def get_graph_components():
    return request("GET", "/api/learning/graph/components", base_url=LANGGRAPH_AGENT_API_URL)


def run_branch(message: str):
    return request("POST", "/api/learning/graph/branch", {"message": message}, LANGGRAPH_AGENT_API_URL)


def run_loop(budget: int, max_iterations: int):
    payload = {"budget": budget, "max_iterations": max_iterations}
    return request("POST", "/api/learning/graph/loop", payload, LANGGRAPH_AGENT_API_URL)


def run_checkpoint(thread_id: str):
    return request("POST", "/api/learning/graph/checkpoint", {"thread_id": thread_id}, LANGGRAPH_AGENT_API_URL)


def compare_workflows(message: str):
    return request("POST", "/api/learning/graph/compare", {"message": message}, LANGGRAPH_AGENT_API_URL)
