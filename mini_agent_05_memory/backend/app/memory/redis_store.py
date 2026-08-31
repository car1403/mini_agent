import json
from hashlib import sha256

from redis import Redis

from app.core.config import settings


def client() -> Redis:
    return Redis.from_url(settings.redis_url, decode_responses=True)


def key(user_id: str, session_id: str) -> str:
    # 외부 ID를 Token으로 바꿔 Redis glob 문자와 구분자 충돌을 막습니다.
    return f"mini-agent:session:{_token(user_id)}:{_token(session_id)}"


def _token(value: str) -> str:
    if not value or len(value) > 100:
        raise ValueError("사용자 ID와 Session ID는 1~100자여야 합니다.")
    return sha256(value.encode("utf-8")).hexdigest()


def save(user_id: str, session_id: str, state: dict) -> int:
    redis_client = client()
    redis_client.setex(
        key(user_id, session_id),
        settings.redis_ttl_seconds,
        json.dumps(state, ensure_ascii=False),
    )
    return settings.redis_ttl_seconds


def get(user_id: str, session_id: str, refresh_ttl: bool = False) -> tuple[dict | None, int]:
    redis_client = client()
    session_key = key(user_id, session_id)
    value = redis_client.get(session_key)
    if value and refresh_ttl:
        redis_client.expire(session_key, settings.redis_ttl_seconds)
    return (json.loads(value) if value else None, redis_client.ttl(session_key))


def delete(user_id: str, session_id: str) -> bool:
    return bool(client().delete(key(user_id, session_id)))


def patch(user_id: str, session_id: str, changes: dict, expected_version: int) -> tuple[dict, int]:
    """WATCH로 동시에 수정된 Session을 덮어쓰지 않도록 갱신합니다."""
    from redis.exceptions import WatchError

    redis_client = client()
    session_key = key(user_id, session_id)
    with redis_client.pipeline() as pipe:
        try:
            pipe.watch(session_key)
            raw = pipe.get(session_key)
            if raw is None:
                raise ValueError("갱신할 Session이 없습니다.")
            state = json.loads(raw)
            if int(state.get("version", 0)) != expected_version:
                raise ValueError("Session version이 달라 갱신을 중단했습니다.")
            state.update(changes)
            state["version"] = expected_version + 1
            pipe.multi()
            pipe.setex(session_key, settings.redis_ttl_seconds, json.dumps(state, ensure_ascii=False))
            pipe.execute()
            return state, settings.redis_ttl_seconds
        except WatchError as error:
            raise ValueError("동시에 Session이 수정되어 다시 시도해야 합니다.") from error


def delete_for_user(user_id: str) -> int:
    redis_client = client()
    keys = list(redis_client.scan_iter(match=f"mini-agent:session:{_token(user_id)}:*", count=100))
    return redis_client.delete(*keys) if keys else 0


def ping() -> bool:
    return bool(client().ping())
