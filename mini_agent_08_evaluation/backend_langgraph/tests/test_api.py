import pytest


try:
    from langgraph.graph import StateGraph  # noqa: F401

    LANGGRAPH_AVAILABLE = True
    LANGGRAPH_ERROR = ""
except ImportError as error:
    LANGGRAPH_AVAILABLE = False
    LANGGRAPH_ERROR = str(error)

pytestmark = pytest.mark.skipif(
    not LANGGRAPH_AVAILABLE,
    reason=f"현재 PC에서 LangGraph 의존성을 불러올 수 없음: {LANGGRAPH_ERROR}",
)

if LANGGRAPH_AVAILABLE:
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["mode"] == "mock"


def test_extract_travel_request() -> None:
    response = client.post(
        "/api/travel/extract",
        json={"message": "8월 부산 2박 여행, 성인 2명, 예산 50만 원"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["destination"] == "부산"
    assert data["nights"] == 2
    assert data["adults"] == 2
    assert data["budget"] == 500000


def test_tool_allowlist_blocks_unknown_tool() -> None:
    response = client.post(
        "/api/tools/run",
        json={"tool_name": "delete_database", "arguments": {}},
    )
    assert response.status_code == 403


def test_core_evaluation_scenarios_pass() -> None:
    response = client.post("/api/evaluations/run", json={})
    assert response.status_code == 200
    report = response.json()["data"]
    assert report["summary"] == {
        "passed": 5,
        "failed": 0,
        "total": 5,
        "pass_rate": 1.0,
    }


def test_preparing_trip_is_not_misclassified_as_rain() -> None:
    response = client.post(
        "/api/tools/select",
        json={"message": "부산 여행을 준비해줘"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["tool_name"] is None


def test_evaluation_trace_explains_failure() -> None:
    response = client.post(
        "/api/evaluations/run",
        json={
            "scenarios": [
                {
                    "name": "의도적으로 실패",
                    "message": "안녕하세요",
                    "expected_tool": "get_weather",
                    "expected_status": "completed",
                }
            ]
        },
    )
    result = response.json()["data"]["results"][0]
    assert result["passed"] is False
    assert result["failed_checks"] == ["tool_match"]
    assert result["trace"][-1]["status"] == "failed"


def test_agent_needs_input() -> None:
    response = client.post(
        "/api/agent/runs",
        json={"user_id": "demo", "message": "여행을 준비해줘"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "needs_input"


def test_agent_approval_flow() -> None:
    created = client.post(
        "/api/agent/runs",
        json={
            "user_id": "demo",
            "message": "8월 부산 2박 여행, 성인 2명, 예산 50만 원",
        },
    ).json()["data"]
    assert created["status"] == "waiting_approval"
    approved = client.post(
        f"/api/agent/runs/{created['run_id']}/approve",
        json={"actor": "demo", "note": "교육용 승인"},
    )
    assert approved.status_code == 200
    assert approved.json()["data"]["status"] == "completed"


def test_langgraph_agent_needs_input() -> None:
    response = client.post(
        "/api/agent/runs",
        json={
            "user_id": "graph-demo",
            "message": "여행을 준비해줘",
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "needs_input"
    assert data["current_node"] == "validate_request"


def test_langgraph_agent_approval_and_resume() -> None:
    created = client.post(
        "/api/agent/runs",
        json={
            "user_id": "graph-demo",
            "message": "8월 부산 2박 여행, 성인 2명, 예산 50만 원",
        },
    ).json()["data"]
    assert created["status"] == "waiting_approval"
    assert created["current_node"] == "approval"

    approved = client.post(
        f"/api/agent/runs/{created['run_id']}/approve",
        json={"actor": "graph-demo", "note": "LangGraph 재개 승인"},
    )
    assert approved.status_code == 200
    data = approved.json()["data"]
    assert data["status"] == "completed"
    assert data["requires_approval"] is False
    assert data["trace"][-1]["node"] == "approval"


def test_langgraph_blocks_different_actor_and_duplicate_decision() -> None:
    created = client.post(
        "/api/agent/runs",
        json={
            "user_id": "owner-user",
            "message": "8월 부산 2박 여행, 성인 2명, 예산 50만 원",
        },
    ).json()["data"]
    blocked = client.post(
        f"/api/agent/runs/{created['run_id']}/approve",
        json={"actor": "other-user", "note": "대신 승인"},
    )
    approved = client.post(
        f"/api/agent/runs/{created['run_id']}/approve",
        json={"actor": "owner-user", "note": "본인 승인"},
    )
    duplicate = client.post(
        f"/api/agent/runs/{created['run_id']}/approve",
        json={"actor": "owner-user", "note": "중복 승인"},
    )
    assert blocked.status_code == 409
    assert approved.status_code == 200
    assert duplicate.status_code == 409
