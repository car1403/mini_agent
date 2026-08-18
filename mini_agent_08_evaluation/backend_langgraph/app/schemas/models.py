from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


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
    provider: Literal["mock", "openai", "gemini", "ollama"] | None = None
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


class TravelExtractRequest(TextRequest):
    reference_date: date = date(2026, 7, 27)


class ToolSelectRequest(TextRequest):
    pass


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
    destination: str | None = None
    start_date: date | None = None
    nights: int | None = Field(default=None, ge=1, le=30)
    adults: int | None = Field(default=None, ge=1, le=20)
    budget: int | None = Field(default=None, gt=0)


class AgentDecisionRequest(BaseModel):
    actor: str = Field(default="demo-user", min_length=1, max_length=100)
    note: str = Field(default="", max_length=500)


class EvaluationScenario(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=2000)
    expected_tool: str | None = Field(default=None, max_length=100)
    expected_status: Literal["completed", "needs_input", "blocked"]


class EvaluationRunRequest(BaseModel):
    scenarios: list[EvaluationScenario] = Field(default_factory=list, max_length=50)


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
