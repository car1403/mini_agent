from fastapi.testclient import TestClient

from app.agents.models import ToolDecision
from app.main import app
from app.tools.executor import execute_tool_safely


client = TestClient(app)


def test_knowledge_search_is_registered_as_read_only_tool() -> None:
    response = client.get("/api/tools")
    assert response.status_code == 200
    tools = {item["name"]: item for item in response.json()["tools"]}
    search_tool = tools["search_knowledge_base"]
    assert search_tool["input_schema"]["additionalProperties"] is False
    assert "query" in search_tool["input_schema"]["required"]


def test_knowledge_search_runs_through_common_executor() -> None:
    result = execute_tool_safely(
        "search_knowledge_base",
        {"query": "수하물은 몇 kg인가요?", "mode": "keyword", "top_k": 2},
    )
    assert result.success is True
    assert result.data["results"][0]["source"] == "baggage.md"


def test_knowledge_search_rejects_unknown_arguments() -> None:
    result = execute_tool_safely(
        "search_knowledge_base",
        {"query": "환불", "mode": "keyword", "run_sql": "DROP TABLE documents"},
    )
    assert result.success is False
    assert result.error["code"] == "TOOL_VALIDATION_ERROR"


def test_rag_agent_selects_executes_and_answers_from_tool_result() -> None:
    response = client.post(
        "/api/rag/agent",
        json={
            "query": "호텔을 당일 취소하면 환불되나요?",
            "provider": "mock",
            "mode": "keyword",
            "top_k": 2,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["decision"]["tool_name"] == "search_knowledge_base"
    assert body["execution"]["success"] is True
    assert body["tool_result"]
    assert body["termination_reason"] == "grounded_answer"
    assert [item["stage"] for item in body["trace"]] == [
        "1_tool_selection",
        "2_tool_execution",
        "3_final_answer",
    ]


def test_rag_agent_fails_closed_when_tool_is_not_selected(monkeypatch) -> None:
    from app.routers import rag_router

    monkeypatch.setattr(
        rag_router,
        "select_tool",
        lambda *args, **kwargs: ToolDecision(
            provider="mock", model="test", tool_name=None, arguments={},
            reason="검색 Tool 미선택", confidence=0.2, latency_ms=0,
        ),
    )
    response = client.post(
        "/api/rag/agent",
        json={"query": "내부 환불 정책은?", "provider": "mock", "mode": "keyword"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["termination_reason"] == "tool_not_selected"
    assert body["tool_result"] == []
    assert body["sources"] == []
