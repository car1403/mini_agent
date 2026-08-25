"""Tool 목록을 Provider에 전달하고 공통 Tool 선택 결과를 반환합니다."""

from datetime import date,timedelta
from typing import Any
from app.agents.mock_selector import select_mock_tool
from app.agents.models import ToolDecision
from app.providers.models import ProviderToolCall
from app.providers.registry import get_provider
from app.tools.registry import get_tool_definitions

def _mock_call(
    message: str,
    tool_names: list[str] | None = None,
    mock_arguments: dict[str, Any] | None = None,
) -> ProviderToolCall:
    if tool_names == ["search_knowledge_base"]:
        return ProviderToolCall(
            "mock", "deterministic-rag-mock", "search_knowledge_base",
            mock_arguments or {"query": message, "mode": "hybrid", "top_k": 3},
            "내부 문서 근거가 필요한 질문", 0.95, 0,
        )
    decision=select_mock_tool(message);today=date.today();city=next((c for c in ("서울","부산","제주","강릉") if c in message),"부산");arguments={}
    if decision["tool_name"]=="get_weather": arguments={"city":city,"target_date":today.isoformat()}
    elif decision["tool_name"]=="search_hotels": arguments={"city":city,"check_in":today.isoformat(),"check_out":(today+timedelta(days=2)).isoformat(),"guests":2}
    elif decision["tool_name"]=="search_attractions": arguments={"city":city,"category":"all"}
    return ProviderToolCall("mock","deterministic-travel-mock",decision["tool_name"],arguments,decision["reason"],decision["confidence"],0)

def select_tool(
    provider: str,
    message: str,
    tool_names: list[str] | None = None,
    mock_arguments: dict[str, Any] | None = None,
) -> ToolDecision:
    tool_definitions = get_tool_definitions(tool_names)
    call=(
        _mock_call(message, tool_names, mock_arguments)
        if provider=="mock"
        else get_provider(provider).select_tool(message,tool_definitions)
    )
    decision=ToolDecision(**call.__dict__)
    definitions={tool["name"]:tool for tool in tool_definitions}
    schema=definitions.get(decision.tool_name or "",{}).get("input_schema",{})
    missing=[name for name in schema.get("required",[]) if name not in decision.arguments]
    decision.missing_arguments=missing
    decision.needs_clarification=bool(missing)
    decision.follow_up_question=(
        f"Tool 실행 전에 다음 정보를 알려주세요: {', '.join(missing)}" if missing else ""
    )
    return decision
