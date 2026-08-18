from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


ProviderName = Literal["mock", "gemini", "openai", "ollama"]


class MessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


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


class WeatherArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    city: str = Field(min_length=1)
    target_date: date


class HotelArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

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
    model_config = ConfigDict(extra="forbid")

    city: str = Field(min_length=1)
    category: Literal["nature", "culture", "food", "all"] = "all"


class ToolSelectRequest(MessageRequest):
    provider: ProviderName | None = None


class ToolSelectionResult(BaseModel):
    provider: ProviderName
    model: str
    tool_name: str | None = None
    arguments: dict[str, Any] = Field(default_factory=dict)
    reason: str
    confidence: float = Field(ge=0, le=1)
    latency_ms: int = 0


class ToolCompareRequest(MessageRequest):
    providers: list[ProviderName] = Field(default_factory=lambda: ["mock"], min_length=1, max_length=4)


class ToolComparisonItem(BaseModel):
    provider: ProviderName
    status: Literal["success", "error"]
    decision: ToolSelectionResult | None = None
    error: str | None = None


class ToolCompareResult(BaseModel):
    request_count: int
    results: list[ToolComparisonItem]


class ToolRunRequest(BaseModel):
    tool_name: str = Field(min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolRunResult(BaseModel):
    success: bool
    tool_name: str
    data: Any | None = None
    error: dict[str, Any] | None = None


class ToolCompleteRequest(ToolSelectRequest):
    pass


class ToolCompleteResult(BaseModel):
    provider: ProviderName
    question: str
    decision: ToolSelectionResult
    tool_result: ToolRunResult | None = None
    final_answer: str
