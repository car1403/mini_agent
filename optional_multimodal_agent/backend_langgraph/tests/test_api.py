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
    from app.schemas.models import TravelImageAnalysis
    from app.services.media_service import validate_image
    from app.workflows.langgraph_travel_workflow import use_image_analysis_node
    client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["mode"] == "mock"


def test_image_analysis_upload(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.routers.api.analyze_travel_image",
        lambda content_type, content, question: TravelImageAnalysis(
            scene_type="transport",
            summary="기차표입니다.",
            visible_text=["서울", "부산"],
            travel_tips=["출발 시간을 확인하세요."],
            safety_notes=["예약번호를 가리세요."],
        ),
    )
    response = client.post(
        "/api/media/image-analysis",
        files={"image": ("ticket.png", b"fake-png", "image/png")},
        data={"question": "무엇인가요?"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["scene_type"] == "transport"


def test_tts_returns_mp3(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.routers.api.synthesize_speech",
        lambda text, voice, instructions: b"fake-mp3",
    )
    response = client.post(
        "/api/media/tts",
        json={"text": "안전한 여행 되세요.", "voice": "coral"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"
    assert response.headers["x-synthetic-voice"] == "true"
    assert response.content == b"fake-mp3"


def test_multimodal_agent_receives_structured_analysis(monkeypatch) -> None:
    captured = {}
    monkeypatch.setattr(
        "app.routers.api.analyze_travel_image",
        lambda content_type, content, question: TravelImageAnalysis(
            scene_type="landmark",
            summary="해변 관광지입니다.",
            travel_tips=["일몰 시간을 확인하세요."],
            safety_notes=["파도에 주의하세요."],
        ),
    )

    def fake_start(payload):
        captured.update(payload)
        return {"run_id": "run-image", "status": "waiting_approval"}

    monkeypatch.setattr("app.routers.api.start_langgraph_run", fake_start)
    response = client.post(
        "/api/media/agent-runs",
        files={"image": ("beach.png", b"fake", "image/png")},
        data={
            "user_id": "demo",
            "message": "8월 부산 2박, 성인 2명, 예산 50만 원",
            "provider": "mock",
        },
    )
    assert response.status_code == 200
    assert captured["image_analysis"]["scene_type"] == "landmark"
    assert "image" not in captured


def test_langgraph_node_uses_analysis_without_binary() -> None:
    output = use_image_analysis_node(
        {
            "message": "부산 여행을 계획해 주세요.",
            "image_analysis": {
                "scene_type": "transport",
                "summary": "기차표입니다.",
                "travel_tips": ["출발 시간을 확인하세요."],
                "safety_notes": ["예약번호를 가리세요."],
            },
        }
    )
    assert "기차표입니다." in output["message"]
    assert output["trace"][0]["node"] == "use_image_analysis"
    assert "image" not in output


def test_image_validation_rejects_non_image() -> None:
    try:
        validate_image("text/plain", b"not-an-image")
        assert False, "비이미지 파일을 허용하면 안 됩니다."
    except ValueError as error:
        assert "이미지" in str(error)


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


def test_langgraph_blocks_wrong_actor_and_duplicate_decision() -> None:
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


def test_preparing_trip_is_not_misclassified_as_rain() -> None:
    response = client.post(
        "/api/tools/select",
        json={"provider": "mock", "message": "부산 여행을 준비해줘"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["tool_name"] is None
