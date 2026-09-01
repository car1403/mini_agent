"""Ollama HTTP API를 공통 Provider 계약으로 변환하는 Adapter입니다."""

from time import perf_counter
from typing import Any
from app.core.config import settings
from app.providers.models import ProviderResult,ProviderToolCall
from app.schemas import TravelPlan

class OllamaProvider:
    name="ollama"
    def _chat(self,system_prompt:str,message:str,format_:dict|None=None,tools:list[dict]|None=None)->dict:
        import httpx
        payload={"model":settings.ollama_model,"messages":[{"role":"system","content":system_prompt},{"role":"user","content":message}],"stream":False}
        if format_ is not None: payload["format"]=format_
        if tools is not None: payload["tools"]=tools
        response=httpx.post(f"{settings.ollama_base_url}/api/chat",json=payload,timeout=settings.request_timeout_seconds);response.raise_for_status();return response.json()
    def generate(self,system_prompt:str,message:str)->ProviderResult:
        started=perf_counter();body=self._chat(system_prompt,message);return ProviderResult(self.name,settings.ollama_model,body["message"]["content"],round((perf_counter()-started)*1000))
    def generate_structured(self,system_prompt:str,message:str)->ProviderResult:
        started=perf_counter();body=self._chat(system_prompt,message,TravelPlan.model_json_schema());parsed=TravelPlan.model_validate_json(body["message"]["content"]);return ProviderResult(self.name,settings.ollama_model,parsed.model_dump(),round((perf_counter()-started)*1000))
    def select_tool(self,message:str,tools:list[dict[str,Any]])->ProviderToolCall:
        definitions=[{"type":"function","function":{"name":t["name"],"description":t["description"],"parameters":t["input_schema"]}} for t in tools];started=perf_counter();body=self._chat("필요한 경우에만 여행 조회 Tool 하나를 선택하세요.",message,tools=definitions);calls=body.get("message",{}).get("tool_calls",[]);call=calls[0].get("function",{}) if calls else {}
        return ProviderToolCall(self.name,settings.ollama_model,call.get("name"),call.get("arguments",{}),"Ollama Tool Calling 결과",0.85 if call else 0.4,round((perf_counter()-started)*1000))
    def status(self)->dict[str,Any]: return {"provider":self.name,"configured":True,"model":settings.ollama_model,"base_url":settings.ollama_base_url,"environment":"local-docker"}
