from typing import Any

from pydantic import BaseModel, Field


class McpRunRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)


class ToolExecutionTrace(BaseModel):
    round: int
    server: str
    tool: str
    public_tool: str
    arguments: dict[str, Any]
    is_error: bool
    result: str


class McpRunResult(BaseModel):
    question: str
    model: str
    available_tools: list[str]
    llm_calls: int
    trace: list[ToolExecutionTrace]
    answer: str
