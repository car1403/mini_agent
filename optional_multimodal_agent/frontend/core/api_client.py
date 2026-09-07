import httpx
from frontend.core.config import BACKEND_URL

def request(method, path, **kwargs):
    response = httpx.request(method,BACKEND_URL+path,timeout=180,**kwargs)
    if response.is_error:
        try:
            detail = response.json().get("detail","요청 실패")
        except ValueError:
            detail = "Backend 응답을 확인할 수 없습니다."
        raise RuntimeError(str(detail))
    return response.json()

def upload(file, kind):
    return request("POST",f"/api/media/{kind}",files={"file":(file.name,file.getvalue(),file.type)})["media_id"]

def get_audio(media_id):
    response = httpx.get(f"{BACKEND_URL}/api/media/{media_id}",timeout=30)
    response.raise_for_status()
    return response.content
