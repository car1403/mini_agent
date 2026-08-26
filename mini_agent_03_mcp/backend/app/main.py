from fastapi import FastAPI, HTTPException

from .agent import run_agent
from .mcp_client import MCP_SERVER_URL, discover_resources, discover_tools, read_resource
from .schemas import McpRunRequest, McpRunResult


app = FastAPI(title="Mini Agent 03 MCP", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "stage": "mini_agent_03_mcp",
        "mcp_transport": "streamable-http",
        "mcp_server_url": MCP_SERVER_URL,
    }


@app.get("/api/mcp/status")
async def mcp_status():
    try:
        tools = await discover_tools()
        return {
            "status": "connected",
            "transport": "streamable-http",
            "server_url": MCP_SERVER_URL,
            "tool_count": len(tools),
        }
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"MCP Server 연결 실패 ({MCP_SERVER_URL}): {error}",
        ) from error


@app.get("/api/mcp/tools")
async def list_mcp_tools():
    try:
        return {"tools": await discover_tools()}
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"MCP Tool 발견 실패: {error}") from error


@app.get("/api/mcp/resources")
async def list_mcp_resources():
    try:
        return {"resources": await discover_resources()}
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"MCP Resource 발견 실패: {error}") from error


@app.get("/api/mcp/baggage-policy")
async def baggage_policy():
    try:
        content = await read_resource("travel://policy/baggage")
        return {"uri": "travel://policy/baggage", "content": content}
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"MCP Resource 읽기 실패: {error}") from error


@app.post("/api/mcp/run", response_model=McpRunResult)
async def run_mcp_agent(payload: McpRunRequest) -> McpRunResult:
    try:
        return await run_agent(payload.question)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"MCP Agent 실행 실패: {error}") from error
