import re
from fastapi import APIRouter, HTTPException, Request, Header, Query
from fastapi.responses import StreamingResponse
from backend.app.schemas import RunRequest, AdditionalInput
from backend.app.services.run_service import submit, follow_up
from backend.app.stores.run_store import get_run, change, TERMINAL
from backend.app.stores.event_store import event_stream
from backend.app.mcp.client import tools_session, call

router = APIRouter(prefix="/api/runs")

@router.post("",status_code=202)
async def start(payload: RunRequest, request: Request):
    try:
        return await submit(request.app.state.redis,payload.model_dump())
    except (ValueError,FileNotFoundError) as exc:
        raise HTTPException(400,str(exc)) from exc

@router.get("/{run_id}")
async def status(run_id: str, request: Request):
    run = await get_run(request.app.state.redis,run_id)
    if run is None:
        raise HTTPException(404,"실행이 없거나 보관 기간이 지났습니다.")
    return run

@router.post("/{run_id}/input",status_code=202)
async def additional(run_id: str, payload: AdditionalInput, request: Request):
    try:
        return await follow_up(request.app.state.redis,run_id,payload)
    except FileNotFoundError as exc:
        raise HTTPException(404,str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409,str(exc)) from exc

@router.post("/{run_id}/speech")
async def retry_speech(run_id: str, request: Request):
    run = await status(run_id,request)
    result = run.get("result") or {}
    if run["status"] not in TERMINAL or not result.get("speech_text"):
        raise HTTPException(409,"음성을 생성할 최종 텍스트가 없습니다.")
    try:
        async with tools_session() as session:
            audio = await call(session,"synthesize_speech",{"text":result["speech_text"]},{"synthesize_speech"})
        result["audio_id"] = audio["audio_id"]
        result.pop("audio_error",None)
        await change(request.app.state.redis,run_id,expected=TERMINAL,result=result,step="audio_ready",message="음성이 준비되었습니다.")
        return result
    except Exception as exc:
        raise HTTPException(502,"음성 생성에 실패했습니다. MCP Server 설정을 확인하세요.") from exc

@router.get("/{run_id}/events")
async def events(run_id: str, request: Request, after: str = Query("0-0"),
                 last_event_id: str | None = Header(None)):
    await status(run_id,request)
    cursor = last_event_id or after
    if not re.fullmatch(r"\d+-\d+",cursor):
        raise HTTPException(400,"잘못된 이벤트 ID입니다.")
    return StreamingResponse(event_stream(request.app.state.redis,run_id,cursor),
                             media_type="text/event-stream",
                             headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no"})
