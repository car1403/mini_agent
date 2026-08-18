import json

from redis import Redis

from app.config import settings


def client() -> Redis:
    return Redis.from_url(settings.redis_url, decode_responses=True)


def key(session_id: str) -> str:
    return f"mini-agent:session:{session_id}"


def save(session_id: str, state: dict) -> int:
    redis_client = client()
    redis_client.setex(
        key(session_id),
        settings.redis_ttl_seconds,
        json.dumps(state, ensure_ascii=False),
    )
    return settings.redis_ttl_seconds


def get(session_id: str) -> tuple[dict | None, int]:
    redis_client = client()
    value = redis_client.get(key(session_id))
    return (json.loads(value) if value else None, redis_client.ttl(key(session_id)))


def delete(session_id: str) -> bool:
    return bool(client().delete(key(session_id)))


def ping() -> bool:
    return bool(client().ping())
