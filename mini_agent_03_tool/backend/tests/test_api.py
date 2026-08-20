from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.main import app


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


def test_mock_selects_hotel_without_running_it() -> None:
    response = client.post("/api/tools/select", json={"provider": "mock", "message": "부산 숙소를 찾아줘."})
    assert response.status_code == 200
    assert response.json()["tool_name"] == "search_hotels"
    assert response.json()["arguments"]["city"] == "부산"
    assert response.json()["needs_clarification"] is True
    assert set(response.json()["missing_arguments"]) == {"check_in", "check_out", "guests"}


def test_tool_choice_none_prevents_selection() -> None:
    response = client.post("/api/tools/select", json={"provider": "mock", "tool_choice": "none", "message": "오늘 부산 날씨"})
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


def test_tool_compare_keeps_provider_error() -> None:
    response = client.post("/api/tools/compare", json={"providers": ["mock", "openai"], "message": "부산 날씨"})
    assert response.status_code == 200
    results = response.json()["results"]
    assert results[0]["status"] == "success"
    if results[1]["status"] == "error":
        assert "OPENAI_API_KEY" in results[1]["error"]


def test_mock_agent_loop_uses_tool_result() -> None:
    response = client.post(
        "/api/tools/complete",
        json={"provider": "mock", "message": "오늘 부산 날씨를 알려줘"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["decision"]["tool_name"] == "get_current_weather"
    assert body["tool_result"]["success"] is True
    assert "get_current_weather" in body["final_answer"]


def test_mock_selects_forecast_for_future_weather() -> None:
    response = client.post("/api/tools/select", json={"provider": "mock", "message": "내일 부산에 비가 올까?"})
    assert response.status_code == 200
    body = response.json()
    assert body["tool_name"] == "get_weather_forecast"
    assert body["arguments"]["city"] == "부산"
    assert "target_date" in body["arguments"]
    assert [item["stage"] for item in body["trace"]] == ["tool_selection", "tool_result", "final_answer"]


def test_agent_loop_asks_before_inventing_missing_arguments() -> None:
    response = client.post(
        "/api/tools/complete",
        json={"provider": "mock", "message": "숙소를 찾아줘"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["decision"]["needs_clarification"] is True
    assert body["tool_result"] is None
    assert "city" in body["final_answer"]


def test_agent_loop_does_not_run_unneeded_tool() -> None:
    response = client.post(
        "/api/tools/complete",
        json={"provider": "mock", "message": "여행을 준비하고 있어요"},
    )
    assert response.status_code == 200
    assert response.json()["decision"]["tool_name"] is None
    assert response.json()["tool_result"] is None
