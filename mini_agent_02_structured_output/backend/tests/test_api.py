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
    assert response.json()["providers"][0]["model"] == "deterministic-structured-mock"


def test_openapi_exposes_generic_structured_route_only() -> None:
    paths = client.get("/openapi.json").json()["paths"]
    assert "/api/structured/generate" in paths
    assert "/api/structured/travel-plan" not in paths


def test_prompt_preview_keeps_four_sections() -> None:
    response = client.post("/api/prompts/preview", json={
        "role": "여행 도우미", "instruction": "정보 추출", "context": "국내 여행", "constraint": "추측 금지"
    })
    assert response.status_code == 200
    assert all(title in response.json()["prompt"] for title in (
        "[Role]", "[Instruction]", "[Context]", "[Constraint]"
    ))


def test_prompt_preview_adds_optional_output_format() -> None:
    response = client.post("/api/prompts/preview", json={
        "role": "회의 기록자",
        "instruction": "결정 사항 정리",
        "context": "프로젝트 회의",
        "constraint": "추측 금지",
        "output_format": "결정 사항과 할 일 목록",
    })
    assert response.status_code == 200
    assert "[Output Format]" in response.json()["prompt"]


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


def test_support_ticket_validation_success() -> None:
    response = client.post("/api/structured/validate", json={
        "schema_type": "support_ticket",
        "payload": {
            "category": "billing",
            "priority": "medium",
            "summary": "중복 결제 확인 요청",
            "requires_human": True,
            "missing_information": ["주문 번호"],
        },
    })
    assert response.status_code == 200
    assert response.json()["schema_type"] == "support_ticket"
    assert response.json()["valid"] is True


def test_support_ticket_validation_rejects_literals_and_extra_field() -> None:
    response = client.post("/api/structured/validate", json={
        "schema_type": "support_ticket",
        "payload": {
            "category": "refund",
            "priority": "urgent",
            "summary": "환불 요청",
            "requires_human": True,
            "missing_information": [],
            "password": "secret",
        },
    })
    assert response.status_code == 200
    fields = {item["field"] for item in response.json()["errors"]}
    assert fields >= {"category", "priority", "password"}


def test_mock_structured_output_matches_contract() -> None:
    response = client.post("/api/structured/generate", json={
        "provider": "mock", "message": "제주 2박 3일 여행을 추천해 주세요."
    })
    assert response.status_code == 200
    assert response.json()["content"]["destination"] == "제주"


def test_mock_support_ticket_matches_contract() -> None:
    response = client.post("/api/structured/generate", json={
        "provider": "mock",
        "schema_type": "support_ticket",
        "message": "결제가 두 번 된 것 같습니다.",
    })
    assert response.status_code == 200
    assert response.json()["schema_type"] == "support_ticket"
    assert response.json()["content"]["category"] == "billing"


def test_legacy_travel_plan_route_remains_compatible() -> None:
    response = client.post("/api/structured/travel-plan", json={
        "provider": "mock", "message": "강릉 여행을 추천해 주세요."
    })
    assert response.status_code == 200
    assert response.json()["schema_type"] == "travel_plan"
    assert response.json()["content"]["destination"] == "강릉"


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
