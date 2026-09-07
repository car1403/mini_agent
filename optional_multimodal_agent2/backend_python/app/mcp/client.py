import json
from contextlib import asynccontextmanager
from typing import Any

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from app.core.config import settings


ALLOWED_TOOLS = frozenset({"get_weather", "search_hotels", "search_attractions"})


@asynccontextmanager
async def tools_session():
    async with streamable_http_client(settings.tools_mcp_url) as streams:
        read_stream, write_stream, _ = streams
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            yield session


async def discover_tools() -> list[dict[str, Any]]:
    async with tools_session() as session:
        tools = [
            tool for tool in (await session.list_tools()).tools
            if tool.name in ALLOWED_TOOLS
        ]
        return [
            {
                "name": tool.name,
                "description": tool.description or "",
                "input_schema": tool.inputSchema,
            }
            for tool in tools
        ]


async def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name not in ALLOWED_TOOLS:
        raise PermissionError("허용되지 않은 Tool입니다.")
    async with tools_session() as session:
        server_tools = {tool.name for tool in (await session.list_tools()).tools}
        if name not in server_tools:
            raise RuntimeError(f"MCP Server가 제공하지 않는 Tool입니다: {name}")
        result = await session.call_tool(name, arguments=arguments)
        text = "\n".join(
            content.text for content in result.content if hasattr(content, "text")
        )
        if result.isError:
            raise RuntimeError(text or "MCP Tool 실행에 실패했습니다.")
        return json.loads(text) if text else {}


async def connection_status() -> dict[str, Any]:
    tools = await discover_tools()
    return {
        "status": "connected",
        "server": "optional-multimodal-travel-tools",
        "transport": "streamable-http",
        "endpoint": settings.tools_mcp_url,
        "tools": [tool["name"] for tool in tools],
    }
