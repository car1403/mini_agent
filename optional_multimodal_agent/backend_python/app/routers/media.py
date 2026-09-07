import asyncio
from typing import Literal
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from shared.config import MAX_BYTES
from shared.media_storage import save, resolve, mime

router = APIRouter(prefix="/api/media")

@router.post("/{kind}",status_code=201)
async def upload(kind: Literal["image","audio"], file: UploadFile = File(...)):
    try:
        content = await file.read(MAX_BYTES+1)
        media_id = await asyncio.to_thread(save,content,kind)
        return {"media_id":media_id}
    except ValueError as exc:
        raise HTTPException(400,str(exc)) from exc
    finally:
        await file.close()

@router.get("/{media_id}")
async def download(media_id: str):
    try:
        return FileResponse(resolve(media_id),media_type=mime(media_id))
    except (ValueError,FileNotFoundError) as exc:
        raise HTTPException(404,"파일을 찾을 수 없습니다.") from exc
