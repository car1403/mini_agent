from typing import TypeVar

from openai import OpenAI
from pydantic import BaseModel

from app.providers.base import ProviderResult, timed_call


T = TypeVar("T", bound=BaseModel)


class OpenAIProvider:
    name = "openai"

    def __init__(self, api_key: str, model: str) -> None:
        if not api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        self.model = model
        self.client = OpenAI(api_key=api_key)

    def generate(self, system_prompt: str, message: str) -> ProviderResult:
        response, latency = timed_call(
            lambda: self.client.responses.create(
                model=self.model,
                instructions=system_prompt,
                input=message,
            )
        )
        return ProviderResult(self.name, self.model, response.output_text, latency)

    def generate_structured(
        self,
        system_prompt: str,
        message: str,
        response_model: type[T],
    ) -> ProviderResult:
        response, latency = timed_call(
            lambda: self.client.responses.parse(
                model=self.model,
                instructions=system_prompt,
                input=message,
                text_format=response_model,
            )
        )
        parsed = response.output_parsed
        if parsed is None:
            raise RuntimeError("OpenAI가 구조화된 결과를 반환하지 않았습니다.")
        return ProviderResult(self.name, self.model, parsed.model_dump(), latency)
