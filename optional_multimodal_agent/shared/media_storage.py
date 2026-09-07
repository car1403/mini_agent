"""UUID 파일 ID만 허용합니다. MCP는 임의의 로컬 경로를 읽지 않습니다."""
import re
import mimetypes
from uuid import uuid4
from shared.config import ROOT
from shared.media_validation import validate

STORAGE = ROOT / "storage"

def save(content: bytes, kind: str) -> str:
    suffix = ".mp3" if kind == "speech" else validate(content, kind)
    folder = STORAGE / ("generated_audio" if kind == "speech" else "uploads")
    folder.mkdir(parents=True, exist_ok=True)
    media_id = uuid4().hex + suffix
    (folder / media_id).write_bytes(content)
    return media_id

def resolve(media_id: str):
    if not re.fullmatch(r"[0-9a-f]{32}\.(jpg|png|webp|wav|mp3)", media_id):
        raise ValueError("올바른 파일 ID가 아닙니다.")
    folder = "generated_audio" if media_id.endswith(".mp3") else "uploads"
    path = STORAGE / folder / media_id
    if not path.is_file():
        raise FileNotFoundError("파일이 없거나 보관 기간이 지났습니다.")
    return path

def mime(media_id: str) -> str:
    return mimetypes.guess_type(media_id)[0] or "application/octet-stream"
