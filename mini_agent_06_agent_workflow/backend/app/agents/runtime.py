import json
import logging
from typing import Any

from app.agents.models import AgentProfile
from app.core.config import MAX_AGENT_STEPS, OPENAI_MODEL
from app.mcp.client import call_tool, discover_tools
from app.providers.openai import create_client, first_response, next_response


logger = logging.getLogger(__name__)


async def run_single_agent(profile: AgentProfile, question: str) -> dict[str, Any]:
    """Agent Profile 하나를 독립적으로 실행하는 공통 순수 Python Agent Loop입니다."""
    state: dict[str, Any] = {
        "agent_id": profile.agent_id,
        "agent_name": profile.name,
        "goal": profile.goal,
        "question": question,
        "model": OPENAI_MODEL,
        "status": "running",
        "termination_reason": None,
        "llm_calls": 0,
        "tool_calls": 0,
        "trace": [],
        "answer": None,
    }
    try:
        tools = await discover_tools(profile.allowed_tools)
        discovered_names = {tool["name"] for tool in tools}
        missing = profile.allowed_tools - discovered_names
        if missing:
            raise RuntimeError(f"MCP Server에 필요한 Tool이 없습니다: {sorted(missing)}")
        state["trace"].append(
            {"owner": "runtime", "stage": "agent_started", "agent": profile.agent_id}
        )
        state["trace"].append(
            {"owner": "mcp", "stage": "tools_discovered", "tools": sorted(discovered_names)}
        )
        client = create_client()
    except Exception as error:
        logger.exception("Agent 초기화 실패: agent_id=%s", profile.agent_id)
        state["status"] = "failed"
        state["termination_reason"] = "startup_error"
        state["trace"].append(
            {"owner": "runtime", "stage": "startup_error", "error_code": "AGENT_STARTUP_FAILED"}
        )
        return state

    try:
        response = await first_response(client, question, profile.instructions, tools)
        state["llm_calls"] += 1
    except Exception:
        logger.exception("최초 Model 호출 실패: agent_id=%s", profile.agent_id)
        state["status"] = "failed"
        state["termination_reason"] = "model_error"
        state["trace"].append(
            {"step": 0, "owner": "runtime", "stage": "model_error", "error_code": "MODEL_REQUEST_FAILED"}
        )
        return state

    for step in range(1, MAX_AGENT_STEPS + 1):
        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            state["status"] = "completed"
            state["termination_reason"] = "model_finished"
            state["answer"] = response.output_text
            state["trace"].append(
                {"step": step, "owner": "ai_agent", "stage": "model_final_answer", "text": response.output_text}
            )
            return state

        outputs = []
        for call in calls:
            try:
                arguments = json.loads(call.arguments)
                if not isinstance(arguments, dict):
                    raise ValueError("Tool arguments는 JSON Object여야 합니다.")
                state["trace"].append(
                    {"step": step, "owner": "ai_agent", "stage": "model_selected_tool", "tool": call.name}
                )
                result, trace = await call_tool(call.name, arguments, profile.allowed_tools)
            except (AttributeError, json.JSONDecodeError, TypeError, ValueError) as error:
                logger.warning(
                    "잘못된 Tool Call: agent_id=%s tool=%s error=%s",
                    profile.agent_id,
                    getattr(call, "name", None),
                    error,
                )
                state["status"] = "failed"
                state["termination_reason"] = "invalid_tool_call"
                state["trace"].append(
                    {
                        "step": step,
                        "owner": "runtime",
                        "stage": "invalid_tool_call",
                        "tool": getattr(call, "name", None),
                        "error_code": "INVALID_TOOL_CALL",
                    }
                )
                return state
            except Exception:
                logger.exception(
                    "MCP Tool 실행 실패: agent_id=%s tool=%s",
                    profile.agent_id,
                    getattr(call, "name", None),
                )
                state["status"] = "failed"
                state["termination_reason"] = "mcp_tool_error"
                state["trace"].append(
                    {
                        "step": step,
                        "owner": "mcp",
                        "stage": "mcp_tool_error",
                        "tool": getattr(call, "name", None),
                        "error_code": "MCP_TOOL_EXECUTION_FAILED",
                    }
                )
                return state
            outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": json.dumps(result, ensure_ascii=False),
                }
            )
            state["tool_calls"] += 1
            state["trace"].append({"step": step, "owner": "mcp", "stage": "tool_executed", **trace})

        try:
            response = await next_response(client, response.id, outputs, profile.instructions, tools)
            state["llm_calls"] += 1
        except Exception:
            logger.exception("후속 Model 호출 실패: agent_id=%s step=%s", profile.agent_id, step)
            state["status"] = "failed"
            state["termination_reason"] = "model_error"
            state["trace"].append(
                {
                    "step": step,
                    "owner": "runtime",
                    "stage": "model_error",
                    "error_code": "MODEL_REQUEST_FAILED",
                }
            )
            return state

    # 마지막 Tool Result 뒤의 응답도 확인합니다. 최종 답변이면 반복 제한 초과가 아니라
    # 정상 완료이며, 추가 Tool Call이 남아 있을 때만 안전하게 중단합니다.
    calls = [item for item in response.output if item.type == "function_call"]
    if not calls:
        state["status"] = "completed"
        state["termination_reason"] = "model_finished"
        state["answer"] = response.output_text
        state["trace"].append(
            {
                "step": MAX_AGENT_STEPS + 1,
                "owner": "ai_agent",
                "stage": "model_final_answer",
                "text": response.output_text,
            }
        )
        return state

    state["status"] = "stopped"
    state["termination_reason"] = "max_steps_exceeded"
    state["trace"].append(
        {
            "owner": "runtime",
            "stage": "max_steps_exceeded",
            "pending_tools": [call.name for call in calls],
        }
    )
    return state
