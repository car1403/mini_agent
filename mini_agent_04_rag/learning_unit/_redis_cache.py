"""RAG 예제가 공유하는 Redis JSON Cache입니다.

Redis 연결 실패나 잘못된 Cache 값은 MISS로 처리하여 pgvector 검색과 답변 생성을
계속할 수 있게 합니다. Redis를 장기 데이터의 유일한 저장소로 사용하지 않습니다.
"""

import hashlib
import json
import os
from typing import Any

import redis


REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
DEFAULT_TTL_SECONDS = int(os.getenv("REDIS_TTL_SECONDS", "1800"))


def cache_key(namespace: str, payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"rag:{namespace}:{digest}"


class JsonCache:
    def __init__(self, url: str = REDIS_URL) -> None:
        self.client = redis.from_url(url, decode_responses=True, socket_connect_timeout=2)

    def get(self, key: str) -> dict[str, Any] | None:
        try:
            value = self.client.get(key)
            if value is None:
                return None
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else None
        except (redis.RedisError, json.JSONDecodeError):
            return None

    def set(self, key: str, value: dict[str, Any], *, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> bool:
        if ttl_seconds < 1:
            raise ValueError("ttl_seconds는 1 이상이어야 합니다.")
        try:
            self.client.setex(key, ttl_seconds, json.dumps(value, ensure_ascii=False))
            return True
        except redis.RedisError:
            return False

    def ttl(self, key: str) -> int | None:
        try:
            value = self.client.ttl(key)
            return value if value >= 0 else None
        except redis.RedisError:
            return None


    def delete_namespace(self, namespace: str) -> int | None:
        """SCAN으로 특정 RAG Namespace만 찾아 삭제합니다.

        Redis 장애는 None으로 표시합니다. 교육 예제에서도 전체 DB를 비우는 FLUSHDB나
        운영 환경을 멈출 수 있는 광범위한 KEYS 명령은 사용하지 않습니다.
        """
        if not namespace or any(character.isspace() for character in namespace):
            raise ValueError("namespace는 공백 없는 문자열이어야 합니다.")
        pattern = f"rag:{namespace}:*"
        deleted = 0
        try:
            batch: list[str] = []
            for key in self.client.scan_iter(match=pattern, count=100):
                batch.append(key)
                if len(batch) == 100:
                    deleted += self.client.delete(*batch)
                    batch.clear()
            if batch:
                deleted += self.client.delete(*batch)
            return deleted
        except redis.RedisError:
            return None

