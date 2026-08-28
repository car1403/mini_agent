"""Redis에 RAG 답변을 짧게 보관하는 교육용 TTL Cache입니다."""

import hashlib
import json
from typing import Any

from redis import Redis

from app.core.config import settings


KEY_PREFIX = "mini-agent:rag-answer:"
AGENT_STATE_PREFIX = "mini-agent:rag-agent-state:"


def client() -> Redis:
    return Redis.from_url(settings.redis_url, decode_responses=True)


def make_key(
    query: str,
    mode: str,
    top_k: int,
    provider: str,
    score_threshold: float | None = None,
    metadata_filter: dict[str, Any] | None = None,
) -> str:
    # 검색 조건이나 모델이 달라지면 같은 질문도 별도 Cache 항목으로 취급합니다.
    payload = (
        f"{settings.rag_collection}|{settings.ollama_embedding_model}|"
        f"{settings.rag_min_score}|{query.strip()}|{mode}|{top_k}|{provider}|"
        f"{score_threshold}|{json.dumps(metadata_filter or {}, ensure_ascii=False, sort_keys=True)}"
    )
    return KEY_PREFIX + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def get(key: str) -> tuple[dict[str, Any] | None, int]:
    redis_client = client()
    value = redis_client.get(key)
    return (json.loads(value) if value else None, redis_client.ttl(key))


def set(key: str, value: dict[str, Any]) -> int:
    redis_client = client()
    redis_client.setex(key, settings.rag_cache_ttl_seconds, json.dumps(value, ensure_ascii=False))
    return settings.rag_cache_ttl_seconds


def invalidate_answer_cache() -> int:
    # KEYS 대신 SCAN을 사용해 Mini Agent RAG prefix만 점진적으로 찾습니다.
    redis_client = client()
    keys = list(redis_client.scan_iter(match=f"{KEY_PREFIX}*", count=100))
    return redis_client.delete(*keys) if keys else 0


def invalidate_all() -> int:
    """기존 호출자를 위한 호환 이름입니다."""
    return invalidate_answer_cache()


def _agent_state_key(session_id: str) -> str:
    digest = hashlib.sha256(session_id.encode("utf-8")).hexdigest()
    return AGENT_STATE_PREFIX + digest


def get_agent_state(session_id: str) -> dict[str, Any] | None:
    value = client().get(_agent_state_key(session_id))
    return json.loads(value) if value else None


def set_agent_state(session_id: str, state: dict[str, Any]) -> int:
    ttl = settings.rag_cache_ttl_seconds
    client().setex(_agent_state_key(session_id), ttl, json.dumps(state, ensure_ascii=False))
    return ttl


def delete_agent_state(session_id: str) -> bool:
    return bool(client().delete(_agent_state_key(session_id)))


def ping() -> bool:
    return bool(client().ping())
