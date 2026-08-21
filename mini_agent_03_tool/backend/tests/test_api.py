from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.main import app
from app.agents import runtime
from app.agents.travel_agent import select_travel_tool
from app.tools.registry import TOOL_REGISTRY, ToolSpec, get_tool_definitions


client = TestClient(app)


def test_health_and_mock_default() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["stage"] == "mini_agent_03_tool"
    assert response.json()["default_provider"] == "mock"


def test_tool_registry_contains_read_only_tools() -> None:
    response = client.get("/api/tools")
    assert response.status_code == 200
    names = {item["name"] for item in response.json()["tools"]}
    assert names == {"get_current_weather", "get_weather_forecast", "search_hotels", "search_attractions"}
    assert "delete" not in names


def test_tool_specs_are_the_single_source_for_definition_and_execution() -> None:
    definitions = {item["name"]: item for item in get_tool_definitions()}
    assert set(definitions) == set(TOOL_REGISTRY)
    for name, spec in TOOL_REGISTRY.items():
        assert isinstance(spec, ToolSpec)
        assert spec.name == name
        assert definitions[name]["description"] == spec.description
        assert definitions[name]["input_schema"] == spec.input_model.model_json_schema()


def test_tool_choice_none_prevents_selection() -> None:
    response = client.post("/api/tools/select", json={"tool_choice": "none", "message": "오늘 부산 날씨"})
    assert response.status_code == 200
    assert response.json()["tool_name"] is None


def test_allowed_tool_runs_after_validation() -> None:
    response = client.post("/api/tools/run", json={"tool_name": "get_current_weather", "arguments": {"city": "부산"}})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["source"] == "mock"


def test_unknown_tool_is_blocked_by_allowlist() -> None:
    response = client.post("/api/tools/run", json={"tool_name": "delete_database", "arguments": {}})
    assert response.status_code == 200
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "TOOL_NOT_ALLOWED"


def test_unknown_argument_is_blocked_by_schema() -> None:
    response = client.post(
        "/api/tools/run",
        json={
            "tool_name": "get_weather_forecast",
            "arguments": {
                "city": "부산",
                "target_date": (date.today() + timedelta(days=1)).isoformat(),
                "unknown": True,
            },
        },
    )
    assert response.status_code == 200
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "TOOL_VALIDATION_ERROR"


def test_forecast_rejects_past_and_too_distant_dates() -> None:
    for target_date in (
        (date.today() - timedelta(days=1)).isoformat(),
        (date.today() + timedelta(days=17)).isoformat(),
    ):
        response = client.post(
            "/api/tools/run",
            json={
                "tool_name": "get_weather_forecast",
                "arguments": {"city": "부산", "target_date": target_date},
            },
        )
        assert response.status_code == 200
        assert response.json()["success"] is False
        assert response.json()["error"]["code"] == "TOOL_VALIDATION_ERROR"


def test_invalid_hotel_dates_return_validation_error() -> None:
    response = client.post("/api/tools/run", json={"tool_name": "search_hotels", "arguments": {"city": "부산", "check_in": "2026-08-12", "check_out": "2026-08-10", "guests": 2}})
    assert response.status_code == 200
    assert response.json()["error"]["code"] == "TOOL_VALIDATION_ERROR"


def test_openai_tool_call_is_visible_and_direct(monkeypatch) -> None:
    class FunctionCall:
        type = "function_call"
        name = "get_current_weather"
        arguments = '{"city":"부산"}'

    class Responses:
        def __init__(self) -> None:
            self.kwargs = None

        def create(self, **kwargs):
            self.kwargs = kwargs
            return type("Response", (), {"output": [FunctionCall()]})()

    responses = Responses()
    client_double = type("OpenAIClient", (), {"responses": responses})()
    monkeypatch.setattr(runtime, "_openai_client", lambda: client_double)

    decision = select_travel_tool("부산 날씨")

    assert decision.tool_name == "get_current_weather"
    assert decision.arguments == {"city": "부산"}
    assert responses.kwargs["input"] == "부산 날씨"
    assert responses.kwargs["tools"]
