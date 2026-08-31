from fastapi.testclient import TestClient

from app.main import app
from app.memory.mock_store import mock_memory_store


client = TestClient(app)


def setup_function() -> None:
    mock_memory_store.clear()


def test_authenticated_api_requires_header() -> None:
    response = client.get("/api/memory/me/items")
    assert response.status_code == 401


def test_authenticated_api_uses_header_scope() -> None:
    for user_id, value in (("user-a", "대중교통"), ("user-b", "렌터카")):
        response = client.post(
            "/api/memory/me/items",
            headers={"X-Demo-User-ID": user_id},
            json={"key": "transportation", "value": value, "storage": "mock"},
        )
        assert response.status_code == 200

    response = client.get(
        "/api/memory/me/items?storage=mock",
        headers={"X-Demo-User-ID": "user-a"},
    )
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["user_id"] == "user-a"
    assert items[0]["value"] == "대중교통"


def test_authenticated_api_rejects_body_user_id() -> None:
    response = client.post(
        "/api/memory/me/items",
        headers={"X-Demo-User-ID": "user-a"},
        json={
            "user_id": "user-b",
            "key": "transportation",
            "value": "렌터카",
            "storage": "mock",
        },
    )
    assert response.status_code == 422


def test_authenticated_delete_cannot_cross_user_scope() -> None:
    created = client.post(
        "/api/memory/me/items",
        headers={"X-Demo-User-ID": "user-a"},
        json={"key": "hotel_preference", "value": "조용한 호텔", "storage": "mock"},
    ).json()

    blocked = client.delete(
        f"/api/memory/me/items/{created['id']}?storage=mock",
        headers={"X-Demo-User-ID": "user-b"},
    )
    assert blocked.json()["deleted"] is False
