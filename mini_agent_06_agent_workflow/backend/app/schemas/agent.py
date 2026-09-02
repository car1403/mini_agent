from typing import Any

from pydantic import BaseModel, Field, field_validator


class AgentRequest(BaseModel):
    agent_id: str
    question: str = Field(min_length=1, max_length=500)

    @field_validator("question", mode="before")
    @classmethod
    def normalize_question(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class AgentSummary(BaseModel):
    agent_id: str
    name: str
    goal: str
    description: str
    example_question: str
    allowed_tools: list[str]


class AgentResponse(BaseModel):
    agent_id: str
    agent_name: str
    goal: str
    question: str
    model: str
    status: str
    termination_reason: str | None
    llm_calls: int
    tool_calls: int
    trace: list[dict[str, Any]]
    answer: str | None = None
