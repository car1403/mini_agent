from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict, Field

from app.agents.models import ToolDecision
from app.main import app
from app.tools.executor import execute_tool_safely
from app.tools.registry import TOOL_REGISTRY, ToolSpec


client = TestClient(app)


class DemoArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    quantity: int = Field(ge=1)


def test_tool_spec_passes_validated_model_to_function() -> None:
    received: list[DemoArguments] = []

    def execute(arguments: BaseModel) -> dict:
        assert isinstance(arguments, DemoArguments)
        received.append(arguments)
        return {"quantity": arguments.quantity}

    spec = ToolSpec("demo", "검증 모델 전달", DemoArguments, execute)
    assert spec.execute({"quantity": "2"}) == {"quantity": 2}
    assert received[0].quantity == 2


def test_executor_returns_standard_not_allowed_error() -> None:
    result = execute_tool_safely("run_arbitrary_sql", {})
    assert result.success is False
    assert result.error["code"] == "TOOL_NOT_ALLOWED"


def test_executor_returns_validation_details() -> None:
    result = execute_tool_safely(
        "search_hotels",
        {
            "city": "부산",
            "check_in": "2026-08-23",
            "check_out": "2026-08-22",
            "guests": 2,
            "unexpected": True,
        },
    )
    assert result.success is False
    assert result.error["code"] == "TOOL_VALIDATION_ERROR"
    assert result.error["details"]


def test_complete_cycle_returns_clarification_before_execution(monkeypatch) -> None:
    from app.routers import stage_03_router

    def incomplete_decision(provider: str, message: str) -> ToolDecision:
        return ToolDecision(
            provider=provider,
            model="test-model",
            tool_name="search_hotels",
            arguments={"city": "부산"},
            reason="필수 날짜 누락",
            confidence=0.8,
            latency_ms=0,
            missing_arguments=["check_in", "check_out", "guests"],
            needs_clarification=True,
            follow_up_question="체크인·체크아웃 날짜와 인원을 알려주세요.",
        )

    monkeypatch.setattr(stage_03_router, "select_tool", incomplete_decision)
    response = client.post(
        "/api/tools/complete",
        json={"provider": "mock", "message": "부산 호텔을 찾아주세요."},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["decision"]["needs_clarification"] is True
    assert body["tool_result"] is None
    assert body["final_answer"] == "체크인·체크아웃 날짜와 인원을 알려주세요."
    assert [item["stage"] for item in body["trace"]] == ["1_tool_selection"]


def test_complete_cycle_contains_selection_execution_and_answer_trace() -> None:
    response = client.post(
        "/api/tools/complete",
        json={"provider": "mock", "message": "부산 오늘 날씨를 알려주세요."},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["tool_result"]["success"] is True
    assert [item["stage"] for item in body["trace"]] == [
        "1_tool_selection",
        "2_tool_execution",
        "3_final_answer",
    ]
