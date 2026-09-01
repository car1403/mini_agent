"""Streamlit과 HTTP Memory MCP Server를 연결하는 Backend API입니다."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.mcp_client import MEMORY_MCP_URL, call_memory_tool, discover_tools


mcp_router = APIRouter(prefix="/api/mcp", tags=["05 · Memory"])


class McpMemorySaveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    key: str = Field(min_length=1, max_length=100)
    value: str = Field(min_length=1, max_length=1000)


class McpRelevantRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: str = Field(min_length=1, max_length=2000)


async def safe_call(name: str, arguments: dict | None = None) -> dict:
    try:
        return await call_memory_tool(name, arguments)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Memory MCP 호출 실패: {error}") from error


@mcp_router.get("/status")
async def mcp_status() -> dict:
    try:
        tools = await discover_tools()
        return {
            "status": "connected",
            "transport": "streamable-http",
            "endpoint": MEMORY_MCP_URL,
            "storage": "postgres",
            "tool_count": len(tools),
        }
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Memory MCP 연결 실패: {error}") from error


@mcp_router.get("/tools")
async def list_mcp_tools() -> dict:
    try:
        return {"tools": await discover_tools()}
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Memory MCP Tool 발견 실패: {error}") from error


@mcp_router.get("/memories")
async def list_mcp_memories() -> dict:
    return await safe_call("list_memories")


@mcp_router.post("/memories")
async def save_mcp_memory(payload: McpMemorySaveRequest) -> dict:
    return await safe_call("save_memory", payload.model_dump())


@mcp_router.delete("/memories/{memory_id}")
async def delete_mcp_memory(memory_id: str) -> dict:
    return await safe_call("delete_memory", {"memory_id": memory_id})


@mcp_router.post("/relevant")
async def relevant_mcp_memories(payload: McpRelevantRequest) -> dict:
    return await safe_call("find_relevant_memories", payload.model_dump())


@mcp_router.get("/export")
async def export_mcp_memories() -> dict:
    return await safe_call("export_memories")
