"""Gemini API를 공통 Provider 계약으로 변환하는 Adapter입니다."""

from time import perf_counter
from typing import Any
from app.core.config import settings
from app.providers.models import ProviderResult, ProviderToolCall
from app.schemas import TravelPlan

class GeminiProvider:
    name="gemini"
    def _client(self):
        if not settings.gemini_api_key: raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")
        if not settings.gemini_model: raise ValueError("GEMINI_MODEL이 설정되지 않았습니다.")
        from google import genai
        from google.genai import types
        return genai.Client(api_key=settings.gemini_api_key),types
    def generate(self,system_prompt:str,message:str)->ProviderResult:
        client,types=self._client();started=perf_counter();response=client.models.generate_content(model=settings.gemini_model,contents=message,config=types.GenerateContentConfig(system_instruction=system_prompt))
        return ProviderResult(self.name,settings.gemini_model,response.text or "",round((perf_counter()-started)*1000))
    def generate_structured(self,system_prompt:str,message:str)->ProviderResult:
        client,types=self._client();started=perf_counter();response=client.models.generate_content(model=settings.gemini_model,contents=message,config=types.GenerateContentConfig(system_instruction=system_prompt,response_mime_type="application/json",response_schema=TravelPlan));parsed=TravelPlan.model_validate_json(response.text or "{}")
        return ProviderResult(self.name,settings.gemini_model,parsed.model_dump(),round((perf_counter()-started)*1000))
    def select_tool(self,message:str,tools:list[dict[str,Any]])->ProviderToolCall:
        client,types=self._client();declarations=[types.FunctionDeclaration(name=t["name"],description=t["description"],parameters_json_schema=t["input_schema"]) for t in tools];started=perf_counter();response=client.models.generate_content(model=settings.gemini_model,contents=message,config=types.GenerateContentConfig(tools=[types.Tool(function_declarations=declarations)]));calls=response.function_calls or [];call=calls[0] if calls else None
        return ProviderToolCall(self.name,settings.gemini_model,call.name if call else None,dict(call.args) if call else {},"Gemini Function Calling 결과",0.9 if call else 0.4,round((perf_counter()-started)*1000))
    def status(self)->dict[str,Any]: return {"provider":self.name,"configured":bool(settings.gemini_api_key and settings.gemini_model),"model":settings.gemini_model or "(GEMINI_MODEL 미설정)","environment":"cloud"}
