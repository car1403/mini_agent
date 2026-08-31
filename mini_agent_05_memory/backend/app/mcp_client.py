"""Mini Agent 05 Backend가 HTTP Memory MCP Server를 호출하는 Client입니다."""

import json
import os
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")
MEMORY_MCP_URL = os.getenv("MEMORY_MCP_URL", "http://127.0.0.1:8012/mcp")


async def open_session(stack: AsyncExitStack) -> ClientSession:
    read_stream, write_stream, _ = await stack.enter_async_context(
        streamable_http_client(MEMORY_MCP_URL)
    )
    session = await stack.enter_async_context(ClientSession(read_stream, write_stream))
    await session.initialize()
    return session


def result_data(result) -> dict[str, Any]:
    if result.isError:
        message = "\n".join(
            content.text for content in result.content if hasattr(content, "text")
        )
        raise RuntimeError(message or "MCP Tool 실행에 실패했습니다.")
    if result.structuredContent:
        return result.structuredContent
    text = "\n".join(
        content.text for content in result.content if hasattr(content, "text")
    )
    return json.loads(text)


async def discover_tools() -> list[dict[str, Any]]:
    async with AsyncExitStack() as stack:
        session = await open_session(stack)
        response = await session.list_tools()
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.model_dump(by_alias=True).get("inputSchema", {}),
            }
            for tool in response.tools
        ]


async def call_memory_tool(name: str, arguments: dict[str, Any] | None = None) -> dict:
    async with AsyncExitStack() as stack:
        session = await open_session(stack)
        result = await session.call_tool(name, arguments or {})
    # MCP Session을 먼저 정상 종료한 뒤 Tool 오류를 평범한 RuntimeError로 변환합니다.
    return result_data(result)
