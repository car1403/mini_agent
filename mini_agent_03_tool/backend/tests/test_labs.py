from fastapi.testclient import TestClient
from app.main import app
from app.repositories.lab_repository import lab_repository
from app.schemas.lab import LabRouteDecision
from app.services import lab_routing_service
from app.schemas.lab import AirConditionerInput, InventoryInput, ParkingInput
from app.services import air_conditioner_service, inventory_service, parking_service

client = TestClient(app)

def setup_function() -> None:
    lab_repository.reset()

def run(lab_id: str, message: str, arguments: dict | None = None, confirmed: bool = False, action_id: str | None = None):
    return client.post("/api/labs/run", json={"lab_id": lab_id, "message": message, "arguments": arguments or {}, "confirmed": confirmed, "action_id": action_id, "session_id": "test"})

def fake_ollama(monkeypatch) -> None:
    def parking(message, arguments):
        return ParkingInput.model_validate(arguments), {"stage": "parking_agent_extraction", "data": arguments}
    def air(message, arguments):
        return AirConditionerInput.model_validate(arguments), {"stage": "air_conditioner_agent_extraction", "data": arguments}
    def inventory(message, arguments):
        return InventoryInput.model_validate(arguments), {"stage": "inventory_agent_extraction", "data": arguments}
    monkeypatch.setattr(parking_service, "extract_parking_request", parking)
    monkeypatch.setattr(air_conditioner_service, "extract_air_conditioner_request", air)
    monkeypatch.setattr(inventory_service, "extract_inventory_request", inventory)

def test_workflow_uses_agent_then_confirmation(monkeypatch) -> None:
    fake_ollama(monkeypatch)
    prepared = run("air_conditioner", "28도", {"temperature_c": 28}).json()
    assert prepared["status"] == "confirmation_required"
    response = run("air_conditioner", "확인", confirmed=True, action_id=prepared["state"]["pending_action_id"])
    assert response.json()["state"]["power"] == "on"

def test_mutation_requires_confirmation(monkeypatch) -> None:
    fake_ollama(monkeypatch)
    response = run("parking", "12가3456 문 열어줘", {"plate_number": "12가3456"})
    assert response.json()["status"] == "confirmation_required"
    assert lab_repository.gate_open is False

def test_confirmed_parking_executes_allowlisted_handler(monkeypatch) -> None:
    fake_ollama(monkeypatch)
    prepared = run("parking", "12가3456 문 열어줘", {"plate_number": "12가3456"}).json()
    response = run("parking", "확인", confirmed=True, action_id=prepared["state"]["pending_action_id"])
    assert response.json()["status"] == "completed"
    assert response.json()["tool_calls"][0]["tool"] == "open_gate"
    assert lab_repository.gate_open is True

def test_cafe_keeps_arguments_between_cycles() -> None:
    first = run("cafe", "카페라테 주세요")
    assert first.json()["status"] == "needs_clarification"
    second = run("cafe", "미디엄 두 잔")
    assert second.json()["status"] == "completed"
    assert second.json()["trace"][-1]["stage"] == "tool_execution"
    assert second.json()["trace"][-1]["data"]["success"] is True

def test_library_rejects_confirmation_without_pending_action() -> None:
    response = run(
        "library", "바로 대출", {"member_id": "M100", "book_id": "B101"},
        confirmed=True,
    )
    assert response.json()["status"] == "rejected"
    assert response.json()["termination_reason"] == "invalid_action"
    assert lab_repository.books["B101"]["available"] is True

def test_library_uses_dynamic_tools_and_one_time_confirmation() -> None:
    arguments = {"member_id": "M100", "book_id": "B101"}
    prepared = run("library", "도서를 대출하고 싶어", arguments).json()
    assert prepared["status"] == "confirmation_required"
    assert [call["tool"] for call in prepared["tool_calls"][:3]] == [
        "get_member", "get_book", "get_current_loans",
    ]
    assert [item["stage"] for item in prepared["trace"] if item["stage"] == "tool_execution"] == [
        "tool_execution", "tool_execution", "tool_execution",
    ]
    action_id = prepared["state"]["pending_action_id"]
    confirmed = run("library", "확인", confirmed=True, action_id=action_id).json()
    assert confirmed["status"] == "completed"
    assert lab_repository.books["B101"]["available"] is False
    repeated = run("library", "다시 확인", confirmed=True, action_id=action_id).json()
    assert repeated["status"] == "rejected"
    assert repeated["termination_reason"] == "invalid_action"

def test_travel_trace_contains_actual_tool_executions() -> None:
    response = run("travel", "내일 부산 여행").json()
    assert response["status"] == "completed"
    assert [call["tool"] for call in response["tool_calls"]] == [
        "get_weather_forecast", "search_attractions",
    ]
    executions = [item for item in response["trace"] if item["stage"] == "tool_execution"]
    assert len(executions) == 2
    assert all(item["data"]["success"] for item in executions)

def test_inventory_detects_version_conflict(monkeypatch) -> None:
    fake_ollama(monkeypatch)
    args = {"sku": "SKU-001", "quantity": 1, "expected_version": 1}
    first = run("inventory", "예약", args).json()
    assert run("inventory", "확인", confirmed=True, action_id=first["state"]["pending_action_id"]).json()["trace"][0]["data"]["reserved"] is True
    assert run("inventory", "예약", args).json()["termination_reason"] == "version_conflict"

def test_auto_route_uses_routing_decision(monkeypatch) -> None:
    monkeypatch.setattr(lab_routing_service, "classify_lab", lambda _: LabRouteDecision(lab_id="travel", confidence=.95, reason="여행 요청", provider="ollama", model="llama3.2"))
    response = run("auto", "내일 부산 여행")
    assert response.json()["lab_id"] == "travel"
    assert response.json()["execution_type"] == "agent"

def test_reset_restores_mock_state() -> None:
    lab_repository.gate_open = True
    response = client.post("/api/labs/reset")
    assert response.status_code == 200
    assert lab_repository.gate_open is False
