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
