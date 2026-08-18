import json
from typing import Any

from redis import Redis


class RedisSessionStore:
    """TTL이 필요한 대화 상태와 Cache를 Redis에 저장합니다."""

    def __init__(self, redis_url: str, ttl_seconds: int) -> None:
        self.client = Redis.from_url(redis_url, decode_responses=True)
        self.ttl_seconds = ttl_seconds

    def set(self, session_id: str, state: dict[str, Any]) -> None:
        self.client.setex(
            f"agent:session:{session_id}",
            self.ttl_seconds,
            json.dumps(state, ensure_ascii=False),
        )

    def get(self, session_id: str) -> dict[str, Any] | None:
        value = self.client.get(f"agent:session:{session_id}")
        return json.loads(value) if value else None

    def delete(self, session_id: str) -> bool:
        return bool(self.client.delete(f"agent:session:{session_id}"))

    def ping(self) -> bool:
        return bool(self.client.ping())
