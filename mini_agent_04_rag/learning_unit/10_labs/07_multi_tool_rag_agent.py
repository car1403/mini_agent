"""재질문, 여러 pgvector 검색 Tool, 종료 조건을 갖는 Multi-Tool RAG Agent."""

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _pgvector_store import OLLAMA_BASE_URL, delete_collection, similarity_search, upsert_text
from _redis_cache import JsonCache, cache_key


MAX_STEPS = 4
CHAT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
COLLECTIONS = {
    "hotel": "rag_multi_tool_hotel",
    "flight": "rag_multi_tool_flight",
    "attraction": "rag_multi_tool_attraction",
}
TOOL_TO_TOPIC = {
    "search_hotel_policy": "hotel",
    "search_flight_policy": "flight",
    "search_attraction_guide": "attraction",
}


class SearchArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=2, max_length=300)
    top_k: int = Field(default=2, ge=1, le=3)


@dataclass
class AgentState:
    requested_topics: set[str] = field(default_factory=set)
    trace: list[dict[str, Any]] = field(default_factory=list)
    step_count: int = 0
    termination_reason: str | None = None


def prepare_documents(cache: JsonCache) -> None:
    documents = {
        "hotel": [
            "체크인 3일 전까지 취소하면 전액 환불합니다.",
            "체크인 당일 취소에는 숙박 요금 전액이 부과됩니다.",
        ],
        "flight": [
            "교육용 국내선의 위탁 수하물은 15kg까지 허용합니다.",
            "국내선 탑승 수속은 출발 40분 전에 마감합니다.",
        ],
        "attraction": [
            "바다 박물관은 매주 화요일에 휴관합니다.",
            "전망대의 운영 시간은 오전 9시부터 오후 8시까지입니다.",
        ],
    }
    for topic, chunks in documents.items():
        collection = COLLECTIONS[topic]
        delete_collection(collection)
        for index, content in enumerate(chunks):
            upsert_text(
                collection=collection,
                title=f"{topic} 지식 저장소",
                content=content,
                source=f"{topic}-knowledge.md",
                chunk_index=index,
                metadata={"topic": topic, "status": "active"},
            )
    cache.delete_namespace("multi-tool-agent")


def detect_topics(message: str) -> set[str]:
    keywords = {
        "hotel": ("호텔", "숙소", "체크인", "환불", "취소"),
        "flight": ("항공", "비행기", "수하물", "탑승"),
        "attraction": ("관광", "박물관", "전망대", "명소"),
    }
    return {topic for topic, words in keywords.items() if any(word in message for word in words)}


def execute_search_tool(name: str, raw_arguments: dict[str, Any]) -> list[dict[str, Any]]:
    """Agent는 DB 이름이나 SQL이 아닌 허용된 검색 Tool만 호출합니다."""
    if name not in TOOL_TO_TOPIC:
        raise ValueError(f"허용되지 않은 Tool입니다: {name}")
    arguments = SearchArguments.model_validate(raw_arguments)
    topic = TOOL_TO_TOPIC[name]
    return similarity_search(
        arguments.query,
        collection=COLLECTIONS[topic],
        top_k=arguments.top_k,
        metadata_filter={"topic": topic, "status": "active"},
    )


def generate_grounded_answer(question: str, results: dict[str, list[dict[str, Any]]]) -> str:
    context_lines = []
    for topic, items in results.items():
        for item in items:
            context_lines.append(f"[{topic}:{item['source']}#{item['chunk_index']}] {item['content']}")
    if not context_lines:
        return "선택한 지식 저장소에서 근거를 찾지 못했습니다."
    response = httpx.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json={
            "model": CHAT_MODEL,
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": "Context만 사용해 답하고 각 문장에 출처를 표시하세요. 근거가 없으면 모른다고 답하세요.",
                },
                {"role": "user", "content": f"질문: {question}\n\nContext:\n" + "\n".join(context_lines)},
            ],
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


def run_cycle(message: str, state: AgentState, cache: JsonCache) -> dict[str, Any]:
    if state.step_count >= MAX_STEPS:
        state.termination_reason = "max_steps_exceeded"
        return {"type": "stop", "message": "최대 실행 횟수를 초과했습니다.", "state": state}

    state.step_count += 1
    state.requested_topics.update(detect_topics(message))
    state.trace.append({"stage": "agent_state", "topics": sorted(state.requested_topics)})
    if not state.requested_topics:
        state.termination_reason = "clarification_required"
        question = "호텔, 항공, 관광 중 어떤 정보가 필요한가요?"
        state.trace.append({"stage": "clarification", "question": question})
        return {"type": "clarification", "message": question, "state": state}

    topics = sorted(state.requested_topics)
    key = cache_key("multi-tool-agent", {"message": message, "topics": topics})
    cached = cache.get(key)
    if cached is not None:
        state.termination_reason = "cache_hit"
        return {
            **cached,
            "termination_reason": state.termination_reason,
            "cache_hit": True,
            "state": state,
        }

    results: dict[str, list[dict[str, Any]]] = {}
    for topic in topics:
        if state.step_count >= MAX_STEPS:
            state.termination_reason = "max_steps_exceeded"
            return {"type": "stop", "message": "최대 실행 횟수를 초과했습니다.", "state": state}
        state.step_count += 1
        tool_name = next(name for name, mapped_topic in TOOL_TO_TOPIC.items() if mapped_topic == topic)
        tool_call = {"name": tool_name, "arguments": {"query": message, "top_k": 2}}
        state.trace.append({"stage": "tool_call", "data": tool_call})
        results[topic] = execute_search_tool(tool_name, tool_call["arguments"])
        state.trace.append({"stage": "tool_result", "tool": tool_name, "data": results[topic]})

    answer = generate_grounded_answer(message, results)
    state.termination_reason = "grounded_answer"
    value = {
        "type": "answer",
        "answer": answer,
        "sources": sorted({item["source"] for items in results.values() for item in items}),
        "termination_reason": state.termination_reason,
        "trace": state.trace,
    }
    saved = cache.set(key, value)
    return {**value, "cache_hit": False, "cache_saved": saved, "state": state}


if __name__ == "__main__":
    redis_cache = JsonCache()
    prepare_documents(redis_cache)
    agent_state = AgentState()

    first = run_cycle("여행 규정을 알려 주세요.", agent_state, redis_cache)
    print("1차 Cycle:", first["type"], first["message"])

    second = run_cycle("호텔 당일 취소와 항공 수하물 규정이 궁금합니다.", agent_state, redis_cache)
    printable = {key: value for key, value in second.items() if key != "state"}
    print("\n2차 Cycle:\n", json.dumps(printable, ensure_ascii=False, indent=2))
