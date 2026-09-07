from dataclasses import asdict, dataclass
from time import perf_counter
from typing import Any, Callable, Protocol, TypeVar

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


@dataclass
class ProviderResult:
    provider: str
    model: str
    content: Any
    latency_ms: int
    fallback_used: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ToolSelectionResult:
    provider: str
    model: str
    tool_name: str | None
    arguments: dict[str, Any]
    latency_ms: int
    fallback_used: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class LlmProvider(Protocol):
    name: str
    model: str

    def generate(self, system_prompt: str, message: str) -> ProviderResult: ...

    def generate_structured(
        self,
        system_prompt: str,
        message: str,
        response_model: type[T],
    ) -> ProviderResult: ...

    def select_tool(
        self,
        system_prompt: str,
        message: str,
        tools: list[dict[str, Any]],
    ) -> ToolSelectionResult: ...


def timed_call(call: Callable[[], Any]) -> tuple[Any, int]:
    started = perf_counter()
    value = call()
    return value, round((perf_counter() - started) * 1000)
