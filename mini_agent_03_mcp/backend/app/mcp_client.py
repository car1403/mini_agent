import os
import sys
from contextlib import AsyncExitStack, asynccontextmanager
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

MCP_SERVERS: dict[str, dict[str, Any]] = {
    "travel": {
        "transport": "streamable-http",
        "url": os.getenv("TRAVEL_MCP_URL", "http://127.0.0.1:8010/mcp"),
    },
    "policy": {
        "transport": "stdio",
        "command": sys.executable,
        "args": [str(PROJECT_ROOT / "mcp_server" / "policy_stdio_server.py")],
    },
}


async def open_session(
    stack: AsyncExitStack,
    config: dict[str, Any],
) -> ClientSession:
    """설정에 맞는 Transport를 열고 초기화된 MCP Session을 반환합니다."""
    transport = config["transport"]

    if transport == "streamable-http":
        read_stream, write_stream, _ = await stack.enter_async_context(
            streamable_http_client(config["url"])
        )
    elif transport == "stdio":
        parameters = StdioServerParameters(
            command=config["command"],
            args=config.get("args", []),
            env=config.get("env"),
        )
        read_stream, write_stream = await stack.enter_async_context(
            stdio_client(parameters)
        )
    else:
        raise ValueError(f"지원하지 않는 MCP Transport입니다: {transport}")

    session = await stack.enter_async_context(
        ClientSession(read_stream, write_stream)
    )
    await session.initialize()
    return session


@asynccontextmanager
async def mcp_sessions():
    """등록된 모든 MCP Server를 열고 이름별 Session을 제공합니다."""
    async with AsyncExitStack() as stack:
        sessions: dict[str, ClientSession] = {}
        for server_name, config in MCP_SERVERS.items():
            sessions[server_name] = await open_session(stack, config)
        yield sessions


def result_text(result) -> str:
    return "\n".join(
        content.text for content in result.content if hasattr(content, "text")
    )


async def discover_tools() -> list[dict[str, Any]]:
    async with mcp_sessions() as sessions:
        tools: list[dict[str, Any]] = []
        for server_name, session in sessions.items():
            response = await session.list_tools()
            for tool in response.tools:
                raw = tool.model_dump(by_alias=True)
                tools.append({
                    "server": server_name,
                    "name": tool.name,
                    "public_name": f"{server_name}__{tool.name}",
                    "description": tool.description,
                    "input_schema": raw.get("inputSchema", {}),
                })
        return tools


async def discover_resources() -> list[dict[str, Any]]:
    async with mcp_sessions() as sessions:
        resources: list[dict[str, Any]] = []
        for server_name, session in sessions.items():
            response = await session.list_resources()
            resources.extend(
                {
                    "server": server_name,
                    "name": resource.name,
                    "uri": str(resource.uri),
                    "description": resource.description,
                }
                for resource in response.resources
            )
        return resources


async def read_resource(server_name: str, uri: str) -> str:
    async with mcp_sessions() as sessions:
        response = await sessions[server_name].read_resource(uri)
        return "\n".join(
            content.text for content in response.contents if hasattr(content, "text")
        )
