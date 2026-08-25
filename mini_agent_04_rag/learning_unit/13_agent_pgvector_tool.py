"""Agent가 필요할 때 pgvector 검색 Tool을 호출하는 최소 Loop입니다.

RAG_AGENT_PROVIDER=mock은 결정적인 교육용 판단을, ollama는 실제 Tool Calling을 사용합니다.
"""

import json
import os
from typing import Any

import httpx

from _pgvector_store import OLLAMA_BASE_URL, similarity_search
from _pgvector_store import upsert_text


COLLECTION = "rag_agent_lesson"
PROVIDER = os.getenv("RAG_AGENT_PROVIDER", "mock")
CHAT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
TOOL = {
    "type": "function",
    "function": {
        "name": "search_knowledge_base",
        "description": "호텔 정책처럼 내부 문서의 근거가 필요한 질문을 의미 검색합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "독립적으로 이해되는 검색 질문"},
                "top_k": {"type": "integer", "minimum": 1, "maximum": 5},
            },
            "required": ["query"],
        },
    },
}


def search_knowledge_base(query: str, top_k: int = 3) -> list[dict[str, Any]]:
    top_k = max(1, min(top_k, 5))
    return similarity_search(query, collection=COLLECTION, top_k=top_k)


def prepare_documents() -> None:
    documents = [
        "반려동물 동반 객실은 1박당 3만 원이 추가됩니다.",
        "체크인 당일 취소에는 숙박 요금 전액이 부과됩니다.",
        "교육용 국내선의 위탁 수하물은 15kg까지 허용합니다.",
    ]
    for index, content in enumerate(documents):
        upsert_text(
            collection=COLLECTION,
            title="Agent용 여행 정책",
            content=content,
            source="agent-policy.md",
            chunk_index=index,
            metadata={"lesson": "agent-tool"},
        )


def ollama_chat(messages: list[dict[str, Any]], *, tools: list[dict] | None = None) -> dict:
    payload: dict[str, Any] = {"model": CHAT_MODEL, "messages": messages, "stream": False}
    if tools:
        payload["tools"] = tools
    response = httpx.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, timeout=120)
    response.raise_for_status()
    return response.json()["message"]


def run_mock_agent(question: str) -> dict[str, Any]:
    tool_call = {"name": "search_knowledge_base", "arguments": {"query": question, "top_k": 3}}
    results = search_knowledge_base(**tool_call["arguments"])
    if not results:
        answer = "등록된 정책 문서에서 근거를 찾지 못했습니다."
    else:
        best = results[0]
        answer = f"{best['content']} (출처: {best['source']})"
    return {"tool_call": tool_call, "tool_result": results, "answer": answer}


def run_ollama_agent(question: str) -> dict[str, Any]:
    messages = [
        {"role": "system", "content": "내부 정책 질문은 Tool로 검색하고 검색 결과만 근거로 답하세요. 출처를 표시하세요."},
        {"role": "user", "content": question},
    ]
    decision = ollama_chat(messages, tools=[TOOL])
    calls = decision.get("tool_calls", [])
    if not calls:
        return {"tool_call": None, "tool_result": [], "answer": decision.get("content", "")}

    call = calls[0]["function"]
    if call["name"] != "search_knowledge_base":
        raise ValueError(f"허용되지 않은 Tool입니다: {call['name']}")
    arguments = call.get("arguments", {})
    results = search_knowledge_base(arguments["query"], arguments.get("top_k", 3))
    messages.extend([
        decision,
        {"role": "tool", "tool_name": call["name"], "content": json.dumps(results, ensure_ascii=False)},
    ])
    final = ollama_chat(messages)
    return {"tool_call": call, "tool_result": results, "answer": final.get("content", "")}


if __name__ == "__main__":
    prepare_documents()
    question = "강아지와 호텔에 묵으면 추가 비용이 있나요?"
    result = run_ollama_agent(question) if PROVIDER == "ollama" else run_mock_agent(question)
    print("질문:", question)
    print("Tool Call:", result["tool_call"])
    print("Tool Result:", result["tool_result"])
    print("최종 답변:", result["answer"])
