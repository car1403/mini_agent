"""Agent의 정규화된 Tool 선택 결과 모델입니다."""

from dataclasses import dataclass, field
from typing import Any

@dataclass
class ToolDecision:
    provider:str
    model:str
    tool_name:str|None
    arguments:dict[str,Any]
    reason:str
    confidence:float
    latency_ms:int
    missing_arguments:list[str]=field(default_factory=list)
    needs_clarification:bool=False
    follow_up_question:str=""
