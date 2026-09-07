from typing import Any, TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel

from app.providers.base import ProviderResult, ToolSelectionResult, timed_call


T = TypeVar("T", bound=BaseModel)


class GeminiProvider:
    name = "gemini"

    def __init__(self, api_key: str, model: str) -> None:
        if not api_key:
            raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")
        if not model:
            raise ValueError("GEMINI_MODEL이 설정되지 않았습니다.")
        self.model = model
        self.client = genai.Client(api_key=api_key)

    def generate(self, system_prompt: str, message: str) -> ProviderResult:
        response, latency = timed_call(
            lambda: self.client.models.generate_content(
                model=self.model,
                contents=message,
                config=types.GenerateContentConfig(system_instruction=system_prompt),
            )
        )
        return ProviderResult(self.name, self.model, response.text or "", latency)

    def generate_structured(
        self,
        system_prompt: str,
        message: str,
        response_model: type[T],
    ) -> ProviderResult:
        response, latency = timed_call(
            lambda: self.client.models.generate_content(
                model=self.model,
                contents=message,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=response_model,
                ),
            )
        )
        parsed = response_model.model_validate_json(response.text or "{}")
        return ProviderResult(self.name, self.model, parsed.model_dump(), latency)

    def select_tool(
        self,
        system_prompt: str,
        message: str,
        tools: list[dict[str, Any]],
    ) -> ToolSelectionResult:
        declarations = [
            types.FunctionDeclaration(
                name=tool["name"],
                description=tool["description"],
                parameters_json_schema=tool["input_schema"],
            )
            for tool in tools
        ]
        response, latency = timed_call(
            lambda: self.client.models.generate_content(
                model=self.model,
                contents=message,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    tools=[types.Tool(function_declarations=declarations)],
                ),
            )
        )
        calls = response.function_calls or []
        call = calls[0] if calls else None
        return ToolSelectionResult(
            self.name,
            self.model,
            call.name if call else None,
            dict(call.args) if call else {},
            latency,
        )
