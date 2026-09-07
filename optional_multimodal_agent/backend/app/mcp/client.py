"""백업 프로젝트의 Streamable HTTP 연결 방식을 사용합니다."""
import json
from contextlib import asynccontextmanager
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from backend.app.core.config import MCP_URL

@asynccontextmanager
async def tools_session():
    async with streamable_http_client(MCP_URL) as (read,write,_):
        async with ClientSession(read,write) as session:
            await session.initialize()
            yield session

async def discover(session, allowed: set[str]) -> list[dict]:
    return [{"type":"function","function":{"name":t.name,"description":t.description or "",
             "parameters":t.inputSchema}} for t in (await session.list_tools()).tools if t.name in allowed]

async def call(session, name: str, arguments: dict, allowed: set[str]) -> dict:
    if name not in allowed:
        raise PermissionError("허용되지 않은 Tool입니다.")
    result = await session.call_tool(name,arguments=arguments)
    if result.isError:
        raise RuntimeError("MCP Tool 실행에 실패했습니다: " + name)
    if result.structuredContent is not None:
        return result.structuredContent
    text = "\n".join(c.text for c in result.content if hasattr(c,"text"))
    return json.loads(text) if text else {}
