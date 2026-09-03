from fastapi import APIRouter, HTTPException

from app.mcp.client import connection_status
from app.schemas.agent import AgentRequest, AgentResponse, ApprovalDecision
from app.services.agent_service import audit_for_run, decide, find_run, start
from app.progress.store import read_progress


router = APIRouter(prefix="/api/agents", tags=["Human Approval and Safety"])

@router.get("/runs/{run_id}/progress")
def progress(run_id: str):
    return read_progress(run_id)


@router.get("/mcp-status")
async def mcp_status():
    try:
        return await connection_status()
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"MCP Server 연결 실패: {error}") from error


@router.post("/runs", response_model=AgentResponse)
async def create_run(request: AgentRequest) -> AgentResponse:
    try:
        return await start(request)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Agent 실행 실패: {error}") from error


@router.get("/runs/{run_id}")
def get_run(run_id: str):
    result = find_run(run_id)
    if result is None:
        raise HTTPException(status_code=404, detail="실행을 찾을 수 없습니다.")
    return result


@router.post("/runs/{run_id}/decision", response_model=AgentResponse)
async def decision(run_id: str, request: ApprovalDecision) -> AgentResponse:
    try:
        return await decide(run_id, request)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"승인 후 실행 실패: {error}") from error


@router.get("/runs/{run_id}/audit")
def audit(run_id: str):
    return {"run_id": run_id, "events": audit_for_run(run_id)}
