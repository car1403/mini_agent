from app.providers.mock import MockProvider
from app.schemas.models import TravelPlan


def test_mock_provider_text_contract() -> None:
    result = MockProvider().generate("system", "부산 여행")
    assert result.provider == "mock"
    assert result.model
    assert "부산 여행" in result.content
    assert result.latency_ms >= 0


def test_mock_provider_structured_contract() -> None:
    result = MockProvider().generate_structured(
        "system",
        "제주 여행을 추천해 주세요.",
        TravelPlan,
    )
    parsed = TravelPlan.model_validate(result.content)
    assert parsed.destination == "제주"
    assert parsed.activities


def test_mock_provider_tool_selection_contract() -> None:
    from app.tools.definitions import TRAVEL_TOOL_DEFINITIONS

    result = MockProvider().select_tool(
        "필요한 Tool을 선택하세요.",
        "부산 숙소를 찾아줘",
        TRAVEL_TOOL_DEFINITIONS,
    )
    assert result.provider == "mock"
    assert result.tool_name == "search_hotels"
    assert result.arguments["city"] == "부산"


def test_provider_status_api(client=None) -> None:
    from fastapi.testclient import TestClient

    from app.main import app

    response = TestClient(app).get("/api/providers/status")
    assert response.status_code == 200
    providers = response.json()["data"]["providers"]
    assert {item["provider"] for item in providers} == {
        "mock",
        "openai",
        "gemini",
        "ollama",
    }


def test_structured_mock_api() -> None:
    from fastapi.testclient import TestClient

    from app.main import app

    response = TestClient(app).post(
        "/api/providers/travel-plan",
        json={"provider": "mock", "message": "강릉 여행을 추천해 주세요."},
    )
    assert response.status_code == 200
    content = response.json()["data"]["content"]
    assert TravelPlan.model_validate(content).destination == "강릉"
