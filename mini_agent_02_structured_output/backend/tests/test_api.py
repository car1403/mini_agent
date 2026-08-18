from fastapi.testclient import TestClient

from app.main import app
from app.schemas import TravelImageAnalysis


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["stage"] == "mini_agent_02_structured_output"
    assert response.json()["default_provider"] == "mock"


def test_provider_list_does_not_expose_keys() -> None:
    response = client.get("/api/providers")
    assert response.status_code == 200
    assert [item["provider"] for item in response.json()["providers"]] == [
        "mock", "gemini", "openai", "ollama"
    ]
    assert "api_key" not in response.text.lower()


def test_prompt_preview_keeps_four_sections() -> None:
    response = client.post("/api/prompts/preview", json={
        "role": "여행 도우미", "instruction": "정보 추출", "context": "국내 여행", "constraint": "추측 금지"
    })
    assert response.status_code == 200
    assert all(title in response.json()["prompt"] for title in (
        "[Role]", "[Instruction]", "[Context]", "[Constraint]"
    ))


def test_travel_plan_validation_success() -> None:
    response = client.post("/api/structured/validate", json={"payload": {
        "destination": "부산", "summary": "여행", "recommended_days": 2,
        "activities": ["산책"], "cautions": []
    }})
    assert response.status_code == 200
    assert response.json()["valid"] is True


def test_travel_plan_validation_reports_range_and_extra_field() -> None:
    response = client.post("/api/structured/validate", json={"payload": {
        "destination": "부산", "summary": "여행", "recommended_days": 0,
        "activities": [], "cautions": [], "password": "secret"
    }})
    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is False
    assert {item["field"] for item in body["errors"]} >= {"recommended_days", "activities", "password"}


def test_mock_structured_output_matches_contract() -> None:
    response = client.post("/api/structured/travel-plan", json={
        "provider": "mock", "message": "제주 2박 3일 여행을 추천해 주세요."
    })
    assert response.status_code == 200
    assert response.json()["content"]["destination"] == "제주"


def test_structured_compare_keeps_provider_errors() -> None:
    response = client.post("/api/structured/compare", json={
        "providers": ["mock", "openai"], "message": "부산 여행"
    })
    assert response.status_code == 200
    results = response.json()["results"]
    assert results[0]["status"] == "success"
    if results[1]["status"] == "error":
        assert "OPENAI_API_KEY" in results[1]["error"]


def test_image_and_tts_routes_are_kept_from_unit_01(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.routers.media_router.analyze_image",
        lambda *_: TravelImageAnalysis(scene_type="other", summary="여행 이미지"),
    )
    monkeypatch.setattr("app.routers.media_router.create_speech", lambda *_: b"mp3")
    image = client.post(
        "/api/media/image-analysis",
        files={"image": ("travel.png", b"fake", "image/png")},
    )
    audio = client.post("/api/media/tts", json={"text": "안내문", "voice": "coral"})
    assert image.status_code == 200
    assert audio.headers["x-synthetic-voice"] == "true"
