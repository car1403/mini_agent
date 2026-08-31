"""음성 생성 유스케이스를 OpenAI Media Provider에 연결합니다.

Stage 01 TTS Endpoint에서 사용합니다.
"""

from app.providers.openai_media import create_speech

__all__ = ["create_speech"]
