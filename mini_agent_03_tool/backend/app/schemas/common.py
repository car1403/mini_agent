"""Mini Agent 전 단계에서 공유하는 Provider 이름과 기본 메시지 계약입니다.

Stage별 API Schema가 상속하며 Router, Service, Agent에서 공통으로 사용합니다.
"""

from typing import Literal

from pydantic import BaseModel, Field


ProviderName = Literal["mock", "gemini", "openai", "ollama"]


class MessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
