from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


ProviderName = Literal["mock", "openai", "gemini", "ollama"]


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[Any] = Field(default_factory=list)


class ApiResponse(BaseModel):
    success: bool
    data: Any | None = None
    error: ErrorDetail | None = None
    trace_id: str


class TextRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ProviderGenerateRequest(TextRequest):
    provider: ProviderName | None = None
    system_prompt: str = Field(
        default="당신은 초보자를 돕는 친절한 여행 상담 도우미입니다.",
        max_length=2000,
    )


class TravelPlan(BaseModel):
    destination: str
    summary: str
    recommended_days: int = Field(ge=1, le=30)
    activities: list[str] = Field(min_length=1, max_length=10)
    cautions: list[str] = Field(default_factory=list, max_length=10)


class TravelImageAnalysis(BaseModel):
    scene_type: Literal[
        "landmark", "food", "transport", "accommodation", "document", "other"
    ]
    summary: str = Field(min_length=1, max_length=500)
    visible_text: list[str] = Field(default_factory=list, max_length=10)
    travel_tips: list[str] = Field(default_factory=list, max_length=10)
    safety_notes: list[str] = Field(default_factory=list, max_length=10)


class TtsRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    voice: Literal[
        "alloy", "ash", "ballad", "coral", "echo", "fable", "nova",
        "onyx", "sage", "shimmer", "verse", "marin", "cedar"
    ] | None = None
    instructions: str = Field(
        default="Speak clearly in a warm travel-guide tone.",
        max_length=500,
    )


class TravelExtractRequest(TextRequest):
    reference_date: date = date(2026, 7, 27)


class ToolSelectRequest(TextRequest):
    provider: ProviderName | None = None


class ToolRunRequest(BaseModel):
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    limit: int = Field(default=3, ge=1, le=10)


class MemoryCreateRequest(BaseModel):
    key: str = Field(min_length=1, max_length=100)
    value: str = Field(min_length=1, max_length=500)


class AgentRunRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=2000)
    provider: ProviderName | None = None
    destination: str | None = None
    start_date: date | None = None
    nights: int | None = Field(default=None, ge=1, le=30)
    adults: int | None = Field(default=None, ge=1, le=20)
    budget: int | None = Field(default=None, gt=0)


class AgentDecisionRequest(BaseModel):
    actor: str = Field(default="demo-user", min_length=1, max_length=100)
    note: str = Field(default="", max_length=500)


class WeatherArgs(BaseModel):
    city: str = Field(min_length=1)
    target_date: date


class HotelArgs(BaseModel):
    city: str = Field(min_length=1)
    check_in: date
    check_out: date
    guests: int = Field(ge=1, le=10)

    @model_validator(mode="after")
    def validate_dates(self) -> "HotelArgs":
        if self.check_out <= self.check_in:
            raise ValueError("체크아웃은 체크인 이후여야 합니다.")
        return self


class AttractionArgs(BaseModel):
    city: str = Field(min_length=1)
    category: Literal["nature", "culture", "food", "all"] = "all"


class LlmCallTrace(BaseModel):
    node: str
    provider: str
    model: str
    operation: str
    latency_ms: int = Field(ge=0)
    success: bool
    retry_count: int = Field(default=0, ge=0)
    error_code: str | None = None


class EvaluationRunRequest(BaseModel):
    providers: list[ProviderName] = Field(min_length=1, max_length=3)
    scenario_set: Literal["tool_selection"] = "tool_selection"
