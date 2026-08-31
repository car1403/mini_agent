"""Tool 목록을 Provider에 전달하고 공통 Tool 선택 결과를 반환합니다."""

from datetime import date,timedelta
from app.agents.mock_selector import select_mock_tool
from app.agents.models import ToolDecision
from app.providers.models import ProviderToolCall
from app.providers.registry import get_provider
from app.tools.registry import get_tool_definitions

def _mock_call(message:str)->ProviderToolCall:
    decision=select_mock_tool(message);today=date.today();city=next((c for c in ("서울","부산","제주","강릉") if c in message),"부산");arguments={}
    if decision["tool_name"]=="get_weather": arguments={"city":city,"target_date":today.isoformat()}
    elif decision["tool_name"]=="search_hotels": arguments={"city":city,"check_in":today.isoformat(),"check_out":(today+timedelta(days=2)).isoformat(),"guests":2}
    elif decision["tool_name"]=="search_attractions": arguments={"city":city,"category":"all"}
    return ProviderToolCall("mock","deterministic-travel-mock",decision["tool_name"],arguments,decision["reason"],decision["confidence"],0)

def select_tool(provider:str,message:str)->ToolDecision:
    call=_mock_call(message) if provider=="mock" else get_provider(provider).select_tool(message,get_tool_definitions())
    return ToolDecision(**call.__dict__)
