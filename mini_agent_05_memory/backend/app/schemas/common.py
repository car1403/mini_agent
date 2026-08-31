"""COMMON 과정의 Pydantic API 계약입니다."""

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ProviderName = Literal["mock", "gemini", "openai", "ollama"]

class MessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)

