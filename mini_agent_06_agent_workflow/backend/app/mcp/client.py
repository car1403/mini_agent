import json
from contextlib import asynccontextmanager
from typing import Any

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from app.core.config import TOOLS_MCP_URL


@asynccontextmanager
async def tools_session():
    async with streamable_http_client(TOOLS_MCP_URL) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            yield session


def to_openai_tool(tool: Any) -> dict[str, Any]:
    raw = tool.model_dump(by_alias=True)
    return {
        "type": "function",
        "name": tool.name,
        "description": tool.description or "",
        "parameters": raw.get("inputSchema", {}),
    }


async def discover_tools(allowed_tools: frozenset[str] | None = None) -> list[dict[str, Any]]:
    async with tools_session() as session:
        tools = (await session.list_tools()).tools
        if allowed_tools is not None:
            tools = [tool for tool in tools if tool.name in allowed_tools]
        return [to_openai_tool(tool) for tool in tools]


async def call_tool(
    name: str,
    arguments: dict[str, Any],
    allowed_tools: frozenset[str],
) -> tuple[Any, dict[str, Any]]:
    if name not in allowed_tools:
        raise ValueError(f"이 Agent에 허용되지 않은 Tool입니다: {name}")
    async with tools_session() as session:
        server_tools = {tool.name for tool in (await session.list_tools()).tools}
        if name not in server_tools:
            raise ValueError(f"MCP Server가 제공하지 않는 Tool입니다: {name}")
        result = await session.call_tool(name, arguments=arguments)
        text = "\n".join(content.text for content in result.content if hasattr(content, "text"))
        if result.isError:
            raise RuntimeError(text or "MCP Tool 실행에 실패했습니다.")
        value = json.loads(text) if text else None
        return value, {
            "server": "business-tools",
            "transport": "streamable-http",
            "endpoint": TOOLS_MCP_URL,
            "tool": name,
            "arguments": arguments,
            "result": value,
        }


async def connection_status() -> dict[str, Any]:
    tools = await discover_tools()
    return {
        "status": "connected",
        "server": "business-tools",
        "transport": "streamable-http",
        "endpoint": TOOLS_MCP_URL,
        "tool_count": len(tools),
        "tools": [tool["name"] for tool in tools],
    }
