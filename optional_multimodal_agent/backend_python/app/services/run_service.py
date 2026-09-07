from shared.media_storage import resolve
from backend_python.app.stores.run_store import create_run, get_run

def validate_files(request):
    if resolve(request["image_id"]).suffix not in {".jpg",".png",".webp"}:
        raise ValueError("이미지 파일을 선택하세요.")
    if request.get("audio_id") and resolve(request["audio_id"]).suffix != ".wav":
        raise ValueError("녹음 파일은 WAV 형식이어야 합니다.")

async def submit(redis, request):
    validate_files(request)
    return await create_run(redis,request)

async def follow_up(redis, run_id, additional):
    previous = await get_run(redis,run_id)
    if previous is None:
        raise FileNotFoundError("실행이 없거나 보관 기간이 지났습니다.")
    if previous["status"] not in {"completed","needs_input","failed"}:
        raise ValueError("현재 실행이 끝난 뒤 추가 질문을 보내세요.")
    request = dict(previous["request"])
    request.update(question=additional.question,audio_id=None)
    request["previous_context"] = {"question":previous["request"]["question"],
                                   "answer":(previous.get("result") or {}).get("answer","")}
    if additional.image_id:
        request["image_id"] = additional.image_id
    validate_files(request)
    return await create_run(redis,request,parent_id=run_id)
