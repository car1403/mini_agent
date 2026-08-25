"""사용자 역할을 Backend에서 확인한 뒤 ACL로 문서를 제한하는 pgvector Tool Lab."""

import sys
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _pgvector_store import delete_collection, similarity_search, upsert_text
from _redis_cache import JsonCache, cache_key


COLLECTION = "rag_internal_policy_acl_lab"
CACHE_NAMESPACE = "internal-policy-acl"
Role = Literal["employee", "manager", "hr"]
ALLOWED_ROLES = {"employee", "manager", "hr"}

ROLE_DOCUMENTS = [
    ("휴가 규정", "연차 휴가는 사내 시스템에서 신청합니다.", ["employee", "manager", "hr"]),
    ("관리자 평가", "관리자는 분기마다 팀원 성과 면담을 진행합니다.", ["manager", "hr"]),
    ("급여 운영", "급여 정정 요청은 HR 담당자가 승인합니다.", ["hr"]),
]


class PolicySearchArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=2, max_length=300)
    top_k: int = Field(default=3, ge=1, le=5)


def prepare_documents(cache: JsonCache) -> None:
    delete_collection(COLLECTION)
    for index, (title, content, allowed_roles) in enumerate(ROLE_DOCUMENTS):
        upsert_text(
            collection=COLLECTION,
            title=title,
            content=content,
            source="internal-policy.md",
            chunk_index=index,
            metadata={"allowed_roles": allowed_roles, "status": "active"},
        )
    cache.delete_namespace(CACHE_NAMESPACE)


def search_internal_policy(
    arguments: PolicySearchArguments,
    *,
    authenticated_role: Role,
) -> list[dict[str, Any]]:
    """role은 Agent arguments가 아니라 인증된 Backend 세션에서 받습니다."""
    if authenticated_role not in ALLOWED_ROLES:
        raise ValueError(f"허용되지 않은 사용자 역할입니다: {authenticated_role}")
    return similarity_search(
        arguments.query,
        collection=COLLECTION,
        top_k=arguments.top_k,
        metadata_filter={"allowed_roles": [authenticated_role], "status": "active"},
    )


def cached_policy_search(question: str, role: Role, cache: JsonCache) -> dict[str, Any]:
    arguments = PolicySearchArguments(query=question, top_k=3)
    # 권한이 다른 사용자가 같은 Cache Entry를 공유하지 않도록 role을 반드시 포함합니다.
    key = cache_key(CACHE_NAMESPACE, {**arguments.model_dump(), "authenticated_role": role})
    cached = cache.get(key)
    if cached is not None:
        return {**cached, "cache_hit": True, "cache_ttl_seconds": cache.ttl(key)}

    results = search_internal_policy(arguments, authenticated_role=role)
    value = {
        "role": role,
        "results": results,
        "termination_reason": "evidence_found" if results else "no_authorized_evidence",
    }
    saved = cache.set(key, value)
    return {**value, "cache_hit": False, "cache_saved": saved}


if __name__ == "__main__":
    redis_cache = JsonCache()
    prepare_documents(redis_cache)
    question = "급여 정정은 누가 승인하나요?"
    for user_role in ("employee", "manager", "hr"):
        result = cached_policy_search(question, user_role, redis_cache)
        print(f"\n[{user_role}] {result['termination_reason']}")
        for item in result["results"]:
            print(item["title"], "|", item["metadata"], "|", item["content"])
        print("cache_hit:", result["cache_hit"])

