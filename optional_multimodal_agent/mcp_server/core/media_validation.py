"""MCP Tool이 읽은 이미지와 음성의 실제 내용을 다시 검사합니다."""
import io
import wave

from PIL import Image

from mcp_server.core.config import MAX_BYTES


def validate(content: bytes, kind: str) -> None:
    if not content or len(content) > MAX_BYTES:
        raise ValueError("파일이 비어 있거나 크기 제한을 초과했습니다.")
    if kind == "image":
        try:
            with Image.open(io.BytesIO(content)) as image:
                if image.width * image.height > 20_000_000:
                    raise ValueError("이미지는 2천만 픽셀 이하로 올려 주세요.")
                image.verify()
                fmt = image.format
        except Exception as exc:
            raise ValueError("올바른 이미지 파일이 아닙니다.") from exc
        if fmt not in {"JPEG", "PNG", "WEBP"}:
            raise ValueError("JPEG, PNG, WEBP 이미지만 지원합니다.")
        return
    if kind == "audio":
        try:
            with wave.open(io.BytesIO(content)) as audio:
                if audio.getnframes() / audio.getframerate() > 120:
                    raise ValueError("녹음은 120초 이하로 해 주세요.")
        except (wave.Error, EOFError) as exc:
            raise ValueError("WAV 녹음 파일을 사용하세요.") from exc
        return
    raise ValueError("지원하지 않는 미디어 종류입니다.")
