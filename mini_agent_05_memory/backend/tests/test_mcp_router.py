from fastapi.testclient import TestClient

from app.main import app
from app.routers import mcp_router as router_module


client = TestClient(app)


def test_mcp_status(monkeypatch) -> None:
    async def fake_discover_tools():
        return [{"name": "list_memories"}, {"name": "save_memory"}]

    monkeypatch.setattr(router_module, "discover_tools", fake_discover_tools)
    response = client.get("/api/mcp/status")
    assert response.status_code == 200
    assert response.json()["storage"] == "postgres"
    assert response.json()["tool_count"] == 2


def test_mcp_save_does_not_accept_user_id(monkeypatch) -> None:
    async def fake_call(name, arguments=None):
        return {"name": name, "arguments": arguments}

    monkeypatch.setattr(router_module, "call_memory_tool", fake_call)
    response = client.post(
        "/api/mcp/memories",
        json={"user_id": "user-b", "key": "transportation", "value": "렌터카"},
    )
    assert response.status_code == 422


def test_mcp_save_forwards_only_memory_fields(monkeypatch) -> None:
    async def fake_call(name, arguments=None):
        return {"name": name, "arguments": arguments}

    monkeypatch.setattr(router_module, "call_memory_tool", fake_call)
    response = client.post(
        "/api/mcp/memories",
        json={"key": "transportation", "value": "대중교통"},
    )
    assert response.status_code == 200
    assert response.json()["arguments"] == {"key": "transportation", "value": "대중교통"}
