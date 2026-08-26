import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")
MCP_SERVER_URL = os.getenv("TRAVEL_MCP_URL", "http://127.0.0.1:8010/mcp")


@asynccontextmanager
async def travel_session():
    async with streamable_http_client(MCP_SERVER_URL) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            yield session


def result_text(result) -> str:
    return "\n".join(
        content.text for content in result.content if hasattr(content, "text")
    )


async def discover_tools() -> list[dict[str, Any]]:
    async with travel_session() as session:
        response = await session.list_tools()
        tools = []
        for tool in response.tools:
            raw = tool.model_dump(by_alias=True)
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": raw.get("inputSchema", {}),
            })
        return tools


async def discover_resources() -> list[dict[str, Any]]:
    async with travel_session() as session:
        response = await session.list_resources()
        return [
            {
                "name": resource.name,
                "uri": str(resource.uri),
                "description": resource.description,
            }
            for resource in response.resources
        ]


async def read_resource(uri: str) -> str:
    async with travel_session() as session:
        response = await session.read_resource(uri)
        return "\n".join(
            content.text for content in response.contents if hasattr(content, "text")
        )
