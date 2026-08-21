"""Mini Agent 01의 LLM 생성·Provider 비교·분류·Media API 계약입니다.

`routers.stage_01_router`, Media Service와 기본 생성 기능에서 사용합니다.
"""

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import MessageRequest, ProviderName


class DecisionResult(BaseModel):
    route: str
    reason: str
    confidence: float = Field(ge=0, le=1)


class ConceptCompareResult(BaseModel):
    message: str
    workflow: DecisionResult
    semantic_router: DecisionResult
    note: str


class TravelIntentResult(BaseModel):
    intent: str
    reason: str
    confidence: float = Field(ge=0, le=1)
    missing_information: list[str] = Field(default_factory=list)
    next_action: Literal["continue", "ask_user"]
    follow_up_question: str = ""


class GenerateRequest(MessageRequest):
    provider: ProviderName | None = None
    system_prompt: str = Field(default="당신은 초보자를 돕는 친절한 여행 도우미입니다.", max_length=2000)


class GenerateResult(BaseModel):
    provider: ProviderName
    model: str
    content: str
    latency_ms: int


class ProviderCompareRequest(MessageRequest):
    providers: list[ProviderName] = Field(default_factory=lambda: ["mock"], min_length=1, max_length=4)
    system_prompt: str = Field(default="당신은 초보자를 돕는 친절한 여행 도우미입니다.", max_length=2000)


class ProviderComparisonItem(BaseModel):
    provider: ProviderName
    status: Literal["success", "error"]
    model: str = ""
    content: str = ""
    latency_ms: int = 0
    error: str | None = None


class ProviderCompareResult(BaseModel):
    request_count: int
    results: list[ProviderComparisonItem]


class TravelImageAnalysis(BaseModel):
    scene_type: Literal["landmark", "food", "transport", "accommodation", "document", "other"]
    summary: str = Field(min_length=1, max_length=500)
    visible_text: list[str] = Field(default_factory=list, max_length=10)
    travel_tips: list[str] = Field(default_factory=list, max_length=10)
    safety_notes: list[str] = Field(default_factory=list, max_length=10)


class TtsRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    voice: Literal["alloy", "ash", "ballad", "coral", "echo", "fable", "nova", "onyx", "sage", "shimmer", "verse", "marin", "cedar"] | None = None
    instructions: str = Field(default="한국어로 또렷하고 따뜻한 여행 가이드처럼 말하세요.", max_length=500)
