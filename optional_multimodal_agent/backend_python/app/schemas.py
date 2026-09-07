from typing import Literal
from pydantic import BaseModel, Field

class RunRequest(BaseModel):
    agent: Literal["product","facility"]
    image_id: str
    question: str = Field(default="",max_length=2000)
    audio_id: str | None = None
    speak: bool = True

class AdditionalInput(BaseModel):
    question: str = Field(min_length=1,max_length=2000)
    image_id: str | None = None

class AgentAnswer(BaseModel):
    status: Literal["completed","needs_input"]
    answer: str
    speech_text: str = Field(max_length=2000)
