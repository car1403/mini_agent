"""이미지 입력을 안전하게 검증하고 Media Provider에 분석을 요청합니다.

Stage 01 Router의 `/api/media/image-analysis` Endpoint가 이 Service를 사용합니다.
"""

from app.core.config import settings
from app.providers.openai_media import openai_media_provider
from app.schemas.stage_01 import TravelImageAnalysis


ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


def _matches_signature(content_type: str, content: bytes) -> bool:
    checks = {
        "image/jpeg": content.startswith(b"\xff\xd8\xff"),
        "image/png": content.startswith(b"\x89PNG\r\n\x1a\n"),
        "image/gif": content.startswith((b"GIF87a", b"GIF89a")),
        "image/webp": content.startswith(b"RIFF") and content[8:12] == b"WEBP",
    }
    return checks.get(content_type, False)


def validate_image(content_type: str | None, content: bytes) -> None:
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError("JPEG, PNG, WEBP, GIF 이미지만 업로드할 수 있습니다.")
    if not content or not _matches_signature(content_type, content):
        raise ValueError("파일 내용과 이미지 형식이 일치하지 않습니다.")
    if len(content) > settings.max_image_size_mb * 1024 * 1024:
        raise ValueError(f"이미지는 {settings.max_image_size_mb}MB 이하여야 합니다.")


def analyze_image(content_type: str, content: bytes, question: str) -> TravelImageAnalysis:
    validate_image(content_type, content)
    return openai_media_provider.analyze_image(content_type, content, question)
