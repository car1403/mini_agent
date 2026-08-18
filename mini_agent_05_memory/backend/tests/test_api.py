from fastapi.testclient import TestClient

from app.main import app
from app.memory.mock_store import mock_memory_store


client = TestClient(app)


def setup_function() -> None:
    mock_memory_store.clear()


def test_health_and_mock_default() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["stage"] == "mini_agent_05_memory"
    assert response.json()["default_provider"] == "mock"


def test_memory_types_explain_rag_difference() -> None:
    response = client.get("/api/memory/types")
    assert response.status_code == 200
    names = {item["name"] for item in response.json()["types"]}
    assert {"short_term_state", "long_term_memory", "rag_document"} <= names


def test_conversation_window_keeps_recent_messages() -> None:
    messages = [
        {"role": "user", "content": f"message-{index}"}
        for index in range(5)
    ]
    response = client.post(
        "/api/memory/conversation-window",
        json={"messages": messages, "max_recent_messages": 2},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total_count"] == 5
    assert [item["content"] for item in body["recent_messages"]] == ["message-3", "message-4"]


def test_memory_upsert_and_user_isolation() -> None:
    created = client.post(
        "/api/memory/items",
        json={"user_id": "user-a", "key": "transportation", "value": "대중교통", "storage": "mock"},
    ).json()
    client.post(
        "/api/memory/items",
        json={"user_id": "user-a", "key": "transportation", "value": "도보", "storage": "mock"},
    )
    items = client.get("/api/memory/items/user-a?storage=mock").json()["items"]
    assert len(items) == 1
    assert items[0]["id"] == created["id"]
    assert items[0]["value"] == "도보"

    blocked = client.delete(f"/api/memory/items/user-b/{created['id']}?storage=mock")
    assert blocked.json()["deleted"] is False


def test_sensitive_memory_key_is_blocked() -> None:
    response = client.post(
        "/api/memory/items",
        json={"user_id": "user-a", "key": "password", "value": "secret", "storage": "mock"},
    )
    assert response.status_code == 422


def test_personalized_answer_uses_only_relevant_memory() -> None:
    for key, value in [
        ("transportation", "대중교통"),
        ("food_restriction", "해산물 알레르기"),
        ("hotel_preference", "조용한 호텔"),
    ]:
        client.post(
            "/api/memory/items",
            json={"user_id": "user-a", "key": key, "value": value, "storage": "mock"},
        )
    response = client.post(
        "/api/memory/personalize",
        json={"user_id": "user-a", "question": "식당을 추천해줘", "storage": "mock", "provider": "mock"},
    )
    keys = {item["key"] for item in response.json()["used_memories"]}
    assert keys == {"food_restriction"}


def test_unrelated_question_does_not_use_memory() -> None:
    client.post(
        "/api/memory/items",
        json={"user_id": "user-a", "key": "transportation", "value": "대중교통", "storage": "mock"},
    )
    response = client.post(
        "/api/memory/personalize",
        json={"user_id": "user-a", "question": "날씨를 알려줘", "storage": "mock", "provider": "mock"},
    )
    assert response.json()["used_memories"] == []
