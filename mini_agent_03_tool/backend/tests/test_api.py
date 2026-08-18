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
    assert names == {"get_weather", "search_hotels", "search_attractions"}
    assert "delete" not in names


def test_mock_selects_hotel_without_running_it() -> None:
    response = client.post("/api/tools/select", json={"provider": "mock", "message": "부산 숙소를 찾아줘."})
    assert response.status_code == 200
    assert response.json()["tool_name"] == "search_hotels"
    assert response.json()["arguments"]["city"] == "부산"


def test_allowed_tool_runs_after_validation() -> None:
    response = client.post("/api/tools/run", json={"tool_name": "get_weather", "arguments": {"city": "부산", "target_date": "2026-08-10"}})
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
            "tool_name": "get_weather",
            "arguments": {
                "city": "부산",
                "target_date": "2026-08-10",
                "unknown": True,
            },
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
        json={"provider": "mock", "message": "부산 날씨를 알려줘"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["decision"]["tool_name"] == "get_weather"
    assert body["tool_result"]["success"] is True
    assert "get_weather" in body["final_answer"]


def test_agent_loop_does_not_run_unneeded_tool() -> None:
    response = client.post(
        "/api/tools/complete",
        json={"provider": "mock", "message": "여행을 준비하고 있어요"},
    )
    assert response.status_code == 200
    assert response.json()["decision"]["tool_name"] is None
    assert response.json()["tool_result"] is None
