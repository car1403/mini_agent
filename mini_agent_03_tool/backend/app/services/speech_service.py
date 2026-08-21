"""음성 생성 유스케이스를 OpenAI Media Provider에 연결합니다.

Stage 01 Router의 `/api/media/tts` Endpoint가 MP3 음성을 생성할 때 사용합니다.
"""

from app.providers.openai_media import openai_media_provider


def create_speech(text: str, voice: str | None, instructions: str) -> bytes:
    return openai_media_provider.create_speech(text, voice, instructions)
