"""Mini Agent 03의 Tool arguments·선택·실행·단일 Agent Cycle API 계약입니다.

`routers.stage_03_router`, Agent, Provider Tool Calling과 Tool 구현에서 사용합니다.
"""

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.common import MessageRequest, ProviderName


class CurrentWeatherArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    city: str = Field(min_length=1)


class WeatherForecastArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    city: str = Field(min_length=1)
    target_date: date

    @model_validator(mode="after")
    def validate_forecast_date(self) -> "WeatherForecastArgs":
        today = date.today()
        if self.target_date < today:
            raise ValueError("예보 날짜는 오늘 이후여야 합니다.")
        if (self.target_date - today).days > 16:
            raise ValueError("예보 날짜는 오늘부터 16일 이내여야 합니다.")
        return self


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
    tool_choice: Literal["auto", "none", "required"] = "auto"


class ToolSelectionResult(BaseModel):
    provider: ProviderName
    model: str
    tool_name: str | None = None
    arguments: dict[str, Any] = Field(default_factory=dict)
    reason: str
    confidence: float = Field(ge=0, le=1)
    latency_ms: int = 0
    missing_arguments: list[str] = Field(default_factory=list)
    needs_clarification: bool = False
    follow_up_question: str = ""
    raw_tool_call: dict[str, Any] | None = None


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
    trace: list[dict[str, Any]] = Field(default_factory=list)
