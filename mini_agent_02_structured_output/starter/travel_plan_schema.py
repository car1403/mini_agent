"""TODO 2: 주석의 조건에 맞춰 TravelPlan Schema를 완성하세요."""

from pydantic import BaseModel, ConfigDict, Field


class TravelPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    destination: str = Field(min_length=1)
    summary: str = Field(min_length=1, max_length=500)
    # TODO: 1일 이상 30일 이하
    recommended_days: int
    # TODO: 최소 1개, 최대 10개
    activities: list[str]
    cautions: list[str] = Field(default_factory=list, max_length=10)
