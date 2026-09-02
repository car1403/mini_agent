"""Single Agent Runtime과 API 입력 계약의 회귀 테스트입니다."""

import asyncio
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from pydantic import ValidationError


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents import runtime  # noqa: E402
from app.agents.models import AgentProfile  # noqa: E402
from app.schemas.agent import AgentRequest  # noqa: E402


PROFILE = AgentProfile(
    agent_id="test",
    name="Test Agent",
    goal="테스트 목표",
    description="테스트 Agent",
    example_question="질문",
    instructions="테스트 지침",
    allowed_tools=frozenset({"test_tool"}),
)


def response(*items, text="", response_id="response-1"):
    return SimpleNamespace(output=list(items), output_text=text, id=response_id)


def tool_call(name="test_tool", arguments=None):
    return SimpleNamespace(
        type="function_call",
        name=name,
        arguments=json.dumps(arguments or {"value": 1}),
        call_id="call-1",
    )


def install_runtime_mocks(monkeypatch) -> None:
    async def discover_tools(_allowed):
        return [{"name": "test_tool"}]

    monkeypatch.setattr(runtime, "discover_tools", discover_tools)
    monkeypatch.setattr(runtime, "create_client", lambda: object())


def test_last_response_after_final_tool_is_completed(monkeypatch) -> None:
    async def first_response(*_args):
        return response(tool_call())

    async def call_tool(*_args):
        return {"success": True}, {"tool": "test_tool"}

    async def next_response(*_args):
        return response(text="완료")

    monkeypatch.setattr(runtime, "MAX_AGENT_STEPS", 1)
    install_runtime_mocks(monkeypatch)
    monkeypatch.setattr(runtime, "first_response", first_response)
    monkeypatch.setattr(runtime, "call_tool", call_tool)
    monkeypatch.setattr(runtime, "next_response", next_response)

    result = asyncio.run(runtime.run_single_agent(PROFILE, "질문"))

    assert result["status"] == "completed"
    assert result["termination_reason"] == "model_finished"
    assert result["answer"] == "완료"


def test_pending_tool_after_limit_is_stopped(monkeypatch) -> None:
    async def model_response(*_args):
        return response(tool_call())

    async def call_tool(*_args):
        return {"success": True}, {"tool": "test_tool"}

    monkeypatch.setattr(runtime, "MAX_AGENT_STEPS", 1)
    install_runtime_mocks(monkeypatch)
    monkeypatch.setattr(runtime, "first_response", model_response)
    monkeypatch.setattr(runtime, "call_tool", call_tool)
    monkeypatch.setattr(runtime, "next_response", model_response)

    result = asyncio.run(runtime.run_single_agent(PROFILE, "질문"))

    assert result["status"] == "stopped"
    assert result["termination_reason"] == "max_steps_exceeded"


def test_blank_question_is_rejected() -> None:
    with pytest.raises(ValidationError):
        AgentRequest(agent_id="travel", question="   ")


def test_initial_model_error_is_sanitized(monkeypatch) -> None:
    async def first_response(*_args):
        raise RuntimeError("secret provider detail")

    install_runtime_mocks(monkeypatch)
    monkeypatch.setattr(runtime, "first_response", first_response)

    result = asyncio.run(runtime.run_single_agent(PROFILE, "질문"))

    assert result["termination_reason"] == "model_error"
    assert result["trace"][-1]["error_code"] == "MODEL_REQUEST_FAILED"
    assert "secret provider detail" not in str(result["trace"])


def test_invalid_json_tool_call_is_rejected(monkeypatch) -> None:
    invalid_call = SimpleNamespace(
        type="function_call",
        name="test_tool",
        arguments="not-json",
        call_id="call-1",
    )

    async def first_response(*_args):
        return response(invalid_call)

    install_runtime_mocks(monkeypatch)
    monkeypatch.setattr(runtime, "first_response", first_response)

    result = asyncio.run(runtime.run_single_agent(PROFILE, "질문"))

    assert result["termination_reason"] == "invalid_tool_call"
    assert result["trace"][-1]["error_code"] == "INVALID_TOOL_CALL"


def test_mcp_tool_error_is_sanitized(monkeypatch) -> None:
    async def first_response(*_args):
        return response(tool_call())

    async def call_tool(*_args):
        raise RuntimeError("secret mcp endpoint")

    install_runtime_mocks(monkeypatch)
    monkeypatch.setattr(runtime, "first_response", first_response)
    monkeypatch.setattr(runtime, "call_tool", call_tool)

    result = asyncio.run(runtime.run_single_agent(PROFILE, "질문"))

    assert result["termination_reason"] == "mcp_tool_error"
    assert result["trace"][-1]["error_code"] == "MCP_TOOL_EXECUTION_FAILED"
    assert "secret mcp endpoint" not in str(result["trace"])


def test_missing_required_tool_is_startup_error(monkeypatch) -> None:
    async def discover_tools(_allowed):
        return []

    monkeypatch.setattr(runtime, "discover_tools", discover_tools)

    result = asyncio.run(runtime.run_single_agent(PROFILE, "질문"))

    assert result["termination_reason"] == "startup_error"
    assert result["trace"][-1]["error_code"] == "AGENT_STARTUP_FAILED"
