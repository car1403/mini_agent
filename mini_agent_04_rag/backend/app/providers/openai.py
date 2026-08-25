"""OpenAI Responses API를 공통 Provider 계약으로 변환하는 Adapter입니다."""

import json
from time import perf_counter
from typing import Any
from app.core.config import settings
from app.providers.models import ProviderResult, ProviderToolCall
from app.schemas import TravelPlan

class OpenAIProvider:
    name = "openai"
    def _client(self):
        if not settings.openai_api_key: raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        from openai import OpenAI
        return OpenAI(api_key=settings.openai_api_key)
    def generate(self, system_prompt: str, message: str) -> ProviderResult:
        started=perf_counter(); response=self._client().responses.create(model=settings.openai_model,instructions=system_prompt,input=message)
        return ProviderResult(self.name,settings.openai_model,response.output_text,round((perf_counter()-started)*1000))
    def generate_structured(self, system_prompt: str, message: str) -> ProviderResult:
        started=perf_counter(); response=self._client().responses.parse(model=settings.openai_model,instructions=system_prompt,input=message,text_format=TravelPlan)
        if response.output_parsed is None: raise RuntimeError("OpenAI가 구조화된 결과를 반환하지 않았습니다.")
        return ProviderResult(self.name,settings.openai_model,response.output_parsed.model_dump(),round((perf_counter()-started)*1000))
    def select_tool(self, message: str, tools: list[dict[str,Any]]) -> ProviderToolCall:
        definitions=[{"type":"function","name":t["name"],"description":t["description"],"parameters":t["input_schema"]} for t in tools]
        started=perf_counter(); response=self._client().responses.create(model=settings.openai_model,instructions="필요한 경우에만 여행 조회 Tool 하나를 선택하세요.",input=message,tools=definitions,tool_choice="auto")
        call=next((item for item in response.output if item.type=="function_call"),None)
        return ProviderToolCall(self.name,settings.openai_model,call.name if call else None,json.loads(call.arguments) if call else {},"OpenAI Tool Calling 결과",0.9 if call else 0.4,round((perf_counter()-started)*1000))
    def status(self)->dict[str,Any]: return {"provider":self.name,"configured":bool(settings.openai_api_key),"model":settings.openai_model,"environment":"cloud"}
