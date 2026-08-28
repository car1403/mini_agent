"""Ollama가 stdio MCP RAG Tool을 선택하고 결과로 답변하는 최소 Agent입니다."""

import asyncio
import json
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
SERVER_PATH = Path(__file__).with_name("rag_stdio_server.py")


def ollama_chat(messages: list[dict], tools: list[dict] | None = None) -> dict:
    payload = {"model": OLLAMA_MODEL, "messages": messages, "stream": False}
    if tools:
        payload["tools"] = tools
    response = httpx.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json=payload,
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["message"]


def to_ollama_tool(tool) -> dict:
    raw = tool.model_dump(by_alias=True)
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": raw.get("inputSchema", {}),
        },
    }


def result_text(result) -> str:
    return "\n".join(
        content.text for content in result.content if hasattr(content, "text")
    )


async def run_agent(question: str) -> None:
    parameters = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_PATH)],
    )

    async with stdio_client(parameters) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            discovered = (await session.list_tools()).tools
            tools = [to_ollama_tool(tool) for tool in discovered]
            allowed_tools = {tool.name for tool in discovered}

            messages = [
                {
                    "role": "system",
                    "content": (
                        "여행 정책 질문은 반드시 search_knowledge_base Tool로 검색하세요. "
                        "Tool 결과만 근거로 한국어 답변을 작성하고 출처를 표시하세요."
                    ),
                },
                {"role": "user", "content": question},
            ]

            decision = ollama_chat(messages, tools)
            tool_calls = decision.get("tool_calls", [])
            if not tool_calls:
                print("Tool을 호출하지 않았습니다:", decision.get("content", ""))
                return

            call = tool_calls[0]["function"]
            if call["name"] not in allowed_tools:
                raise ValueError(f"허용되지 않은 Tool입니다: {call['name']}")

            arguments = call.get("arguments", {})
            result = await session.call_tool(call["name"], arguments)
            tool_output = result_text(result)

            messages.extend([
                decision,
                {
                    "role": "tool",
                    "tool_name": call["name"],
                    "content": tool_output,
                },
            ])
            final = ollama_chat(messages)

            print("질문:", question)
            print("발견한 MCP Tool:", sorted(allowed_tools))
            print("Tool Call:", json.dumps(call, ensure_ascii=False))
            print("Tool Result:", tool_output)
            print("최종 답변:", final.get("content", ""))


if __name__ == "__main__":
    asyncio.run(run_agent("호텔을 당일 취소하면 환불받을 수 있나요?"))
