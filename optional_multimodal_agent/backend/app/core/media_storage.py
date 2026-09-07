"""Backend가 업로드 파일을 저장하고 미디어 ID로 조회합니다."""
import mimetypes
import re
from pathlib import Path
from uuid import uuid4

from backend.app.core.config import ROOT, env
from backend.app.core.media_validation import validate


def _storage_directory() -> Path:
    configured = Path(env("MEDIA_STORAGE_DIR", "storage"))
    return configured if configured.is_absolute() else ROOT / configured


STORAGE = _storage_directory()


def save(content: bytes, kind: str) -> str:
    suffix = validate(content, kind)
    folder = STORAGE / "uploads"
    folder.mkdir(parents=True, exist_ok=True)
    media_id = uuid4().hex + suffix
    (folder / media_id).write_bytes(content)
    return media_id


def resolve(media_id: str) -> Path:
    if not re.fullmatch(r"[0-9a-f]{32}\.(jpg|png|webp|wav|mp3)", media_id):
        raise ValueError("올바른 파일 ID가 아닙니다.")
    folder = "generated_audio" if media_id.endswith(".mp3") else "uploads"
    path = STORAGE / folder / media_id
    if not path.is_file():
        raise FileNotFoundError("파일이 없거나 보관 기간이 지났습니다.")
    return path


def mime(media_id: str) -> str:
    return mimetypes.guess_type(media_id)[0] or "application/octet-stream"
