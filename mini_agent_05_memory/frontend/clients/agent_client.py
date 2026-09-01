from typing import Any
from urllib.parse import quote

from core.api_client import request


def get_memory_types():
    return request("GET", "/api/memory/types")


def preview_conversation_window(messages: list[dict[str, str]], max_recent_messages: int):
    return request("POST", "/api/memory/conversation-window", json={
        "messages": messages,
        "max_recent_messages": max_recent_messages,
    })


def save_memory(user_id: str, key: str, value: str, storage: str):
    return request("POST", "/api/memory/items", json={
        "user_id": user_id, "key": key, "value": value, "storage": storage,
    })


def list_memories(user_id: str, storage: str):
    return request("GET", f"/api/memory/items/{quote(user_id, safe='')}?storage={storage}")


def delete_memory(user_id: str, memory_id: str, storage: str):
    path = f"/api/memory/items/{quote(user_id, safe='')}/{quote(memory_id, safe='')}?storage={storage}"
    return request("DELETE", path)


def personalize_with_memory(user_id: str, question: str, storage: str, provider: str):
    return request("POST", "/api/memory/personalize", json={
        "user_id": user_id, "question": question, "storage": storage, "provider": provider,
    })


def save_session(session_id: str, state: dict[str, Any], user_id: str = "demo-user"):
    return request("POST", "/api/memory/sessions", json={
        "user_id": user_id, "session_id": session_id, "state": state,
    })


def get_session(session_id: str, user_id: str = "demo-user", refresh_ttl: bool = False):
    path = f"/api/memory/sessions/{quote(session_id, safe='')}?user_id={quote(user_id, safe='')}&refresh_ttl={str(refresh_ttl).lower()}"
    return request("GET", path)


def delete_session(session_id: str, user_id: str = "demo-user"):
    path = f"/api/memory/sessions/{quote(session_id, safe='')}?user_id={quote(user_id, safe='')}"
    return request("DELETE", path)


def patch_session(user_id: str, session_id: str, changes: dict[str, Any], expected_version: int):
    return request("PATCH", "/api/memory/sessions", json={
        "user_id": user_id, "session_id": session_id,
        "changes": changes, "expected_version": expected_version,
    })


def append_conversation(user_id: str, session_id: str, role: str, content: str):
    return request("POST", "/api/memory/conversations", json={
        "user_id": user_id, "session_id": session_id, "role": role, "content": content,
    })


def restore_memory(user_id: str, session_id: str):
    return request("GET", f"/api/memory/restore/{quote(user_id, safe='')}/{quote(session_id, safe='')}")


def export_memory(user_id: str):
    return request("GET", f"/api/memory/export/{quote(user_id, safe='')}")


def get_memory_status():
    return request("GET", "/api/memory/status")
