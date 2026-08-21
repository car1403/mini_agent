"""Mini Agent 02의 Prompt·Pydantic·Structured Output API 계약입니다.

`routers.stage_02_router`와 Provider의 구조화 출력 기능에서 사용합니다.
"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import MessageRequest, ProviderName


class PromptPreviewRequest(BaseModel):
    role: str = Field(min_length=1, max_length=500)
    instruction: str = Field(min_length=1, max_length=1000)
    context: str = Field(min_length=1, max_length=1000)
    constraint: str = Field(min_length=1, max_length=1000)


class PromptPreviewResult(PromptPreviewRequest):
    prompt: str


class TravelPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    destination: str = Field(min_length=1)
    summary: str = Field(min_length=1, max_length=500)
    recommended_days: int = Field(ge=1, le=30)
    activities: list[str] = Field(min_length=1, max_length=10)
    cautions: list[str] = Field(default_factory=list, max_length=10)


class TravelValidationRequest(BaseModel):
    payload: dict[str, Any]


class TravelValidationResult(BaseModel):
    valid: bool
    data: TravelPlan | None = None
    errors: list[dict[str, Any]] = Field(default_factory=list)


class StructuredTravelRequest(MessageRequest):
    provider: ProviderName | None = None
    system_prompt: str = Field(default="당신은 여행 계획 도우미입니다. TravelPlan Schema에 맞춰 작성하세요.", max_length=2000)


class StructuredTravelResult(BaseModel):
    provider: ProviderName
    model: str
    content: TravelPlan
    latency_ms: int


class StructuredCompareRequest(MessageRequest):
    providers: list[ProviderName] = Field(default_factory=lambda: ["mock"], min_length=1, max_length=4)
    system_prompt: str = Field(default="당신은 여행 계획 도우미입니다. TravelPlan Schema에 맞춰 작성하세요.", max_length=2000)


class StructuredComparisonItem(BaseModel):
    provider: ProviderName
    status: Literal["success", "error"]
    model: str = ""
    content: TravelPlan | None = None
    latency_ms: int = 0
    error: str | None = None


class StructuredCompareResult(BaseModel):
    request_count: int
    results: list[StructuredComparisonItem]
