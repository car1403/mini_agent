from typing import TypeVar

import httpx
from pydantic import BaseModel

from app.providers.base import ProviderResult, ToolSelectionResult, timed_call


T = TypeVar("T", bound=BaseModel)


class OllamaProvider:
    name = "ollama"

    def __init__(self, base_url: str, model: str, timeout: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def _chat(self, system_prompt: str, message: str, format_: dict | None = None) -> dict:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            "stream": False,
        }
        if format_ is not None:
            payload["format"] = format_
        response = httpx.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def select_tool(
        self,
        system_prompt: str,
        message: str,
        tools: list[dict],
    ) -> ToolSelectionResult:
        payload_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"],
                },
            }
            for tool in tools
        ]
        body, latency = timed_call(
            lambda: self._chat_with_tools(system_prompt, message, payload_tools)
        )
        calls = body.get("message", {}).get("tool_calls", [])
        call = calls[0].get("function", {}) if calls else {}
        return ToolSelectionResult(
            self.name,
            self.model,
            call.get("name"),
            call.get("arguments", {}),
            latency,
        )

    def _chat_with_tools(
        self,
        system_prompt: str,
        message: str,
        tools: list[dict],
    ) -> dict:
        response = httpx.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message},
                ],
                "tools": tools,
                "stream": False,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def generate(self, system_prompt: str, message: str) -> ProviderResult:
        body, latency = timed_call(lambda: self._chat(system_prompt, message))
        return ProviderResult(
            self.name, self.model, body["message"]["content"], latency
        )

    def generate_structured(
        self,
        system_prompt: str,
        message: str,
        response_model: type[T],
    ) -> ProviderResult:
        body, latency = timed_call(
            lambda: self._chat(
                system_prompt,
                message,
                response_model.model_json_schema(),
            )
        )
        parsed = response_model.model_validate_json(body["message"]["content"])
        return ProviderResult(self.name, self.model, parsed.model_dump(), latency)
