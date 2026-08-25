"""pgvector 검색 Tool과 Redis Cache를 사용하는 고객지원 RAG Agent Lab.

기본 mock 모드는 Agent 결정을 재현 가능하게 만들고, ollama 모드는 실제 Tool
Calling을 사용합니다. 두 모드 모두 실제 pgvector를 검색합니다.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError


# 10_labs에서 실행해도 상위 폴더의 공통 교육 모듈을 가져올 수 있게 합니다.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _pgvector_store import EMBEDDING_MODEL, OLLAMA_BASE_URL, similarity_search, upsert_text
from _redis_cache import DEFAULT_TTL_SECONDS, JsonCache, cache_key


COLLECTION = "rag_customer_support_lab"
AGENT_PROVIDER = os.getenv("RAG_LAB_AGENT_PROVIDER", "mock")
CHAT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


class SearchArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=2, max_length=500)
    top_k: int = Field(default=3, ge=1, le=5)


SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "search_knowledge_base",
        "description": "고객지원 정책 문서에서 질문과 관련된 근거를 검색합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "minLength": 2, "maxLength": 500},
                "top_k": {"type": "integer", "minimum": 1, "maximum": 5},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
}


def prepare_documents(cache: JsonCache) -> None:
    documents = [
        ("환불 정책", "체크인 3일 전까지 취소하면 전액 환불합니다.", "hotel-refund.md"),
        ("당일 취소", "체크인 당일 취소에는 숙박 요금 전액이 부과됩니다.", "hotel-refund.md"),
        ("수하물 정책", "교육용 국내선의 위탁 수하물은 15kg까지 허용합니다.", "baggage.md"),
    ]
    for index, (title, content, source) in enumerate(documents):
        upsert_text(
            collection=COLLECTION,
            title=title,
            content=content,
            source=source,
            chunk_index=index,
            metadata={"status": "active", "lesson": "customer-support-agent"},
        )
    cache.delete_namespace("customer-support-answer:v1")


def search_knowledge_base(arguments: SearchArguments) -> list[dict[str, Any]]:
    return similarity_search(
        arguments.query,
        collection=COLLECTION,
        top_k=arguments.top_k,
        metadata_filter={"status": "active"},
    )


TOOL_FUNCTIONS = {"search_knowledge_base": search_knowledge_base}


def execute_tool(name: str, raw_arguments: dict[str, Any]) -> list[dict[str, Any]]:
    """Agent 제안을 Allowlist와 Pydantic으로 검증한 뒤에만 실행합니다."""
    if name not in TOOL_FUNCTIONS:
        raise ValueError(f"허용되지 않은 Tool입니다: {name}")
    arguments = SearchArguments.model_validate(raw_arguments)
    return TOOL_FUNCTIONS[name](arguments)


def ollama_chat(messages: list[dict[str, Any]], *, tools: list[dict] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"model": CHAT_MODEL, "messages": messages, "stream": False}
    if tools:
        payload["tools"] = tools
    response = httpx.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, timeout=120)
    response.raise_for_status()
    return response.json()["message"]


def choose_action(question: str) -> dict[str, Any]:
    if AGENT_PROVIDER == "mock":
        return {"tool_calls": [{"function": {
            "name": "search_knowledge_base",
            "arguments": {"query": question, "top_k": 3},
        }}]}
    if AGENT_PROVIDER != "ollama":
        raise ValueError("RAG_LAB_AGENT_PROVIDER는 mock 또는 ollama여야 합니다.")
    return ollama_chat(
        [
            {"role": "system", "content": "고객지원 정책 질문은 반드시 검색 Tool을 사용하세요."},
            {"role": "user", "content": question},
        ],
        tools=[SEARCH_TOOL],
    )


def grounded_answer(question: str, results: list[dict[str, Any]]) -> str:
    if not results:
        return "등록된 고객지원 정책에서 근거를 찾지 못했습니다."
    context = "\n".join(
        f"[{item['source']}#{item['chunk_index']}] {item['content']}" for item in results
    )
    message = ollama_chat([
        {
            "role": "system",
            "content": "제공된 Context만 사용해 한국어로 답하고 출처를 표시하세요. 근거가 부족하면 모른다고 답하세요.",
        },
        {"role": "user", "content": f"질문: {question}\n\nContext:\n{context}"},
    ])
    return message.get("content", "")


def run_agent(question: str, cache: JsonCache) -> dict[str, Any]:
    key = cache_key("customer-support-answer:v1", {
        "collection": COLLECTION,
        "embedding_model": EMBEDDING_MODEL,
        "chat_model": CHAT_MODEL,
        "question": question,
        "top_k": 3,
    })
    cached = cache.get(key)
    if cached is not None:
        return {**cached, "cache_hit": True, "cache_ttl_seconds": cache.ttl(key)}

    trace: list[dict[str, Any]] = []
    decision = choose_action(question)
    trace.append({"stage": "agent_decision", "data": decision})
    calls = decision.get("tool_calls", [])
    if not calls:
        result = {
            "answer": "정책 근거를 검색하지 않아 답변을 생성하지 않았습니다.",
            "sources": [],
            "termination_reason": "required_tool_not_called",
            "trace": trace,
        }
    else:
        call = calls[0]["function"]
        results = execute_tool(call["name"], call.get("arguments", {}))
        trace.append({"stage": "tool_result", "data": results})
        answer = grounded_answer(question, results)
        sources = sorted({f"{item['source']}#{item['chunk_index']}" for item in results})
        result = {
            "answer": answer,
            "sources": sources,
            "termination_reason": "grounded_answer" if results else "no_evidence",
            "trace": trace,
        }

    cache_saved = cache.set(key, result, ttl_seconds=DEFAULT_TTL_SECONDS)
    return {
        **result,
        "cache_hit": False,
        "cache_saved": cache_saved,
        "cache_ttl_seconds": cache.ttl(key) if cache_saved else None,
    }


if __name__ == "__main__":
    try:
        redis_cache = JsonCache()
        prepare_documents(redis_cache)
        question = "호텔을 당일 취소하면 환불받을 수 있나요?"
        first = run_agent(question, redis_cache)
        second = run_agent(question, redis_cache)
        print("1회차:\n", json.dumps(first, ensure_ascii=False, indent=2))
        print("\n2회차:\n", json.dumps(second, ensure_ascii=False, indent=2))
    except (httpx.HTTPError, ValidationError, ValueError) as error:
        print(f"실행 실패: {error}")
        print("Ollama·PostgreSQL/pgvector와 DB Schema·embeddinggemma 준비 상태를 확인하세요.")

