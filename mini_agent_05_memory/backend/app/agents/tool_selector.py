"""Tool 목록을 Provider에 전달하고 공통 Tool 선택 결과를 반환합니다."""

from app.agents.models import ToolDecision
from app.providers.registry import get_provider
from app.tools.registry import get_tool_definitions

def select_tool(provider:str,message:str)->ToolDecision:
    call = get_provider(provider).select_tool(message, get_tool_definitions())
    return ToolDecision(**call.__dict__)
